from unittest.mock import patch, MagicMock

import numpy as np

from rag_retrieval import (
    chunk_report,
    get_embeddings,
    create_vector_store,
    get_query_embedding,
    search_store,
)


def test_chunk_report_returns_list_of_dicts():
    chunks = chunk_report()
    assert isinstance(chunks, list)
    assert len(chunks) > 0
    for chunk in chunks:
        assert "heading" in chunk
        assert "content" in chunk


def test_chunk_report_splits_all_sections():
    chunks = chunk_report()
    assert len(chunks) >= 14


def test_chunk_report_heading_in_content():
    chunks = chunk_report()
    for chunk in chunks:
        assert chunk["heading"] in chunk["content"]


def test_get_embeddings_calls_endpoint():
    mock_response = MagicMock()
    mock_response.json.return_value = [[0.1, 0.2, 0.3]]
    mock_response.raise_for_status = MagicMock()

    with patch("rag_retrieval.requests.post", return_value=mock_response) as mock_post:
        result = get_embeddings(["hello"], endpoint_url="http://test:8080/embed")

    mock_post.assert_called_once_with(
        "http://test:8080/embed", json={"inputs": ["hello"]}
    )
    assert isinstance(result, np.ndarray)
    assert result.shape == (1, 3)


def test_get_query_embedding_returns_1d_array():
    mock_response = MagicMock()
    mock_response.json.return_value = [[0.1, 0.2, 0.3]]
    mock_response.raise_for_status = MagicMock()

    with patch("rag_retrieval.requests.post", return_value=mock_response):
        result = get_query_embedding(
            "test query", endpoint_url="http://test:8080/embed"
        )

    assert result.shape == (3,)


def test_create_vector_store_structure():
    chunks = [{"heading": "## Test", "content": "## Test\nSome content"}]
    embeddings = np.array([[0.1, 0.2, 0.3]])

    store = create_vector_store(chunks, embeddings)

    assert store["chunks"] == chunks
    assert np.array_equal(store["embeddings"], embeddings)


def test_search_store_returns_top_k():
    chunks = [
        {"heading": "## A", "content": "## A\nFirst"},
        {"heading": "## B", "content": "## B\nSecond"},
        {"heading": "## C", "content": "## C\nThird"},
    ]
    embeddings = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    store = create_vector_store(chunks, embeddings)

    query_embedding = np.array([1.0, 0.0, 0.0])
    results = search_store(query_embedding, store, top_k=2)

    assert len(results) == 2
    assert results[0]["heading"] == "## A"
    assert results[0]["score"] > results[1]["score"]


def test_search_store_scores_sorted_descending():
    chunks = [
        {"heading": "## A", "content": "## A\nFirst"},
        {"heading": "## B", "content": "## B\nSecond"},
        {"heading": "## C", "content": "## C\nThird"},
    ]
    embeddings = np.array(
        [
            [0.5, 0.5, 0.0],
            [0.9, 0.1, 0.0],
            [0.1, 0.1, 0.9],
        ]
    )
    store = create_vector_store(chunks, embeddings)

    query_embedding = np.array([1.0, 0.0, 0.0])
    results = search_store(query_embedding, store, top_k=3)

    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)
