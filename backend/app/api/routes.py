import time
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.ingestion.pipeline import ingest_document
from app.retrieval.retriever import retrieve
from app.generation.generator import AnswerGenerator
from app.db import repository

router = APIRouter(prefix="/api")


class QueryRequest(BaseModel):
    document_id: str
    question: str
    mode: str = "text"


@router.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    file_bytes = await file.read()
    if len(file_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 20MB)")
    if not file_bytes.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="Invalid PDF file")
    try:
        doc = ingest_document(file_bytes, file.filename)
        return doc
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)[:200]}")


@router.get("/documents")
def list_documents():
    return repository.get_all_documents()


@router.get("/documents/{doc_id}")
def get_document(doc_id: str):
    doc = repository.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("/query")
def ask_query(req: QueryRequest):
    doc = repository.get_document(req.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc["status"] != "indexed":
        raise HTTPException(status_code=400, detail=f"Document not indexed yet (status: {doc['status']})")

    t0 = time.time()
    chunks = retrieve(req.document_id, req.question)
    retrieval_ms = int((time.time() - t0) * 1000)

    t1 = time.time()
    gen = AnswerGenerator()
    result = gen.generate(req.question, chunks, req.document_id)
    generation_ms = int((time.time() - t1) * 1000)

    query_id = str(uuid.uuid4())
    repository.insert_query({
        "id": query_id,
        "document_id": req.document_id,
        "mode": req.mode,
        "transcript": req.question,
        "answer": result["answer"],
        "confidence": result["confidence"],
        "retrieval_latency_ms": retrieval_ms,
        "generation_latency_ms": generation_ms,
        "stt_latency_ms": 0,
    })

    if chunks:
        repository.insert_retrieved_chunks([
            {
                "query_id": query_id,
                "chunk_id": c["chunk_id"],
                "rank": c["rank"],
                "score": c["score"],
                "text": c["text"],
                "page_number": c["page_number"],
            }
            for c in chunks
        ])

    return {
        "query_id": query_id,
        "answer": result["answer"],
        "confidence": result["confidence"],
        "citations": result["citations"],
        "timings": {
            "retrieval_latency_ms": retrieval_ms,
            "generation_latency_ms": generation_ms,
            "total_ms": retrieval_ms + generation_ms,
        },
    }


from app.retrieval.vector_store import VectorStore

@router.delete("/documents/{doc_id}", status_code=204)
def delete_document(doc_id: str):
    doc = repository.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    vs = VectorStore()
    vs.delete_collection(doc_id)
    repository.delete_document(doc_id)


@router.get("/queries/{query_id}")
def get_query(query_id: str):
    query = repository.get_query(query_id)
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    chunks = repository.get_chunks_for_query(query_id)
    return {**query, "retrieved_chunks": chunks}


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    from app.speech.stt import transcribe
    audio_bytes = await file.read()
    result = transcribe(audio_bytes)
    if not result.get("available"):
        raise HTTPException(status_code=503, detail=f"STT unavailable: {result.get('error', 'unknown')}")
    return result
