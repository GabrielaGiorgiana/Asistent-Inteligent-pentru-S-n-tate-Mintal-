"""
Functii pentru interogarea bazei de cunostinte vectoriale (RAG).
"""
import chromadb
from google.genai import types

EMBED_DIM = 768  # trebuie sa fie identic cu cel folosit in build_kb.py

_chroma_client = chromadb.PersistentClient(path="./chroma_db")
_collection = _chroma_client.get_or_create_collection("mindcare_kb")


def retrieve_context(client_ai, query, n_results=3):
    """
    Primeste un client google-genai si o intrebare, returneaza un string
    cu cele mai relevante bucati de text din baza de cunostinte.
    """
    result = client_ai.models.embed_content(
        model="gemini-embedding-001",
        contents=query,
        config=types.EmbedContentConfig(output_dimensionality=EMBED_DIM)
    )
    query_embedding = result.embeddings[0].values

    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    documents = results.get("documents", [[]])[0]
    if not documents:
        return ""

    return "\n\n---\n\n".join(documents)
