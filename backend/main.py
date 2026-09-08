import os
import shutil
import uuid
import zipfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google import genai

from rag.loader import load_codebase
from rag.chunker import chunk_documents
from rag.embeddings import create_embeddings
from rag.vector_store import VectorStore

from mcp_client import (
    get_mcp_tools_async,
    call_mcp_tool_async,
)


# --------------------------------------------------
# Environment
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# FastAPI
# --------------------------------------------------

app = FastAPI(
    title="DevPilot API"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://devpilot-fawn.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Configuration
# --------------------------------------------------

UPLOAD_ROOT = (
    Path(__file__).parent / "uploaded_projects"
)

UPLOAD_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)


# --------------------------------------------------
# Current uploaded project
# --------------------------------------------------

current_project_path = None

current_documents = []

current_chunks = []

vector_store = None


# --------------------------------------------------
# Gemini client
# --------------------------------------------------

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# --------------------------------------------------
# Load and chunk project
# --------------------------------------------------

def load_project_data(project_path: str):

    documents = load_codebase(
        project_path
    )

    chunks = chunk_documents(
        documents
    )

    return documents, chunks


# --------------------------------------------------
# Health endpoint
# --------------------------------------------------

@app.get("/api/health")
def health():

    return {
        "status": "ok",
        "project_loaded": (
            current_project_path is not None
        ),
    }


# --------------------------------------------------
# Upload ZIP
# --------------------------------------------------

@app.post("/api/upload")
async def upload_project(
    file: UploadFile = File(...)
):

    global current_project_path
    global current_documents
    global current_chunks
    global vector_store

    # ----------------------------------------------
    # Validate file
    # ----------------------------------------------

    if not file.filename:

        return {
            "success": False,
            "error": "No file selected.",
        }


    if not file.filename.lower().endswith(".zip"):

        return {
            "success": False,
            "error": "Please upload a ZIP file.",
        }


    project_id = str(
        uuid.uuid4()
    )

    zip_path = (
        UPLOAD_ROOT /
        f"{project_id}.zip"
    )

    extract_path = (
        UPLOAD_ROOT /
        project_id
    )


    try:

        # ------------------------------------------
        # Save ZIP
        # ------------------------------------------

        with open(
            zip_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )


        # ------------------------------------------
        # Extract ZIP safely
        # ------------------------------------------

        extract_path.mkdir(
            parents=True,
            exist_ok=True
        )


        with zipfile.ZipFile(
            zip_path,
            "r"
        ) as zip_ref:

            for member in zip_ref.infolist():

                target_path = (
                    extract_path /
                    member.filename
                )

                # Prevent ZIP path traversal
                if not target_path.resolve().is_relative_to(
                    extract_path.resolve()
                ):

                    raise ValueError(
                        "Unsafe ZIP file detected."
                    )


            zip_ref.extractall(
                extract_path
            )


        # ------------------------------------------
        # Detect project root
        # ------------------------------------------

        children = list(
            extract_path.iterdir()
        )


        if (
            len(children) == 1
            and children[0].is_dir()
        ):

            project_root = children[0]

        else:

            project_root = extract_path


        # ------------------------------------------
        # Load source files
        # ------------------------------------------

        documents, chunks = load_project_data(
            str(project_root)
        )


        if not documents:

            raise ValueError(
                "No supported source files were found "
                "in the uploaded project."
            )


        # ------------------------------------------
        # Store project in memory
        # ------------------------------------------

        current_project_path = (
            str(project_root)
        )

        current_documents = documents

        current_chunks = chunks

        # Important:
        # Do not generate embeddings during upload.
        #
        # This keeps ZIP upload fast.

        vector_store = None


        return {

            "success": True,

            "filename": file.filename,

            "files": len(documents),

            "chunks": len(chunks),

            "message": (
                "Project uploaded successfully."
            ),
        }


    except Exception as e:

        if extract_path.exists():

            shutil.rmtree(
                extract_path,
                ignore_errors=True
            )


        return {

            "success": False,

            "error": str(e),
        }


    finally:

        if zip_path.exists():

            zip_path.unlink(
                missing_ok=True
            )


# --------------------------------------------------
# Create RAG vector store
# --------------------------------------------------

def ensure_vector_store():

    global vector_store


    # Already created
    if vector_store is not None:

        return vector_store


    # No chunks
    if not current_chunks:

        return None


    print(
        f"Creating embeddings for "
        f"{len(current_chunks)} chunks..."
    )


    embedded_chunks = create_embeddings(
        current_chunks
    )


    if not embedded_chunks:

        return None


    dimension = len(
        embedded_chunks[0]["embedding"]
    )


    store = VectorStore(
        dimension
    )


    store.add(
        embedded_chunks
    )


    vector_store = store


    print(
        "RAG index ready."
    )


    return vector_store


# --------------------------------------------------
# Chat endpoint
# --------------------------------------------------

@app.post("/api/chat")
async def chat(request: dict):

    # ----------------------------------------------
    # Check project
    # ----------------------------------------------

    if current_project_path is None:

        return {

            "answer": (
                "Please upload a project ZIP "
                "before asking questions."
            ),

            "sources": [],
        }


    # ----------------------------------------------
    # Get question
    # ----------------------------------------------

    question = request.get(
        "message",
        ""
    ).strip()


    if not question:

        return {

            "answer": (
                "Please enter a question."
            ),

            "sources": [],
        }


    try:

        # ------------------------------------------
        # Step 1: Build RAG index
        # ------------------------------------------

        store = ensure_vector_store()


        if store is None:

            return {

                "answer": (
                    "I could not build a search "
                    "index for the uploaded codebase."
                ),

                "sources": [],
            }


        # ------------------------------------------
        # Step 2: Embed user question
        # ------------------------------------------

        query_chunks = [
            {
                "content": question
            }
        ]


        embedded_query = create_embeddings(
            query_chunks
        )


        if not embedded_query:

            return {

                "answer": (
                    "I could not process your question."
                ),

                "sources": [],
            }


        query_embedding = (
            embedded_query[0]["embedding"]
        )


        # ------------------------------------------
        # Step 3: Search RAG
        # ------------------------------------------

        rag_results = store.search(
            query_embedding,
            top_k=8
        )


        # ------------------------------------------
        # Step 4: Build retrieved context
        # ------------------------------------------

        context_parts = []


        for result in rag_results:

            chunk = result["chunk"]


            context_parts.append(
                f"""
FILE: {chunk["path"]}
LANGUAGE: {chunk["language"]}
LINES: {chunk["start_line"]}-{chunk["end_line"]}

CODE:
{chunk["content"]}
"""
            )


        context = "\n\n".join(
            context_parts
        )


        # ------------------------------------------
        # Step 5: Get MCP tools
        # ------------------------------------------

        mcp_tools = (
            await get_mcp_tools_async(
                current_project_path
            )
        )


        # ------------------------------------------
        # Step 6: Agent instructions
        # ------------------------------------------

        system_instruction = """
You are DevPilot, an AI developer knowledge agent.

Your job is to answer questions about the user's
uploaded codebase.

IMPORTANT RULES:

1. The uploaded repository is the primary
   source of truth.

2. Use the retrieved RAG context when it
   directly answers the question.

3. If the retrieved context is insufficient,
   use an appropriate MCP repository tool.

4. Never invent files, functions, classes,
   variables, APIs, or implementation details.

5. If the repository does not provide enough
   evidence, clearly say that you cannot determine
   the answer from the available code.

6. Mention relevant file paths.

7. Include line numbers whenever available.

8. If multiple files are involved, explain
   how they work together.

9. Clearly distinguish facts from inference.

10. Keep the answer practical and easy to
    understand.

11. Prefer a direct answer over unnecessary
    explanation.
"""


        # ------------------------------------------
        # Step 7: First Gemini request
        # ------------------------------------------

        prompt = f"""
{system_instruction}

USER QUESTION:
{question}

RETRIEVED CODE CONTEXT:
{context}

AVAILABLE MCP TOOLS:
{mcp_tools}

First analyze the retrieved code.

If the retrieved code contains enough evidence,
answer directly.

If it does not contain enough evidence,
use an appropriate MCP repository tool.

Do not guess.
"""


        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )


        # ------------------------------------------
        # Step 8: Detect MCP function call
        # ------------------------------------------

        answer = response.text or ""

        function_call = None


        if response.candidates:

            candidate = (
                response.candidates[0]
            )


            if (
                candidate.content
                and candidate.content.parts
            ):

                for part in (
                    candidate.content.parts
                ):

                    if getattr(
                        part,
                        "function_call",
                        None
                    ):

                        function_call = (
                            part.function_call
                        )

                        break


        # ------------------------------------------
        # Step 9: Execute MCP tool
        # ------------------------------------------

        if function_call:

            tool_name = (
                function_call.name
            )

            tool_arguments = dict(
                function_call.args or {}
            )


            print(
                f"MCP tool requested: "
                f"{tool_name}"
            )


            print(
                f"MCP arguments: "
                f"{tool_arguments}"
            )


            try:

                tool_result = (
                    await call_mcp_tool_async(
                        current_project_path,
                        tool_name,
                        tool_arguments,
                    )
                )


                print(
                    "MCP tool executed successfully."
                )


                # ----------------------------------
                # Convert MCP result to text
                # ----------------------------------

                tool_result_text = (
                    str(tool_result)
                )


                # ----------------------------------
                # Step 10: Final Gemini response
                # ----------------------------------

                follow_up_prompt = f"""
You are DevPilot, an AI developer knowledge agent.

The user asked:

{question}

You initially searched the uploaded repository
using RAG.

You then used this MCP repository tool:

TOOL:
{tool_name}

ARGUMENTS:
{tool_arguments}

MCP RESULT:
{tool_result_text}

Now provide the final answer.

IMPORTANT:

- Answer the user's original question directly.
- Use only evidence from the uploaded repository.
- Do not invent code or files.
- Mention relevant file paths.
- Include line numbers when available.
- Explain relationships between files when useful.
- If the evidence is insufficient, say so clearly.
"""


                final_response = (
                    client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=follow_up_prompt,
                    )
                )


                answer = (
                    final_response.text or ""
                )


            except Exception as tool_error:

                print(
                    f"MCP tool error: "
                    f"{tool_error}"
                )


                answer = (
                    "I found that additional "
                    "repository inspection was needed, "
                    "but the repository tool could not "
                    "be executed successfully."
                )


        # ------------------------------------------
        # Step 11: Fallback
        # ------------------------------------------

        if not answer.strip():

            answer = (
                "I could not generate a text answer "
                "from the available codebase evidence."
            )


        # ------------------------------------------
        # Step 12: Sources
        # ------------------------------------------

        sources = []

        seen = set()


        for result in rag_results:

            chunk = result["chunk"]


            key = (
                chunk["path"],
                chunk["start_line"],
                chunk["end_line"],
            )


            if key in seen:

                continue


            seen.add(key)


            sources.append({

                "path": chunk["path"],

                "language": chunk["language"],

                "start_line": chunk["start_line"],

                "end_line": chunk["end_line"],

            })


        # ------------------------------------------
        # Return answer
        # ------------------------------------------

        return {

            "answer": answer,

            "sources": sources,

        }


    except Exception as e:

        print(
            f"Chat error: {e}"
        )


        return {

            "answer": (
                "DevPilot encountered an error "
                "while analyzing the codebase."
            ),

            "sources": [],

            "error": str(e),

        }