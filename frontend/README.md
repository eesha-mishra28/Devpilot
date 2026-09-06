# DevPilot — AI Developer Knowledge Agent

DevPilot is an AI-powered developer knowledge agent that helps developers understand, navigate, and explore complex codebases using natural-language questions.

Instead of manually searching through multiple files, developers can ask questions such as:

> **"Where is authentication implemented?"**
> **"Which files handle JWT validation?"**
> **"Explain how this API works."**
> **"What happens when a user creates a task?"**

DevPilot combines **Retrieval-Augmented Generation (RAG), semantic search, Gemini, FAISS, and Model Context Protocol (MCP)** to retrieve relevant code and generate contextual answers with file and line references.

---

## 🚀 Key Features

* 🤖 **AI-powered codebase Q&A**

  * Ask questions about a project using natural language.

* 🔍 **Retrieval-Augmented Generation**

  * Retrieves relevant code snippets before generating an answer.

* 🧠 **Semantic code search**

  * Uses embeddings to find conceptually relevant code rather than relying only on exact keyword matches.

* 📁 **Codebase intelligence**

  * Reads and analyzes supported source files across a repository.

* 🔌 **MCP integration**

  * Provides repository tools that the AI can use when additional information is required.

* 📍 **Source references**

  * Responses can include:

    * File path
    * Programming language
    * Approximate line numbers

* ⚡ **Fast vector search**

  * FAISS enables efficient similarity search across indexed code chunks.

* 🛡️ **Hallucination-aware responses**

  * The agent is instructed to avoid inventing information when the required information cannot be found.

* 💻 **Developer-focused interface**

  * Clean React-based chat interface designed for code exploration.

---

# 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │       User          │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    React Frontend   │
                         │      Vite + CSS      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    FastAPI Backend  │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
             ┌─────────────┐                 ┌─────────────┐
             │     RAG     │                 │     MCP     │
             │   Pipeline  │                 │ Tool Layer  │
             └──────┬──────┘                 └──────┬──────┘
                    │                               │
             ┌──────┴──────┐                ┌──────┴──────┐
             │ Embeddings  │                │ Repository  │
             │             │                │   Tools     │
             └──────┬──────┘                └─────────────┘
                    │
             ┌──────▼──────┐
             │    FAISS    │
             │ Vector Store│
             └──────┬──────┘
                    │
                    ▼
             ┌─────────────┐
             │   Gemini    │
             │     LLM     │
             └──────┬──────┘
                    │
                    ▼
             ┌─────────────────────┐
             │ AI Answer + Sources │
             └─────────────────────┘
```

---

# 🔄 How DevPilot Works

When a developer asks a question, DevPilot follows this general workflow:

### 1. User asks a question

For example:

```text
Where is authentication implemented?
```

### 2. Query embedding

The question is converted into a numerical vector using:

```text
all-MiniLM-L6-v2
```

### 3. Semantic retrieval

The query vector is compared against vectors representing chunks of the indexed codebase.

FAISS retrieves the most relevant chunks.

### 4. Context construction

DevPilot collects information such as:

```text
File: backend/main.py
Language: Python
Lines: 91-137

<relevant code>
```

### 5. Gemini reasoning

The retrieved context is provided to Gemini along with the user's question.

Gemini generates a developer-friendly explanation based on the available code.

### 6. MCP tool usage

If the retrieved context isn't sufficient, Gemini can request repository tools through MCP.

Available tools include:

```text
list_repository_files
search_codebase
read_repository_file
```

### 7. Final response

DevPilot returns an answer along with relevant source information.

Example:

```text
Authentication is implemented in backend/auth.py.

The JWT validation logic is handled by the
verify_token() function around lines 42–58.
```

---

# 🧠 RAG Pipeline

DevPilot's RAG pipeline consists of several stages:

```text
Codebase
   ↓
File Loader
   ↓
Document Chunks
   ↓
Embeddings
   ↓
FAISS Vector Store
   ↓
Similarity Search
   ↓
Relevant Context
   ↓
Gemini
   ↓
Answer
```

### File Loading

DevPilot scans the repository and processes supported source files.

Supported extensions include:

```text
.py
.js
.jsx
.ts
.tsx
.json
.md
.css
.html
```

Common directories such as `node_modules`, `.git`, `dist`, `build`, and virtual environments are ignored.

### Chunking

Large files are divided into smaller overlapping chunks.

Current configuration:

```text
Chunk size: 1200 characters
Overlap:    200 characters
```

Chunk metadata is preserved during processing.

### Embeddings

Each chunk is converted into a vector representation using:

```text
Sentence Transformers
all-MiniLM-L6-v2
```

This allows DevPilot to perform semantic similarity search.

### Vector Search

FAISS stores the generated vectors and retrieves the most relevant chunks for a user's question.

---

# 🔌 MCP Integration

DevPilot uses **Model Context Protocol (MCP)** as its repository tool layer.

The MCP server exposes three tools:

### `list_repository_files`

Lists supported source files in the repository.

### `search_codebase`

Searches repository files for a specific text query.

### `read_repository_file`

Reads the contents of a specific repository file.

This creates a separation between:

```text
RAG
→ Finds semantically relevant knowledge

MCP
→ Gives the AI direct access to repository tools
```

Together, they allow DevPilot to combine semantic retrieval with direct repository interaction.

---

# 🛠️ Tech Stack

| Technology                | Purpose                                |
| ------------------------- | -------------------------------------- |
| **React**                 | Frontend user interface                |
| **Vite**                  | Frontend development and build tooling |
| **CSS**                   | UI styling                             |
| **FastAPI**               | Python backend/API                     |
| **Gemini**                | Large Language Model                   |
| **Google GenAI SDK**      | Gemini API integration                 |
| **Sentence Transformers** | Local text/code embeddings             |
| **FAISS**                 | Vector similarity search               |
| **MCP**                   | AI tool/repository integration         |
| **Python**                | Backend and AI pipeline                |
| **Git/GitHub**            | Version control                        |

---

# 📂 Project Structure

```text
DevPilot/
│
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── chunker.py
│   │   ├── embeddings.py
│   │   └── vector_store.py
│   │
│   ├── mcp_tools/
│   │   ├── tools.py
│   │   └── server.py
│   │
│   ├── mcp_client.py
│   ├── main.py
│   ├── .env
│   └── requirements.txt
│
├── .gitignore
└── README.md
```

---

# ⚙️ Getting Started

## Prerequisites

Make sure you have:

* Python 3.10+
* Node.js
* npm
* Git
* A Gemini API key

---

## 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/DevPilot.git
cd DevPilot
```

---

# 2. Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 3. Configure Environment Variables

Create:

```text
backend/.env
```

Add:

```env
GEMINI_API_KEY=your_gemini_api_key
```

> Never commit `.env` or expose your API key publicly.

---

# 4. Start the Backend

From the `backend` directory:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Health check:

```text
GET /api/health
```

---

# 5. Start the Frontend

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Vite will provide the local frontend URL, typically:

```text
http://localhost:5173
```

---

# 🔐 Environment & Security

DevPilot uses environment variables for sensitive configuration.

Example:

```env
GEMINI_API_KEY=your_api_key
```

The following should **never** be committed:

```text
.env
venv/
__pycache__/
```

A `.gitignore` file is included to help prevent accidental commits.

---

# 📡 API

## Health Check

### Request

```http
GET /api/health
```

### Response

```json
{
  "status": "ok"
}
```

---

## Chat

### Request

```http
POST /api/chat
```

Example:

```json
{
  "message": "Where is authentication implemented?"
}
```

### Response

```json
{
  "answer": "Authentication is implemented in ...",
  "sources": [
    {
      "file": "backend/main.py",
      "language": "Python",
      "start_line": 91,
      "end_line": 137
    }
  ]
}
```

---

# 🎯 Example Questions

DevPilot can be used for questions such as:

```text
Where is authentication implemented?

Which files handle JWT validation?

Explain how the chat API works.

Where is the Gemini API called?

What happens when a user creates a task?

Which files contain the database logic?

What programming language is this module written in?
```

---

# 💡 Why DevPilot?

Modern software projects can contain hundreds or thousands of files. Understanding an unfamiliar repository often requires manually searching through files, following imports, and understanding relationships between different components.

DevPilot aims to reduce this friction by allowing developers to interact with their codebase using natural language.

Instead of:

```text
Search → Open file → Read code → Follow references → Understand
```

developers can use:

```text
Ask → Retrieve → Analyze → Explain
```

---

# 🧩 Design Principles

### Grounded answers

DevPilot uses retrieved repository information as the basis for responses rather than relying solely on the LLM's general knowledge.

### Source awareness

Relevant files and line ranges are preserved throughout the RAG pipeline.

### Tool-assisted reasoning

MCP allows the AI to access repository operations when semantic retrieval alone isn't enough.

### Developer-friendly output

Responses are designed to explain implementation details in a way that is useful for developers navigating unfamiliar code.

---

# 🚧 Current Limitations

DevPilot is currently an MVP/prototype.

Current limitations include:

* Repository indexing is performed when the backend starts.
* The current MCP integration handles a single tool call in the agent flow.
* MCP tool schemas are currently simplified rather than dynamically generated from each tool's exact schema.
* RAG retrieval can occasionally return additional context that is not directly relevant.
* The current implementation is primarily designed for source-code exploration rather than full software-engineering automation.

---

# 🔮 Future Improvements

Potential improvements include:

* [ ] Upload repositories directly through the UI
* [ ] Incremental codebase indexing
* [ ] Persistent vector database
* [ ] Improved code-aware chunking
* [ ] Multi-step MCP agent workflows
* [ ] Dynamic MCP tool schemas
* [ ] Conversation history
* [ ] Repository selection
* [ ] GitHub repository integration
* [ ] Authentication and user accounts
* [ ] Streaming AI responses
* [ ] Improved source ranking
* [ ] Deployment-ready architecture

---

# 📈 Learning Outcomes

This project demonstrates practical experience with:

* Full-stack application architecture
* React and modern frontend development
* REST API development
* FastAPI
* LLM integration
* Prompt engineering
* Retrieval-Augmented Generation
* Text embeddings
* Vector similarity search
* FAISS
* Sentence Transformers
* MCP
* AI agent/tool integration
* Codebase analysis
* Environment and dependency management
* Git and GitHub

---

# 👩‍💻 Author

**Eesha Mishra**

Aspiring Software Developer focused on building practical applications involving **full-stack development, AI, RAG, and developer tooling**.

---

# ⭐ Project Summary

**DevPilot** brings together **AI + RAG + semantic search + MCP** to create a developer-focused knowledge agent capable of understanding and navigating source code through natural-language interaction.

> **Ask your codebase. Understand your codebase. Build faster.**
