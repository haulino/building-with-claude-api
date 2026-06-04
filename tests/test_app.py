import sys
import os
import json

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "rag-and-agentic-search")
)

from app import app


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
    from app import state

    assert state["chunks"] is not None
    assert len(state["chunks"]) >= 14
