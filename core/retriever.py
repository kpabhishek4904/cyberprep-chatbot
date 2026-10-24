"""
Phase 3 -- Retriever

Searches the vector database built in Phase 2 and returns the most relevant
glossary entries for a given question. This is the "Retrieval" step of RAG
(Retrieval-Augmented Generation) -- it runs BEFORE the LLM is called, and
its output gets attached as extra context for the model to ground its
answer in.
"""

import os
import chromadb
from chromadb.config import Settings

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(HERE), "knowledge_base", "chroma_db")

# Based on testing in Phase 2: genuinely relevant matches scored roughly
# 0.86-1.43, while a clearly unrelated query scored 1.89+. This threshold
# draws the line between "worth using as context" and "not relevant enough
# to bother including." Adjust this later if testing shows it's too
# strict or too loose.
RELEVANCE_THRESHOLD = 1.6
N_RESULTS = 3

# These stay None until first used, so we only connect to the database
# once per run instead of reconnecting on every single question.
_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(
            path=DB_PATH, settings=Settings(anonymized_telemetry=False)
        )
        _collection = _client.get_collection("cybersecurity_glossary")
    return _collection


def retrieve_context(query: str) -> str:
    """
    Search the knowledge base for content relevant to the query.
    Returns a formatted text block ready to insert into the prompt, or an
    empty string if nothing relevant enough was found (in which case the
    chatbot will just answer from its own general knowledge, same as
    Phase 1 did).
    """
    collection = _get_collection()
    results = collection.query(query_texts=[query], n_results=N_RESULTS)

    documents = results["documents"][0]
    distances = results["distances"][0]

    relevant = [
        doc for doc, dist in zip(documents, distances) if dist <= RELEVANCE_THRESHOLD
    ]

    if not relevant:
        return ""

    return "\n\n".join(relevant)
