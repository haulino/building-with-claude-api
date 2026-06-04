from flask import Flask, render_template, jsonify
from rag_retrieval import chunk_report, get_embeddings

app = Flask(__name__)

state = {
    "chunks": None,
    "embeddings": None,
    "store": None,
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chunk", methods=["POST"])
def chunk():
    chunks = chunk_report()
    if not chunks:
        return jsonify({"error": "No chunks found — is report.md present?"}), 400

    state["chunks"] = chunks
    state["embeddings"] = None
    state["store"] = None

    result = [
        {
            "heading": c["heading"],
            "content_preview": c["content"][:80],
        }
        for c in chunks
    ]
    return jsonify(result)


@app.route("/embed", methods=["POST"])
def embed():
    if state["chunks"] is None:
        return jsonify({"error": "Run chunking first"}), 400

    try:
        texts = [c["content"] for c in state["chunks"]]
        embeddings = get_embeddings(texts)
        state["embeddings"] = embeddings
        state["store"] = None
        return jsonify({"shape": list(embeddings.shape)})
    except Exception as e:
        error_msg = str(e)
        if "Connection refused" in error_msg or "ConnectionError" in error_msg:
            error_msg = (
                "Connection refused — is the embedding service running on port 8080?"
            )
        return jsonify({"error": error_msg}), 502


if __name__ == "__main__":
    app.run(debug=False, port=5000)
