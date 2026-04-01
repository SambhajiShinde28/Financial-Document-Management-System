from collections import Counter

from fastapi import HTTPException
from langchain_chroma import Chroma
from langchain_core.documents import Document as LangChainDocument
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document
from app.schemas.rag import RagChunkResponse
from app.services.document_reader import DocumentReader


FINANCIAL_TERMS = {
    "asset",
    "audit",
    "balance",
    "cash",
    "compliance",
    "contract",
    "cost",
    "debt",
    "equity",
    "expense",
    "income",
    "interest",
    "invoice",
    "liability",
    "margin",
    "profit",
    "ratio",
    "revenue",
    "risk",
    "tax",
}


class RagService:
    def __init__(self) -> None:
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model_name,
            encode_kwargs={"normalize_embeddings": True},
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        self.vector_store = Chroma(
            collection_name="financial_documents",
            embedding_function=self.embeddings,
            persist_directory=str(settings.vector_db_dir),
        )

    def index_document(self, db: Session, document_id: int) -> int:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found.")

        text = DocumentReader.extract_text(document.file_path)
        if not text:
            raise HTTPException(status_code=400, detail="Document has no readable text.")

        self.remove_document(document_id)
        chunks = self.text_splitter.split_text(text)
        langchain_docs: list[LangChainDocument] = []

        for index, chunk in enumerate(chunks):
            langchain_docs.append(
                LangChainDocument(
                    page_content=chunk,
                    metadata={
                        "document_id": document.id,
                        "chunk_id": f"{document.id}-{index}",
                        "title": document.title,
                        "company_name": document.company_name,
                        "document_type": document.document_type,
                    },
                )
            )

        if langchain_docs:
            self.vector_store.add_documents(langchain_docs)

        return len(langchain_docs)

    def remove_document(self, document_id: int) -> None:
        existing = self.vector_store.get(where={"document_id": document_id})
        ids = existing.get("ids", []) if existing else []
        if ids:
            self.vector_store.delete(ids=ids)

    def get_document_context(self, document_id: int, limit: int = 5) -> list[RagChunkResponse]:
        matches = self.vector_store.similarity_search(
            query="financial summary",
            k=limit,
            filter={"document_id": document_id},
        )
        return [
            RagChunkResponse(
                document_id=item.metadata["document_id"],
                chunk_id=item.metadata["chunk_id"],
                title=item.metadata["title"],
                company_name=item.metadata["company_name"],
                document_type=item.metadata["document_type"],
                content=item.page_content,
                score=1.0,
            )
            for item in matches
        ]

    def search(self, query: str, top_k: int = 5) -> list[RagChunkResponse]:
        search_limit = max(top_k * 4, 10)
        results = self.vector_store.similarity_search_with_relevance_scores(query, k=search_limit)

        ranked: list[RagChunkResponse] = []
        for document, base_score in results:
            reranked_score = self._financial_relevance_score(query, document.page_content, base_score)
            ranked.append(
                RagChunkResponse(
                    document_id=document.metadata["document_id"],
                    chunk_id=document.metadata["chunk_id"],
                    title=document.metadata["title"],
                    company_name=document.metadata["company_name"],
                    document_type=document.metadata["document_type"],
                    content=document.page_content,
                    score=round(reranked_score, 4),
                )
            )

        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[:top_k]

    def _financial_relevance_score(self, query: str, content: str, vector_score: float) -> float:
        query_terms = self._normalize(query)
        content_terms = self._normalize(content)
        if not query_terms or not content_terms:
            return vector_score

        overlap = len(set(query_terms) & set(content_terms))
        financial_hits = sum(1 for term in content_terms if term in FINANCIAL_TERMS)
        density_bonus = financial_hits / max(len(content_terms), 1)
        counts = Counter(content_terms)
        keyword_bonus = sum(counts[term] for term in set(query_terms))

        return float(vector_score) + overlap * 0.08 + density_bonus * 0.4 + keyword_bonus * 0.01

    @staticmethod
    def _normalize(text: str) -> list[str]:
        cleaned = text.lower().replace("/", " ").replace(",", " ").replace(".", " ")
        return [word for word in cleaned.split() if len(word) > 2]
