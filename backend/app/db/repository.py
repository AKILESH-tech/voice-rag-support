import uuid
from app.db.database import get_db


def insert_document(doc: dict) -> str:
    doc_id = doc.get("id") or str(uuid.uuid4())
    with get_db() as conn:
        conn.execute(
            "INSERT INTO documents (id, filename, page_count, chunk_count, status) VALUES (?, ?, ?, ?, ?)",
            (doc_id, doc["filename"], doc.get("page_count"), doc.get("chunk_count"), doc.get("status", "pending")),
        )
    return doc_id


def update_document_status(doc_id: str, status: str, page_count: int | None = None, chunk_count: int | None = None):
    with get_db() as conn:
        if page_count is not None and chunk_count is not None:
            conn.execute(
                "UPDATE documents SET status=?, page_count=?, chunk_count=? WHERE id=?",
                (status, page_count, chunk_count, doc_id),
            )
        elif page_count is not None:
            conn.execute("UPDATE documents SET status=?, page_count=? WHERE id=?", (status, page_count, doc_id))
        elif chunk_count is not None:
            conn.execute("UPDATE documents SET status=?, chunk_count=? WHERE id=?", (status, chunk_count, doc_id))
        else:
            conn.execute("UPDATE documents SET status=? WHERE id=?", (status, doc_id))


def get_document(doc_id: str) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
        return dict(row) if row else None


def get_all_documents() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


def insert_query(query: dict) -> str:
    query_id = query.get("id") or str(uuid.uuid4())
    with get_db() as conn:
        conn.execute(
            """INSERT INTO queries (id, document_id, mode, transcript, answer, confidence,
               retrieval_latency_ms, generation_latency_ms, stt_latency_ms)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                query_id,
                query.get("document_id"),
                query.get("mode", "text"),
                query["transcript"],
                query.get("answer"),
                query.get("confidence"),
                query.get("retrieval_latency_ms"),
                query.get("generation_latency_ms"),
                query.get("stt_latency_ms", 0),
            ),
        )
    return query_id


def get_query(query_id: str) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM queries WHERE id=?", (query_id,)).fetchone()
        return dict(row) if row else None


def insert_retrieved_chunks(chunks: list[dict]):
    with get_db() as conn:
        for chunk in chunks:
            conn.execute(
                "INSERT INTO retrieved_chunks (id, query_id, chunk_id, rank, score, text, page_number) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    str(uuid.uuid4()),
                    chunk["query_id"],
                    chunk.get("chunk_id"),
                    chunk.get("rank"),
                    chunk.get("score"),
                    chunk.get("text"),
                    chunk.get("page_number"),
                ),
            )


def get_chunks_for_query(query_id: str) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM retrieved_chunks WHERE query_id=? ORDER BY rank", (query_id,)
        ).fetchall()
        return [dict(r) for r in rows]
