import re
import requests
import chromadb
from pypdf import PdfReader
OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
GEN_MODEL = "gemma2:2b"
EMBED_MODEL = "nomic-embed-text"
DOC_PATH = "Amazon Refund policy.pdf"

# --- Step 1: Document loading (Section 3) - handles both .md and .pdf ---
def load_document(path: str) -> str:
    if path.lower().endswith(".pdf"):
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

# --- Step 2: Document splitting / chunking (Section 4) ---
# Instead of fixed word counts, we chunk by Markdown section (## headings).
# This keeps each policy topic (Refund Timelines, Return Window, Shipping
# Cost Refunds, etc.) together as one coherent, retrievable unit.
def chunk_by_section(text: str, source: str) -> list[dict]:
    # Split on lines starting with "## " or "### " (keep the heading with its body)
    pattern = r"(?=^#{1,3}\s)"
    raw_sections = re.split(pattern, text, flags=re.MULTILINE)
    chunks = []
    for section in raw_sections:
        section = section.strip()
        if not section:
            continue
        # Use the first line (the heading) as a readable chunk title
        first_line = section.splitlines()[0].lstrip("#").strip()
        chunks.append({
            "text": section,
            "title": first_line or "Untitled section",
            "source": source,
        })
    return chunks

# Fallback for PDFs (or any file without clean markdown headings) -
# PDF text extraction loses "#" symbols, so section-based chunking won't work.
def chunk_by_words(text: str, source: str, max_words: int = 150) -> list[dict]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        piece = " ".join(words[i:i + max_words])
        chunks.append({
            "text": piece,
            "title": f"Chunk {i // max_words + 1}",
            "source": source,
        })
    return chunks

def chunk_document(text: str, source: str) -> list[dict]:
    has_markdown_headings = bool(re.search(r"^#{1,3}\s", text, flags=re.MULTILINE))
    if source.lower().endswith(".md") and has_markdown_headings:
        return chunk_by_section(text, source)
    else:
        return chunk_by_words(text, source)

# --- Step 3: Embeddings (Section 5) ---
def embed(text: str) -> list[float]:
    response = requests.post(
        OLLAMA_EMBED_URL,
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["embedding"]

def generate(prompt: str) -> str:
    response = requests.post(
        OLLAMA_GENERATE_URL,
        json={"model": GEN_MODEL, "prompt": prompt, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["response"]

# --- Step 4: Vector store setup (Section 5 & 6) - ChromaDB instead of a list ---
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="amazon_refund_policy_pdf")

def index_document():
    """Load, chunk, embed, and store the document - skip if already indexed."""
    if collection.count() > 0:
        print(f"Collection already has {collection.count()} chunks. Skipping re-index.\n")
        return
    raw_text = load_document(DOC_PATH)
    if not raw_text.strip():
        raise ValueError(
            f"No text could be extracted from {DOC_PATH}. "
            "If it's a scanned PDF (images, not selectable text), it needs OCR first."
        )
    chunks = chunk_document(raw_text, source=DOC_PATH)
    collection.add(
        ids=[f"chunk_{i}" for i in range(len(chunks))],
        embeddings=[embed(c["text"]) for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[{"title": c["title"], "source": c["source"]} for c in chunks],
    )
    print(f"Indexed {len(chunks)} section-chunks into ChromaDB.\n")

# --- Step 5: Retrieval (Section 7) - ChromaDB does the similarity search ---
def retrieve(query: str, k: int = 3) -> list[dict]:
    results = collection.query(
        query_embeddings=[embed(query)],
        n_results=k,
    )
    return [
        {"text": doc, "title": meta["title"], "distance": dist}
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]

# --- Step 6: Augment + Generate (Section 2 & 8) ---
def answer(query: str, k: int = 3) -> str:
    top_chunks = retrieve(query, k)
    context = "\n\n".join(f"[{c['title']}]\n{c['text']}" for c in top_chunks)
    prompt = (
        "Answer the question using only the context below, which comes from "
        "the Amazon Refund Policy document. If the context doesn't contain "
        "the answer, say you don't know - do not guess.\n\n"
        f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    )
    result = generate(prompt)
    print(f"Q: {query}")
    print("Retrieved sections:")
    for c in top_chunks:
        print(f"  [{c['distance']:.3f}] {c['title']}")
    print(f"\nA: {result}\n")
    return result

if __name__ == "__main__":
    index_document()
    answer("Within how many days can most items be returned on Amazon.com?")
    answer("How does Amazon.in refund Pay on Delivery orders?")
    answer("What is the maximum return shipping cost refunded on Amazon.in for Prime items?")
    answer("Can I get a cash refund on Amazon.in?")
    answer("What is your policy on returning pets?")  # out-of-scope test