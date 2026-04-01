from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.user import User
from app.services.document_reader import DocumentReader
from app.services.file_service import FileService


class DocumentService:
    @staticmethod
    def create_document(
        db: Session,
        current_user: User,
        title: str,
        company_name: str,
        document_type: str,
        file: UploadFile,
    ) -> Document:
        saved_path = FileService.save_upload(file)

        excerpt = None
        try:
            full_text = DocumentReader.extract_text(str(saved_path))
            excerpt = full_text[:400] if full_text else None
        except Exception:
            excerpt = None

        document = Document(
            title=title,
            company_name=company_name,
            document_type=document_type,
            filename=file.filename or saved_path.name,
            file_path=str(saved_path),
            content_excerpt=excerpt,
            uploaded_by=current_user.id,
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def get_document_or_404(db: Session, document_id: int) -> Document:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="Document not found.")
        return document

    @staticmethod
    def delete_document(db: Session, document_id: int) -> None:
        document = DocumentService.get_document_or_404(db, document_id)
        path = Path(document.file_path)
        if path.exists():
            path.unlink()
        db.delete(document)
        db.commit()

    @staticmethod
    def search_documents(
        db: Session,
        title: str | None = None,
        company_name: str | None = None,
        document_type: str | None = None,
        uploaded_by: int | None = None,
    ) -> list[Document]:
        query = db.query(Document)

        if title:
            query = query.filter(Document.title.ilike(f"%{title}%"))
        if company_name:
            query = query.filter(Document.company_name.ilike(f"%{company_name}%"))
        if document_type:
            query = query.filter(Document.document_type.ilike(f"%{document_type}%"))
        if uploaded_by:
            query = query.filter(Document.uploaded_by == uploaded_by)

        return query.order_by(Document.created_at.desc()).all()
