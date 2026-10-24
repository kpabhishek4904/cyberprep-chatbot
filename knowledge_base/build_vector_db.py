"""
Phase 2 -- Build the Knowledge Base

Reads the curated glossary (source_documents/glossary.json), converts each
entry into a single text document, and stores it in a local ChromaDB vector
database (saved to the chroma_db/ folder, which this script creates).

This does NOT connect to the chatbot yet -- that happens in Phase 3.
Run this script on its own first, and use test_vector_db.py to confirm it
worked, before touching app.py at all.

Run this from the project root with:  python knowledge_base/build_vector_db.py
"""

import json
import os
import chromadb
from chromadb.config import Settings
from knowledge_base.db_location import CHROMA_DB_PATH as DB_PATH

HERE = os.path.dirname(os.path.abspath(__file__))
GLOSSARY_PATH = os.path.join(HERE, "source_documents", "glossary.json")


def load_glossary():
    with open(GLOSSARY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build():
    glossary = load_glossary()
    print(f"Loaded {len(glossary)} terms from glossary.json")

    # PersistentClient saves the database to disk at DB_PATH, so it's still
    # there the next time you run the program -- you don't have to rebuild
    # it every time.
    # anonymized_telemetry=False silences the (harmless but noisy) telemetry
    # warnings you may have seen in the terminal -- purely cosmetic, has no
    # effect on how the database works.
    client = chromadb.PersistentClient(
        path=DB_PATH, settings=Settings(anonymized_telemetry=False)
    )

    # If a collection already exists from a previous run, remove it first.
    # This means you can safely re-run this script any time you edit
    # glossary.json, and it will always rebuild cleanly from scratch.
    try:
        client.delete_collection("cybersecurity_glossary")
    except Exception:
        pass

    # A "collection" is just the name ChromaDB uses for one database/table.
    # We don't specify an embedding function here, so Chroma uses its
    # built-in default one automatically (it downloads a small model the
    # first time you run this -- that's expected and only happens once).
    collection = client.create_collection("cybersecurity_glossary")

    ids = []
    documents = []
    metadatas = []

    for i, entry in enumerate(glossary):
        term = entry["term"]
        # Combine the whole entry into one block of text. This is what
        # actually gets converted into an embedding and searched later.
        text = (
            f"{term}. "
            f"What: {entry['what']} "
            f"Why: {entry['why']} "
            f"Where: {entry['where']} "
            f"Key terms: {', '.join(entry['keywords'])}"
        )
        ids.append(f"term_{i}")
        documents.append(text)
        metadatas.append({"term": term})

    collection.add(ids=ids, documents=documents, metadatas=metadatas)

    print(f"Stored {len(documents)} entries in the vector database.")
    print(f"Database location: {DB_PATH}")


if __name__ == "__main__":
    build()
