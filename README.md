# Financial Document Management System

A beginner-friendly full-stack project for managing financial documents with authentication, role-based access control, and semantic search.

The backend is built with FastAPI and SQLAlchemy. The frontend is built with Streamlit. Uploaded documents can be indexed into a vector database and searched using semantic similarity.

## What this project does

This system helps an organization:

- register and log in users
- assign roles and permissions
- upload and manage financial documents
- search documents by metadata
- index document content into a vector database
- run semantic search on indexed document chunks
- fetch related context for a selected document

## Tech stack

- FastAPI
- Streamlit
- SQLite
- SQLAlchemy
- JWT authentication
- RBAC
- LangChain text splitter
- HuggingFace embeddings
- Chroma vector database
- PyPDF for PDF text extraction

## Main features

- User registration and login
- JWT-based protected APIs
- Role creation and role assignment
- Default roles: `Admin`, `Financial Analyst`, `Auditor`, `Client`
- Document upload, list, get, search, and delete
- PDF, TXT, and MD document text extraction
- Chunking and embedding generation
- Vector storage in Chroma
- Semantic search with a simple finance-aware reranking step
- Streamlit UI for end-to-end testing

## Project structure

```text
.
├── app
│   ├── api
│   │   ├── dependencies.py
│   │   └── routes
│   ├── core
│   ├── db
│   ├── models
│   ├── schemas
│   ├── services
│   └── storage
├── streamlit_app.py
├── requirements.txt
├── .env.example
└── README.md
```

## Environment variables

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=9f4c2b7d1e3a8c6f0d5b9a2e7f1c4d8b6a9e3f2c7d1b5a8f0e4c6d9b2a7f1e3
ACCESS_TOKEN_EXPIRE_MINUTES=60
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
```

Meaning of each key:

- `SECRET_KEY`: private key used to sign JWT tokens
- `ACCESS_TOKEN_EXPIRE_MINUTES`: token expiry time in minutes
- `EMBEDDING_MODEL_NAME`: embedding model used for semantic search

## Setup instructions

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate the virtual environment

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the `.env` file

```bash
copy .env.example .env
```

If you already have a `.env`, keep using that file.

## How to run the project

Open two terminals.

### Terminal 1: Run FastAPI backend

```bash
uvicorn app.main:app --reload
```

FastAPI docs will open at:

```text
http://127.0.0.1:8000/docs
```

### Terminal 2: Run Streamlit frontend

```bash
streamlit run streamlit_app.py
```

## Recommended testing sequence

Use this order when testing the app from Streamlit or Swagger docs.

### 1. Register user

Endpoint:

```text
POST /auth/register
```

Sample input:

```json
{
  "full_name": "Aman Sharma",
  "email": "aman@example.com",
  "password": "Aman@123"
}
```

Note:

- the first registered user becomes `Admin`

### 2. Login

Endpoint:

```text
POST /auth/login
```

Sample input:

```json
{
  "email": "aman@example.com",
  "password": "Aman@123"
}
```

### 3. Create role

Endpoint:

```text
POST /roles/create
```

Sample input:

```json
{
  "name": "Manager",
  "permissions": [
    "documents:create",
    "documents:read",
    "documents:index"
  ]
}
```

### 4. Assign role

Endpoint:

```text
POST /users/assign-role
```

Sample input:

```json
{
  "user_id": 1,
  "role_name": "Financial Analyst"
}
```

### 5. Upload document

Endpoint:

```text
POST /documents/upload
```

Form input:

```text
title = Q4 Revenue Report
company_name = ABC Finance Ltd
document_type = report
file = choose a PDF, TXT, or MD file
```

### 6. List all documents

Endpoint:

```text
GET /documents
```

### 7. Search documents by metadata

Endpoint:

```text
GET /documents/search
```

Example query values:

```text
title=Revenue
company_name=ABC Finance Ltd
document_type=report
uploaded_by=1
```

### 8. Index document for semantic search

Endpoint:

```text
POST /rag/index-document
```

Sample input:

```json
{
  "document_id": 1
}
```

### 9. Run semantic search

Endpoint:

```text
POST /rag/search
```

Sample input:

```json
{
  "query": "financial risk related to high debt ratio",
  "top_k": 5
}
```

### 10. Get document context

Endpoint:

```text
GET /rag/context/{document_id}
```

Example:

```text
/rag/context/1
```

### 11. Delete document

Endpoint:

```text
DELETE /documents/{document_id}
```

Example:

```text
/documents/1
```

## API summary

### Authentication

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/token`

### Roles and users

- `POST /roles/create`
- `POST /users/assign-role`
- `GET /users/{id}/roles`
- `GET /users/{id}/permissions`

### Documents

- `POST /documents/upload`
- `GET /documents`
- `GET /documents/search`
- `GET /documents/{document_id}`
- `DELETE /documents/{document_id}`

### RAG

- `POST /rag/index-document`
- `DELETE /rag/remove-document/{document_id}`
- `POST /rag/search`
- `GET /rag/context/{document_id}`

## Default roles and permissions

### Admin

- full access to documents
- can create roles
- can assign roles
- can view roles and permissions

### Financial Analyst

- can upload documents
- can read documents
- can index documents

### Auditor

- can read documents
- can view roles
- can view permissions

### Client

- can read documents

## Streamlit dashboard

The Streamlit UI supports:

- register and login
- role creation
- role assignment
- role and permission lookup
- document upload
- document listing and search
- document deletion
- RAG indexing
- semantic search
- context lookup
- response viewer for debugging

## Notes about authentication

- `SECRET_KEY` is your app's JWT signing key
- it is not a Groq key or model key
- JWT token is generated after login
- the JWT token should not be stored in `.env`

## Data storage

- relational data is stored in `financial_documents.db`
- uploaded files are stored in `app/storage/documents`
- vector data is stored in `app/storage/vector_db`

## Important implementation notes

- password hashing uses `pbkdf2_sha256`
- first registered user is assigned the `Admin` role automatically
- deleting a document also removes its vector index
- semantic search uses local embeddings, not Groq

## Troubleshooting

### 403 Forbidden on role creation

Reason:

- current user does not have `roles:create`

Fix:

- log in with the first registered user
- or recreate the database and register a fresh first user

### Register endpoint crashes with bcrypt error

This project already uses `pbkdf2_sha256` to avoid that issue. If you still see old dependency issues, reinstall packages:

```bash
pip uninstall bcrypt -y
pip install -r requirements.txt
```

### Authorize button in Swagger does not work

Use the built-in token flow:

- click `Authorize`
- enter email in the `username` field
- enter password normally

### Semantic search returns nothing

Check that:

- the document was uploaded successfully
- the document was indexed using `/rag/index-document`
- the file contains readable text

## Future improvements

- add refresh tokens
- add document update endpoint
- support more document formats
- add better reranking model
- add audit logs
- add containerization with Docker

## Author note

This project is written in a clean and simple style so it is easy to understand, test, and extend.
