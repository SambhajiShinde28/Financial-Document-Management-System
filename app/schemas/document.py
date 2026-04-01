from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    title: str
    company_name: str
    document_type: str
    filename: str
    uploaded_by: int
    created_at: datetime
    content_excerpt: str | None = None

    model_config = {"from_attributes": True}


class DocumentSearchResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
