import re
import fitz  # pymupdf

MAX_PDF_SIZE = 20 * 1024 * 1024  # 20MB


def validate_pdf(file_bytes: bytes, filename: str) -> None:
    if len(file_bytes) > MAX_PDF_SIZE:
        raise ValueError(f"File too large: {len(file_bytes)} bytes (max 20MB)")
    if not filename.lower().endswith(".pdf"):
        raise ValueError(f"Invalid file extension: {filename}")
    if not file_bytes.startswith(b"%PDF"):
        raise ValueError("Not a valid PDF file")


def extract_pages(file_bytes: bytes) -> list[dict]:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()
        pages.append({"page_number": page_num + 1, "text": text})
    doc.close()
    return pages
