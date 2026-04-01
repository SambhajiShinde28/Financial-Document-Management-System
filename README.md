# Financial Document Management System

FastAPI-based financial document management platform with JWT authentication, role-based access control, metadata search, and semantic retrieval over indexed document content.

## Overview

This project provides a backend API and a Streamlit client for managing financial documents such as reports, invoices, and contracts. Documents are stored with structured metadata in a relational database and indexed into a vector store for semantic search and contextual retrieval.

## Key Capabilities

- User registration and authentication with JWT
- Role-based access control for `Admin`, `Financial Analyst`, `Auditor`, and `Client`
- Document upload, retrieval, deletion, and metadata filtering
- Text extraction from PDF, TXT, and MD files
- Chunking, embedding generation, and vector indexing
- Semantic search with a lightweight finance-aware reranking layer
- Streamlit interface for end-to-end operation and testing

## Technology Stack

- FastAPI
- Streamlit
- SQLAlchemy
- SQLite
- LangChain text splitters
- HuggingFace sentence-transformer embeddings
- Chroma vector database
- PyPDF

## Architecture

```text
Streamlit UI
    |
    v
FastAPI application
    |
    +-- Authentication and RBAC
    +-- Document management APIs
    +-- RAG indexing and retrieval services
    |
    +-- SQLite for metadata
    +-- Local file storage for uploaded documents
    +-- Chroma for vector search
```

## Repository Structure

```text
app/
  api/
  core/
  db/
  models/
  schemas/
  services/
  storage/
streamlit_app.py
requirements.txt
.env.example
README.md
```

## Configuration

Create a `.env` file in the project root:

```env
SECRET_KEY=your-generated-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
```

`SECRET_KEY` is used to sign JWT tokens and should be a long random value generated for your environment.

## Local Setup

```bash
uv venv
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

## Running the Application

Start the API server:

```bash
uvicorn app.main:app --reload
```

Start the Streamlit client in a separate terminal:

```bash
streamlit run streamlit_app.py
```

Available interfaces:

- FastAPI docs: `http://127.0.0.1:8000/docs`
- Streamlit UI: default Streamlit local URL shown in terminal

## Core API Surface

Authentication:

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/token`

Roles and users:

- `POST /roles/create`
- `POST /users/assign-role`
- `GET /users/{id}/roles`
- `GET /users/{id}/permissions`

Documents:

- `POST /documents/upload`
- `GET /documents`
- `GET /documents/search`
- `GET /documents/{document_id}`
- `DELETE /documents/{document_id}`

RAG:

- `POST /rag/index-document`
- `DELETE /rag/remove-document/{document_id}`
- `POST /rag/search`
- `GET /rag/context/{document_id}`

## Typical Workflow

1. Register the first user. The first account is assigned the `Admin` role automatically.
2. Log in and obtain a JWT token, or use the Streamlit interface which stores it in session state.
3. Upload financial documents with title, company name, and document type.
4. Index selected documents through the RAG endpoint.
5. Run metadata search or semantic search depending on the use case.
6. Retrieve contextual chunks for a document or remove documents when no longer needed.

## Storage

- Relational metadata: `financial_documents.db`
- Uploaded files: `app/storage/documents`
- Vector store: `app/storage/vector_db`

## Implementation Notes

- Password hashing uses `pbkdf2_sha256`
- Document deletion also removes indexed vector entries
- Semantic retrieval uses local embeddings and does not require an external LLM provider
- Swagger authorization is supported through the `/auth/token` endpoint

## Troubleshooting

`403 Forbidden` on role operations:
- Log in with an `Admin` user. Only users with `roles:create` can create roles.

Password hashing or legacy bcrypt issues:

```bash
uv pip uninstall bcrypt
uv pip install -r requirements.txt
```

No semantic results returned:
- Ensure the document was uploaded successfully, contains readable text, and has been indexed via `/rag/index-document`.

## Future Enhancements

- Refresh-token support
- Document update and versioning
- Additional document parsers
- Model-based reranking
- Dockerized deployment
