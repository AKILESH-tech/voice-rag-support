import pytest
from unittest.mock import MagicMock, patch


def test_retrieve_returns_ranked_chunks():
    mock_embedding = [0.1] * 768
    mock_chunks = [
        {"chunk_id": "chunk_1_0", "text": "Support hours are 9-5.", "page_number": 1, "score": 0.8, "rank": 1},
        {"chunk_id": "chunk_2_0", "text": "Refund policy is 30 days.", "page_number": 2, "score": 0.6, "rank": 2},
    ]

    with patch("app.retrieval.retriever.EmbeddingAdapter") as MockEmbedder, \
         patch("app.retrieval.retriever.VectorStore") as MockStore:
        mock_embedder_inst = MagicMock()
        mock_embedder_inst.embed.return_value = mock_embedding
        MockEmbedder.return_value = mock_embedder_inst

        mock_store_inst = MagicMock()
        mock_store_inst.search.return_value = mock_chunks
        MockStore.return_value = mock_store_inst

        from app.retrieval.retriever import retrieve
        results = retrieve("doc123", "What are support hours?", top_k=5, threshold=0.4)

    assert len(results) == 2
    assert results[0]["score"] == 0.8
    assert results[1]["rank"] == 2


def test_retrieve_filters_below_threshold():
    mock_embedding = [0.1] * 768
    mock_chunks = [
        {"chunk_id": "chunk_1_0", "text": "low relevance text", "page_number": 1, "score": 0.2, "rank": 1},
    ]

    with patch("app.retrieval.retriever.EmbeddingAdapter") as MockEmbedder, \
         patch("app.retrieval.retriever.VectorStore") as MockStore:
        mock_embedder_inst = MagicMock()
        mock_embedder_inst.embed.return_value = mock_embedding
        MockEmbedder.return_value = mock_embedder_inst

        mock_store_inst = MagicMock()
        mock_store_inst.search.return_value = mock_chunks
        MockStore.return_value = mock_store_inst

        from app.retrieval.retriever import retrieve
        results = retrieve("doc123", "What is the refund policy?", top_k=5, threshold=0.4)

    assert results == []


def test_retrieve_empty_collection():
    mock_embedding = [0.1] * 768

    with patch("app.retrieval.retriever.EmbeddingAdapter") as MockEmbedder, \
         patch("app.retrieval.retriever.VectorStore") as MockStore:
        mock_embedder_inst = MagicMock()
        mock_embedder_inst.embed.return_value = mock_embedding
        MockEmbedder.return_value = mock_embedder_inst

        mock_store_inst = MagicMock()
        mock_store_inst.search.return_value = []
        MockStore.return_value = mock_store_inst

        from app.retrieval.retriever import retrieve
        results = retrieve("doc123", "Anything?", top_k=5, threshold=0.4)

    assert results == []
