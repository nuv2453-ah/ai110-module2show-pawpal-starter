import os
from pathlib import Path


KNOWLEDGE_BASE_DIR = Path(__file__).parent / "knowledge_base"


def load_documents() -> dict[str, str]:
    """Load all markdown files from the knowledge base directory."""
    documents = {}
    for filepath in KNOWLEDGE_BASE_DIR.glob("*.md"):
        with open(filepath, "r") as f:
            documents[filepath.stem] = f.read()
    return documents


def chunk_document(text: str, chunk_size: int = 400) -> list[str]:
    """Split a document into overlapping chunks by paragraph."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) < chunk_size:
            current_chunk += "\n\n" + paragraph
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def build_index() -> list[dict]:
    """Build a searchable index of all document chunks."""
    documents = load_documents()
    index = []

    for doc_name, content in documents.items():
        chunks = chunk_document(content)
        for i, chunk in enumerate(chunks):
            index.append({
                "source": doc_name,
                "chunk_id": i,
                "text": chunk,
            })

    return index


def retrieve(query: str, index: list[dict], top_k: int = 3) -> list[dict]:
    """
    Retrieve the most relevant chunks for a query using keyword matching.
    Returns top_k chunks ranked by relevance score.
    """
    query_terms = set(query.lower().split())

    scored = []
    for chunk in index:
        chunk_text = chunk["text"].lower()
        score = sum(1 for term in query_terms if term in chunk_text)
        if score > 0:
            scored.append({**chunk, "score": score})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def format_context(retrieved_chunks: list[dict]) -> str:
    """Format retrieved chunks into a clean context string for the prompt."""
    if not retrieved_chunks:
        return "No relevant information found in the knowledge base."

    lines = ["Relevant pet care information:"]
    for chunk in retrieved_chunks:
        lines.append(f"\n--- From {chunk['source'].replace('_', ' ').title()} ---")
        lines.append(chunk["text"])

    return "\n".join(lines)


if __name__ == "__main__":
    print("Building knowledge base index...")
    index = build_index()
    print(f"Index built: {len(index)} chunks from {len(load_documents())} documents\n")

    test_queries = [
        "how often should I feed my dog",
        "cat medication toxic",
        "missed dose what to do",
    ]

    for query in test_queries:
        print(f"Query: '{query}'")
        results = retrieve(query, index)
        for r in results:
            print(f"  [{r['source']} | score={r['score']}] {r['text'][:80]}...")
        print()