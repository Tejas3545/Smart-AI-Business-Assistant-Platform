from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.utils.retry import default_retry
from app.models.document import Document


class RAGStore:
    def __init__(self) -> None:
        # Defer heavy imports until initialization so the web service can start
        # without loading ML dependencies.
        import chromadb
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

        embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient(path=settings.chroma_path)
        self.collection = self.client.get_or_create_collection(
            name="business_docs",
            embedding_function=embedding_fn,
        )

    @staticmethod
    def chunk_text(text: str, max_len: int = 700, overlap: int = 120) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + max_len, len(text))
            chunks.append(text[start:end])
            start = end - overlap
            if start < 0:
                start = 0
            if end == len(text):
                break
        return chunks

    async def add_document(
        self,
        db: AsyncSession,
        user_id: int,
        filename: str,
        content: str,
        content_type: str | None = None,
        source: str | None = None,
    ) -> Document:
        document = Document(
            user_id=user_id,
            filename=filename,
            content_type=content_type,
            source=source,
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)

        chunks = self.chunk_text(content)
        if not chunks:
            chunks = [content[:1000] or "No readable text found."]
        ids = [f"doc-{document.id}-chunk-{i}" for i in range(len(chunks))]
        metadatas = [{"doc_id": document.id, "user_id": user_id} for _ in chunks]
        self.collection.add(ids=ids, documents=chunks, metadatas=metadatas)
        return document

    def delete_document(self, user_id: int, document_id: int) -> None:
        self.collection.delete(where={"$and": [{"user_id": user_id}, {"doc_id": document_id}]})

    @default_retry
    def query(self, user_id: int, question: str, limit: int = 4) -> List[dict]:
        results = self.collection.query(
            query_texts=[question],
            n_results=limit,
            where={"user_id": user_id},
        )
        matches = []
        for doc, metadata in zip(results.get("documents", [[]])[0], results.get("metadatas", [[]])[0]):
            matches.append(
                {
                    "document_id": metadata.get("doc_id"),
                    "snippet": doc,
                }
            )
        return matches


_rag_singleton: Optional[RAGStore] = None


def get_rag_store() -> RAGStore:
    global _rag_singleton
    if _rag_singleton is None:
        _rag_singleton = RAGStore()
    return _rag_singleton
