from app.config import settings


def chunk_pages(
    pages: list[dict],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[dict]:
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap if overlap is not None else settings.chunk_overlap

    chunks = []
    for page in pages:
        text = page["text"]
        page_number = page["page_number"]
        words = text.split()
        if not words:
            continue
        start = 0
        idx = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_text = " ".join(words[start:end])
            chunk_id = f"chunk_{page_number}_{idx}"
            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "page_number": page_number,
            })
            idx += 1
            if end >= len(words):
                break
            start = end - overlap
    return chunks
