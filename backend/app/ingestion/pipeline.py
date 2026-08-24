import uuid
from app.ingestion.extractor import validate_pdf, extract_pages
from app.ingestion.chunker import chunk_pages
from app.ai.embedder import EmbeddingAdapter
from app.retrieval.vector_store import VectorStore
from app.db import repository


def ingest_document(file_bytes: bytes, filename: str) -> dict:
    doc_id = str(uuid.uuid4())
    doc_record = {"id": doc_id, "filename": filename, "status": "pending"}
    repository.insert_document(doc_record)

    try:
        validate_pdf(file_bytes, filename)
        pages = extract_pages(file_bytes)
        chunks = chunk_pages(pages)

        embedder = EmbeddingAdapter()
        texts = [c["text"] for c in chunks]
        embeddings = embedder.embed_batch(texts)

        store = VectorStore()
        collection_name = f"doc_{doc_id}"
        store.add_chunks(collection_name, chunks, embeddings)

        repository.update_document_status(
            doc_id, "indexed",
            page_count=len(pages),
            chunk_count=len(chunks),
        )

        return repository.get_document(doc_id)
    except Exception as exc:
        repository.update_document_status(doc_id, "failed")
        raise
