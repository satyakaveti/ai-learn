from pathlib import Path

import chromadb

# Persist to the project-root ./chroma_db folder regardless of where the script is run from
DB_PATH = Path(__file__).resolve().parent.parent / "chroma_db"

client = chromadb.PersistentClient(path=str(DB_PATH))
print(f"List of collections:  {client.list_collections()}")

collection = client.get_or_create_collection(name="my_collection")
print("Get Collection:", collection.count())
"""
print("Insert Collection:")
collection.upsert(
    ids=["p1", "p2", "p3"],
    documents=[
        "The sky is blue",
        "The grass is green",
        "Bananas are yellow",
    ],
    metadatas=[
        {"category": "sky"},
        {"category": "plant"},
        {"category": "fruit"},
    ],
)

print("Get Collection:", collection.count())
"""

"""
results = collection.query(
    query_texts=["What color is the sky?"],
    n_results=2,
)
print("Query Results: ", results)
"""

results = collection.query(
    query_texts=["What color is the sky?"],
    n_results=2,
    include=["documents", "metadatas", "distances", "embeddings"],
)
print(results["embeddings"])
