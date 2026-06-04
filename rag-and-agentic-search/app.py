from flask import Flask, render_template, jsonify
from rag_retrieval import chunk_report

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


if __name__ == "__main__":
    app.run(debug=False, port=5000)
