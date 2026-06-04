import sys
import os
import json
from unittest.mock import patch, MagicMock

import numpy as np

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "rag-and-agentic-search")
)

from rag_retrieval_ui import app
from rag_retrieval import create_vector_store


def test_index_returns_html():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"RAG Retrieval Pipeline Explorer" in response.data


def test_chunk_returns_list_with_headings():
    client = app.test_client()
    response = client.post("/chunk")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) >= 14
    assert "heading" in data[0]
    assert "content_preview" in data[0]
    assert len(data[0]["content_preview"]) <= 80


def test_chunk_stores_state():
    client = app.test_client()
    client.post("/chunk")
    from rag_retrieval_ui import state

    assert state["chunks"] is not None
    assert len(state["chunks"]) >= 14


def test_embed_requires_chunks_first():
    client = app.test_client()
    from rag_retrieval_ui import state

    state["chunks"] = None
    response = client.post("/embed")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_embed_returns_shape():
    client = app.test_client()
    from rag_retrieval_ui import state

    state["chunks"] = [
        {"heading": "## A", "content": "## A\nContent A"},
        {"heading": "## B", "content": "## B\nContent B"},
    ]

    mock_response = MagicMock()
    mock_response.json.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    mock_response.raise_for_status = MagicMock()

    with patch("rag_retrieval.requests.post", return_value=mock_response):
        response = client.post("/embed")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["shape"] == [2, 3]


def test_create_store_requires_embeddings():
    client = app.test_client()
    from rag_retrieval_ui import state

    state["chunks"] = [{"heading": "## A", "content": "## A\nContent"}]
    state["embeddings"] = None
    response = client.post("/create-store")
    assert response.status_code == 400


def test_create_store_returns_counts():
    client = app.test_client()
    from rag_retrieval_ui import state

    state["chunks"] = [
        {"heading": "## A", "content": "## A\nContent A"},
        {"heading": "## B", "content": "## B\nContent B"},
    ]
    state["embeddings"] = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

    response = client.post("/create-store")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["chunk_count"] == 2
    assert data["matrix_shape"] == [2, 3]


def test_search_requires_store():
    client = app.test_client()
    from rag_retrieval_ui import state

    state["store"] = None
    response = client.post("/search", json={"query": "test"})
    assert response.status_code == 400


def test_search_requires_query():
    client = app.test_client()
    from rag_retrieval_ui import state

    state["store"] = {"chunks": [], "embeddings": np.array([])}
    response = client.post("/search", json={})
    assert response.status_code == 400


def test_search_returns_ranked_results():
    client = app.test_client()
    from rag_retrieval_ui import state

    chunks = [
        {"heading": "## A", "content": "## A\nFirst chunk content here"},
        {"heading": "## B", "content": "## B\nSecond chunk content here"},
        {"heading": "## C", "content": "## C\nThird chunk content here"},
    ]
    embeddings = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    state["store"] = create_vector_store(chunks, embeddings)

    mock_response = MagicMock()
    mock_response.json.return_value = [[1.0, 0.0, 0.0]]
    mock_response.raise_for_status = MagicMock()

    with patch("rag_retrieval.requests.post", return_value=mock_response):
        response = client.post("/search", json={"query": "first"})

    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 3
    assert data[0]["heading"] == "## A"
    assert "score" in data[0]
    assert "content_preview" in data[0]
    assert "content" in data[0]
    assert len(data[0]["content_preview"]) <= 80
