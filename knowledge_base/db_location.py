"""
Centralized location for the ChromaDB vector database folder.

This uses the system's temporary files directory rather than a path
inside the project's own source folder (e.g. knowledge_base/chroma_db).
That matters specifically for cloud deployment: on platforms like
Streamlit Community Cloud, the folder your source code lives in can have
restricted or unreliable write permissions -- fine for reading your code,
not guaranteed safe for a database actively writing files to itself at
runtime. This caused a real deployment failure (chromadb.errors.
InvalidCollectionException right after creating the collection) that
never showed up locally, since a local Windows filesystem has no such
restriction.

The system temp directory is explicitly designed to always be writable,
on any platform -- the standard, recommended place for exactly this kind
of regenerable data. It works identically whether running locally or
deployed, so build_vector_db.py, retriever.py, and streamlit_app.py all
import this same constant instead of each computing their own path.
"""

import os
import tempfile

CHROMA_DB_PATH = os.path.join(tempfile.gettempdir(), "cyberprep_chroma_db")
