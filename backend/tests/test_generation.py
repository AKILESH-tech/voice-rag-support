import pytest
from unittest.mock import MagicMock, patch


def _make_chunks(scores):
    return [
        {"chunk_id": f"chunk_1_{i}", "text": f"Chunk text {i} about support.", "page_number": i + 1, "score": s, "rank": i + 1}
        for i, s in enumerate(scores)
    ]


def test_grounded_answer_uses_chunks():
    chunks = _make_chunks([0.8, 0.7])
    with patch("app.generation.generator.FallbackAIProvider") as MockProvider:
        mock_inst = MagicMock()
        mock_resp = MagicMock()
        mock_resp.text = "Support hours are 9 AM to 5 PM (page 1)."
        mock_inst.generate.return_value = mock_resp
        MockProvider.return_value = mock_inst

        from app.generation.generator import AnswerGenerator
        gen = AnswerGenerator()
        result = gen.generate("What are support hours?", chunks, "doc123")

    assert result["confidence"] == pytest.approx(0.75)
    assert len(result["citations"]) == 2
    assert result["citations"][0]["page_number"] == 1
    assert "Support hours" in result["answer"]


def test_uncertainty_response_when_no_chunks():
    with patch("app.generation.generator.FallbackAIProvider"):
        from app.generation.generator import AnswerGenerator
        gen = AnswerGenerator()
        result = gen.generate("What is the refund policy?", [], "doc123")

    assert result["confidence"] == 0.0
    assert result["citations"] == []
    assert "couldn't find" in result["answer"]


def test_citations_use_retrieved_page_numbers():
    chunks = _make_chunks([0.9, 0.6, 0.5])
    with patch("app.generation.generator.FallbackAIProvider") as MockProvider:
        mock_inst = MagicMock()
        mock_resp = MagicMock()
        mock_resp.text = "See page 1 for details."
        mock_inst.generate.return_value = mock_resp
        MockProvider.return_value = mock_inst

        from app.generation.generator import AnswerGenerator
        gen = AnswerGenerator()
        result = gen.generate("Question?", chunks, "doc456")

    pages = [c["page_number"] for c in result["citations"]]
    assert pages == [1, 2, 3]
