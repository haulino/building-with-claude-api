import sys
import os

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "rag-and-agentic-search")
)

from app import app


def test_index_returns_html():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"RAG Retrieval Pipeline Explorer" in response.data
