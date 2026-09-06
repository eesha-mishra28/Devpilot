import asyncio
import os
import json

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

from rag.loader import load_codebase
from rag.chunker import chunk_documents
from rag.embeddings import create_embeddings
from rag.vector_store import VectorStore

from mcp_client import get_mcp_tools, call_mcp_tool


load_dotenv()

app = FastAPI(title="DevPilot API")

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


class ChatRequest(BaseModel):
    message: str


# Load and index the DevPilot codebase
documents = load_codebase(r"D:\DevPilot")
chunks = chunk_documents(documents)
embedded_chunks = create_embeddings(chunks)

vector_store = VectorStore(
    len(embedded_chunks[0]["embedding"])
)

vector_store.add(embedded_chunks)


def get_mcp_tool_definitions():
    tools = asyncio.run(get_mcp_tools())

    definitions = []

    for tool in tools:
        definitions.append({
            "name": tool.name,
            "description": tool.description or "",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for the repository.",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Repository-relative file path.",
                    },
                },
            },
        })

    return definitions


def execute_mcp_tool(tool_name, arguments):
    return asyncio.run(
        call_mcp_tool(
            tool_name,
            arguments,
        )
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat")
def chat(request: ChatRequest):
    # Convert user's question into an embedding
    query_embedding = create_embeddings([
        {
            "content": request.message,
            "path": "",
            "filename": "query",
            "extension": "",
            "language": "Unknown",
            "start_line": 0,
            "end_line": 0,
        }
    ])[0]["embedding"]

    # Retrieve relevant code using RAG
    results = vector_store.search(
        query_embedding,
        top_k=10,
    )

    context = "\n\n".join(
        f"File: {result['chunk']['path']}\n"
        f"Language: {result['chunk']['language']}\n"
        f"Lines: {result['chunk']['start_line']}-"
        f"{result['chunk']['end_line']}\n"
        f"{result['chunk']['content']}"
        for result in results
    )

    prompt = f"""
You are DevPilot, an AI developer knowledge agent.

Answer the user's question using the provided codebase context.

You have access to repository tools when you need more information.

If the context does not contain enough information, use an appropriate repository tool.

If the information still cannot be found, say so instead of inventing details.

Codebase context:
{context}

User question:
{request.message}
"""

    tool_definitions = get_mcp_tool_definitions()

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={
            "tools": [
                {
                    "function_declarations": tool_definitions,
                }
            ]
        },
    )

    # Check whether Gemini requested a tool
    if response.function_calls:
        tool_call = response.function_calls[0]

        tool_name = tool_call.name
        arguments = dict(tool_call.args)

        tool_result = execute_mcp_tool(
            tool_name,
            arguments,
        )

        tool_output = json.dumps(
            tool_result.structuredContent
            if hasattr(tool_result, "structuredContent")
            else str(tool_result),
            default=str,
        )

        follow_up_prompt = f"""
You are DevPilot, an AI developer knowledge agent.

The user asked:
{request.message}

You requested the MCP tool:
{tool_name}

The tool returned:
{tool_output}

Use this tool result to answer the user's question.

Give a clear developer-friendly answer.
Mention relevant file paths when possible.
Do not invent information.
"""

        final_response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=follow_up_prompt,
        )

        answer = final_response.text

    else:
        answer = response.text

    # Remove duplicate source files
    unique_sources = {}

    for result in results:
        chunk = result["chunk"]
        path = chunk["path"]

        if path not in unique_sources:
            unique_sources[path] = {
                "file": path,
                "language": chunk["language"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
                "distance": result["distance"],
            }

    return {
        "answer": answer,
        "sources": list(unique_sources.values()),
    }