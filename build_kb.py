"""
Script care citeste documentele din knowledge_base/, le imparte in bucati (chunks)
si creeaza o baza de date vectoriala locala cu ChromaDB.

Ruleaza o singura data (sau ori de cate ori adaugi/modifici documente):
    python build_kb.py
"""
import os
import toml
import chromadb
from google import genai
from google.genai import types

# citim cheia API direct din secrets.toml, fara sa pornim Streamlit
secrets = toml.load(".streamlit/secrets.toml")
client_ai = genai.Client(api_key=secrets["GOOGLE_API_KEY"])

CHUNK_SIZE = 500       # caractere per bucata
CHUNK_OVERLAP = 100    # suprapunere intre bucati, ca sa nu taiem ideile la mijloc
EMBED_DIM = 768        # dimensiunea vectorului (768 e un compromis bun cost/calitate)


def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += size - overlap
    return chunks


def build():
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    # stergem colectia veche daca exista, ca sa nu adaugam duplicate la fiecare rulare
    try:
        chroma_client.delete_collection("mindcare_kb")
    except Exception:
        pass
    collection = chroma_client.create_collection("mindcare_kb")

    kb_folder = "knowledge_base"
    doc_id = 0

    for filename in sorted(os.listdir(kb_folder)):
        if not filename.endswith(".txt"):
            continue

        with open(os.path.join(kb_folder, filename), encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text)

        for chunk in chunks:
            result = client_ai.models.embed_content(
                model="gemini-embedding-001",
                contents=chunk,
                config=types.EmbedContentConfig(output_dimensionality=EMBED_DIM)
            )
            embedding = result.embeddings[0].values

            collection.add(
                ids=[f"doc_{doc_id}"],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"source": filename}]
            )
            doc_id += 1

        print(f"Am procesat {filename}: {len(chunks)} bucati")

    print(f"\nGata! Baza de cunostinte are {doc_id} bucati de text, salvata in ./chroma_db")


if __name__ == "__main__":
    build()
