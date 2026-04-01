from functools import lru_cache

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import require_permission
from app.db.session import get_db
from app.schemas.rag import IndexDocumentRequest, RagSearchRequest, RagSearchResponse
from app.services.rag_service import RagService


router = APIRouter(prefix="/rag", tags=["RAG"])


@lru_cache
def get_rag_service() -> RagService:
    return RagService()


@router.post("/index-document")
def index_document(
    payload: IndexDocumentRequest,
    db: Session = Depends(get_db),
    rag_service: RagService = Depends(get_rag_service),
    _=Depends(require_permission("documents:index")),
):
    chunks_indexed = rag_service.index_document(db, payload.document_id)
    return {"message": "Document indexed successfully.", "chunks_indexed": chunks_indexed}


@router.delete("/remove-document/{document_id}")
def remove_document(
    document_id: int,
    rag_service: RagService = Depends(get_rag_service),
    _=Depends(require_permission("documents:index")),
):
    rag_service.remove_document(document_id)
    return {"message": "Document embeddings removed successfully."}


@router.post("/search", response_model=RagSearchResponse)
def semantic_search(
    payload: RagSearchRequest,
    rag_service: RagService = Depends(get_rag_service),
    _=Depends(require_permission("documents:read")),
):
    results = rag_service.search(payload.query, payload.top_k)
    return RagSearchResponse(query=payload.query, results=results)


@router.get("/context/{document_id}")
def get_document_context(
    document_id: int,
    rag_service: RagService = Depends(get_rag_service),
    _=Depends(require_permission("documents:read")),
):
    results = rag_service.get_document_context(document_id)
    return {"document_id": document_id, "chunks": results}
