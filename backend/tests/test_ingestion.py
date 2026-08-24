import pytest
from app.ingestion.extractor import validate_pdf, extract_pages
from app.ingestion.chunker import chunk_pages


def _make_minimal_pdf(text: str = "Hello World") -> bytes:
    """Create a minimal valid PDF in memory using fpdf2."""
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, text)
    return bytes(pdf.output())


def test_validate_pdf_rejects_non_pdf():
    with pytest.raises(ValueError, match="Not a valid PDF"):
        validate_pdf(b"not a pdf", "test.pdf")


def test_validate_pdf_rejects_large_file():
    big = b"%PDF" + b"x" * (21 * 1024 * 1024)
    with pytest.raises(ValueError, match="too large"):
        validate_pdf(big, "big.pdf")


def test_validate_pdf_rejects_wrong_extension():
    with pytest.raises(ValueError, match="extension"):
        validate_pdf(b"%PDF-1.4", "test.txt")


def test_validate_pdf_accepts_valid():
    pdf_bytes = _make_minimal_pdf()
    validate_pdf(pdf_bytes, "test.pdf")  # should not raise


def test_extract_pages_returns_pages():
    pdf_bytes = _make_minimal_pdf("Sample support policy text for testing.")
    pages = extract_pages(pdf_bytes)
    assert len(pages) >= 1
    assert pages[0]["page_number"] == 1
    assert isinstance(pages[0]["text"], str)


def test_chunker_basic():
    pages = [{"page_number": 1, "text": " ".join([f"word{i}" for i in range(100)])}]
    chunks = chunk_pages(pages, chunk_size=20, overlap=5)
    assert len(chunks) > 1
    for c in chunks:
        assert "chunk_id" in c
        assert "text" in c
        assert c["page_number"] == 1


def test_chunker_overlap():
    words = [f"w{i}" for i in range(30)]
    pages = [{"page_number": 2, "text": " ".join(words)}]
    chunks = chunk_pages(pages, chunk_size=10, overlap=3)
    # Second chunk should start 7 words in (10 - 3)
    assert len(chunks) > 1
    first_chunk_words = chunks[0]["text"].split()
    second_chunk_words = chunks[1]["text"].split()
    # Overlap means last 3 words of chunk 0 appear at start of chunk 1
    assert first_chunk_words[-3:] == second_chunk_words[:3]


def test_chunker_chunk_ids():
    pages = [{"page_number": 3, "text": " ".join(["word"] * 50)}]
    chunks = chunk_pages(pages, chunk_size=20, overlap=0)
    for i, chunk in enumerate(chunks):
        assert chunk["chunk_id"] == f"chunk_3_{i}"


def test_policy_pdf_fixture():
    import os
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "policy.pdf")
    if os.path.exists(fixture_path):
        with open(fixture_path, "rb") as f:
            pdf_bytes = f.read()
        validate_pdf(pdf_bytes, "policy.pdf")
        pages = extract_pages(pdf_bytes)
        assert len(pages) == 5
