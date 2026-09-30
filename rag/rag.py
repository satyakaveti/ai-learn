"""
rag_demo.py — a minimal, complete RAG pipeline:
chunk -> embed -> store -> retrieve -> generate,
using a free local LLM and embedding model via Ollama,
with ChromaDB as the vector store.
"""

import requests
import chromadb

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
GEN_MODEL = "gemma2:2b"
EMBED_MODEL = "nomic-embed-text"

company_docs = [
    "Refund Policy: Refunds are accepted within 30 days of purchase, as long "
    "as the item is unused and you have a receipt.",

    "Shipping Policy: Standard shipping takes 5-7 business days. Express "
    "shipping takes 1-2 business days for an additional fee.",

    "Warranty Policy: All electronics come with a 1-year manufacturer "
    "warranty covering defects, but not accidental damage.",
]


def chunk_text(text: str, max_words: int = 40) -> list[str]:
    print("Split text into chunks of roughly max_words words each.")
    words = text.split()
    print("words: ", words)
    return [
        " ".join(words[i:i + max_words])
        for i in range(0, len(words), max_words)
    ]


def embed(text: str) -> list[float]:
    print("Get an embedding vector for a piece of text from the local model.")
    response = requests.post(
        OLLAMA_EMBED_URL,
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=60,
    )
    response.raise_for_status()
    #print("Embedding vector: ", response.json())
    return response.json()["embedding"]


def generate(prompt: str) -> str:
    print("Generate - Prompt: ", prompt)
    response = requests.post(
        OLLAMA_GENERATE_URL,
        json={"model": GEN_MODEL, "prompt": prompt, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["response"]


# --- Step 1 & 2: Chunk and build the vector store (ChromaDB instead of a list) ---
print("1. Connect with ChromaDB")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="company_docs_1")
print(f"Collection: {collection}")


if collection.count() == 0:
    chunk_id = 0
    print("2. Chunk creation and Storing in ChromaDB")
    for doc in company_docs:
        print(f"--Chunk {chunk_id}: {doc}")
        for chunk in chunk_text(doc):
            collection.add(
                ids=[f"chunk_{chunk_id}"],
                embeddings=[embed(chunk)],
                documents=[chunk],
            )
            chunk_id += 1
    print(f"--Indexed {collection.count()} chunks.\n")
else:
    print(f"--Collection already has {collection.count()} chunks. Skipping re-index.\n")


# --- Step 3: Retrieve top-k most similar chunks for a query ---
def retrieve(query: str, k: int = 2) -> list[dict]:
    results = collection.query(
        query_embeddings=[embed(query)],
        n_results=k,
    )
    return [
        {"text": doc, "distance": dist}
        for doc, dist in zip(results["documents"][0], results["distances"][0])
    ]


# --- Step 4: Augment + Generate ---
def answer(query: str, k: int = 2) -> str:
    top_chunks = retrieve(query, k)
    context = "\n".join(f"- {c['text']}" for c in top_chunks)

    prompt = (
        "Answer the question using only the context below. If the context "
        "doesn't contain the answer, say you don't know.\n\n"
        f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    )

    result = generate(prompt)

    print(f"Q: {query}")
    print("Retrieved chunks:")
    for c in top_chunks:
        print(f"  [dist={c['distance']:.3f}] {c['text']}")
    print(f"\nA: {result}\n")
    return result


if __name__ == "__main__":
    answer("What's your refund policy?")
    #answer("How long does shipping take?")
    #answer("Do you cover water damage under warranty?")