"""
Phase 2 -- Quick test for the vector database.

Run this AFTER knowledge_base/build_vector_db.py to confirm the database
was built correctly and that searching it actually returns relevant
results. This does NOT touch the chatbot yet -- that wiring happens in
Phase 3.

Run this from the project root with:  python testing/test_vector_db.py
"""

import chromadb
from chromadb.config import Settings
from knowledge_base.db_location import CHROMA_DB_PATH as DB_PATH


def search(query, n_results=3):
    client = chromadb.PersistentClient(
        path=DB_PATH, settings=Settings(anonymized_telemetry=False)
    )
    collection = client.get_collection("cybersecurity_glossary")
    results = collection.query(query_texts=[query], n_results=n_results)

    print(f"\nQuery: \"{query}\"")
    print("-" * 60)
    for doc, meta, distance in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        print(f"Matched term: {meta['term']}   (distance: {distance:.3f} -- lower is a closer match)")
        print(doc[:150] + "...")
        print()


if __name__ == "__main__":
    # Notice none of these queries use the exact term name -- this tests
    # whether the database is matching by MEANING, not just exact words.
    search("How do I protect data so only authorized people can read it?")
    search("What tool centralizes security logs for a SOC analyst?")
    search("Something that tricks people into giving away their password")
    search("completely unrelated query about cooking pasta")
