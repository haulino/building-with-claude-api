import os
import re
from pathlib import Path

import numpy as np
import requests
from dotenv import load_dotenv

load_dotenv()

# Embedding model: sentence-transformers/all-MiniLM-L6-v2
# "sentence-transformers" is the HuggingFace org (namespace) that publishes the model.
# Format is org-name/model-name, like a GitHub username/repo.
EMBEDDING_URL = os.getenv("EMBEDDING_SERVICE_URL", "http://localhost:8080/embed")


def chunk_report(file_path=None):
    """Read report.md and split into chunks by ## headings."""
    if file_path is None:
        file_path = Path(__file__).parent / "report.md"

    text = Path(file_path).read_text()

    sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)

    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue

        lines = section.split("\n")
        heading = lines[0].strip()
        chunks.append({"heading": heading, "content": section})

    return chunks


def get_embeddings(texts, endpoint_url=None):
    """POST texts to embedding service, return numpy array."""
    if endpoint_url is None:
        endpoint_url = EMBEDDING_URL

    response = requests.post(endpoint_url, json={"inputs": texts})
    response.raise_for_status()

    return np.array(response.json())


def create_vector_store(chunks, embeddings):
    """Bundle chunks and embeddings into a simple dict."""
    return {"chunks": chunks, "embeddings": embeddings}


def get_query_embedding(query, endpoint_url=None):
    """Get embedding for a single query string."""
    embeddings = get_embeddings([query], endpoint_url)
    return embeddings[0]


def search_store(query_embedding, store, top_k=3):
    """Find top-k most similar chunks using cosine similarity."""
    embeddings = store["embeddings"]

    dot_products = np.dot(embeddings, query_embedding)
    query_norm = np.linalg.norm(query_embedding)
    embedding_norms = np.linalg.norm(embeddings, axis=1)
    similarities = dot_products / (embedding_norms * query_norm)

    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for i in top_indices:
        chunk = store["chunks"][i]
        results.append(
            {
                "heading": chunk["heading"],
                "content": chunk["content"],
                "score": float(similarities[i]),
            }
        )

    return results


if __name__ == "__main__":
    chunks = chunk_report()
    print(f"Chunked report into {len(chunks)} sections")

    texts = [chunk["content"] for chunk in chunks]
    embeddings = get_embeddings(texts)
    print(f"Generated embeddings with shape {embeddings.shape}")

    store = create_vector_store(chunks, embeddings)

    query = "What cybersecurity incidents occurred?"
    query_embedding = get_query_embedding(query)
    print(f"\nQuery: {query}")

    results = search_store(query_embedding, store)
    print(f"\nTop {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['heading']} (score: {result['score']:.4f})")
        print(f"   {result['content'][:100]}...")
