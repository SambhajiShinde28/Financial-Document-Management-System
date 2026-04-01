from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import require_permission
from app.api.routes.rag import get_rag_service
from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentSearchResponse
from app.services.document_service import DocumentService
from app.services.rag_service import RagService


router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    title: str = Form(...),
    company_name: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("documents:create")),
):
    document = DocumentService.create_document(
        db=db,
        current_user=current_user,
        title=title,
        company_name=company_name,
        document_type=document_type,
        file=file,
    )
    return document


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    _=Depends(require_permission("documents:read")),
):
    return db.query(Document).order_by(Document.created_at.desc()).all()


@router.get("/search", response_model=DocumentSearchResponse)
def search_documents(
    title: str | None = None,
    company_name: str | None = None,
    document_type: str | None = None,
    uploaded_by: int | None = None,
    db: Session = Depends(get_db),
    _=Depends(require_permission("documents:read")),
):
    items = DocumentService.search_documents(
        db=db,
        title=title,
        company_name=company_name,
        document_type=document_type,
        uploaded_by=uploaded_by,
    )
    return DocumentSearchResponse(items=items, total=len(items))


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("documents:read")),
):
    return DocumentService.get_document_or_404(db, document_id)


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    rag_service: RagService = Depends(get_rag_service),
    _=Depends(require_permission("documents:delete")),
):
    rag_service.remove_document(document_id)
    DocumentService.delete_document(db, document_id)
    return {"message": "Document deleted successfully."}
