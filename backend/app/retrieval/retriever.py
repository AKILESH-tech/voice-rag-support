from app.ai.embedder import EmbeddingAdapter
from app.retrieval.vector_store import VectorStore
from app.config import settings


def retrieve(
    document_id: str,
    question: str,
    top_k: int | None = None,
    threshold: float | None = None,
) -> list[dict]:
    top_k = top_k or settings.top_k
    threshold = threshold if threshold is not None else settings.retrieval_threshold

    embedder = EmbeddingAdapter()
    query_embedding = embedder.embed(question)

    store = VectorStore()
    collection_name = f"doc_{document_id}"
    results = store.search(collection_name, query_embedding, top_k)

    return [r for r in results if r["score"] >= threshold]
