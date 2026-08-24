import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings


class VectorStore:
    def __init__(self):
        self._client = chromadb.PersistentClient(
            path=settings.chroma_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

    def add_chunks(self, collection_name: str, chunks: list[dict], embeddings: list[list[float]]):
        collection = self._client.get_or_create_collection(collection_name)
        collection.add(
            ids=[c["chunk_id"] for c in chunks],
            embeddings=embeddings,
            documents=[c["text"] for c in chunks],
            metadatas=[{"page_number": c["page_number"], "chunk_id": c["chunk_id"]} for c in chunks],
        )

    def search(
        self, collection_name: str, query_embedding: list[float], top_k: int
    ) -> list[dict]:
        try:
            collection = self._client.get_collection(collection_name)
        except Exception:
            return []
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        output = []
        ids = results.get("ids", [[]])[0]
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        for rank, (doc_id, doc, meta, dist) in enumerate(zip(ids, docs, metas, distances)):
            # Convert L2 distance to similarity score (0-1)
            score = 1.0 / (1.0 + dist)
            output.append({
                "chunk_id": doc_id,
                "text": doc,
                "page_number": meta.get("page_number", 0),
                "score": score,
                "rank": rank + 1,
            })
        return output

    def delete_collection(self, collection_name: str):
        try:
            self._client.delete_collection(collection_name)
        except Exception:
            pass
