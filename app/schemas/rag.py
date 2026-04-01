from pydantic import BaseModel


class IndexDocumentRequest(BaseModel):
    document_id: int


class RagSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class RagChunkResponse(BaseModel):
    document_id: int
    chunk_id: str
    title: str
    company_name: str
    document_type: str
    content: str
    score: float


class RagSearchResponse(BaseModel):
    query: str
    results: list[RagChunkResponse]
