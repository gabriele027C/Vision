"""
Step 3: Embed chunks and index them in ChromaDB.
Reads chunks from docs/chunks/all_chunks.json and creates a vector store.

Uses Google text-embedding-004 by default.
Set GOOGLE_API_KEY as environment variable or in a .env file at project root.

Fallback: set USE_LOCAL=1 to use ChromaDB's built-in embeddings (no API key needed).
"""

import json
import os
import sys
import time
from pathlib import Path

CHUNKS_PATH = Path(r"C:\Users\Gabri\Vision\docs\chunks\all_chunks.json")
VECTOR_STORE_PATH = Path(r"C:\Users\Gabri\Vision\vector_store")
COLLECTION_NAME = "vision_docs"

BATCH_SIZE = 20  # Google API limit per request


def load_env():
    env_file = Path(r"C:\Users\Gabri\Vision\.env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"')
                if k and v and not os.environ.get(k):
                    os.environ[k] = v


def load_chunks() -> list[dict]:
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_google_embedding_fn():
    from google import genai
    from google.genai.types import Content, Part

    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key or "INSERISCI" in api_key:
        return None

    client = genai.Client(api_key=api_key)

    class GoogleEmbeddingFunction:
        def name(self):
            return "google-gemini-embedding-2"

        def _embed(self, texts: list[str]) -> list[list[float]]:
            contents = [Content(parts=[Part(text=t)]) for t in texts]
            response = client.models.embed_content(
                model="gemini-embedding-2",
                contents=contents,
            )
            return [e.values for e in response.embeddings]

        def __call__(self, input: list[str]) -> list[list[float]]:
            return self._embed(input)

        def embed_documents(self, input: list[str]) -> list[list[float]]:
            return self._embed(input)

        def embed_query(self, input):
            if isinstance(input, list):
                return self._embed(input)
            return self._embed([input])

    return GoogleEmbeddingFunction()


def build_index(chunks: list[dict], use_local: bool = False):
    import chromadb

    client = chromadb.PersistentClient(path=str(VECTOR_STORE_PATH))

    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        print(f"Deleting existing collection '{COLLECTION_NAME}'...")
        client.delete_collection(COLLECTION_NAME)

    embedding_fn = None
    if not use_local:
        embedding_fn = get_google_embedding_fn()
        if embedding_fn:
            print("Using Google gemini-embedding-2")
        else:
            print("No GOOGLE_API_KEY found, falling back to local embeddings")

    if embedding_fn:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )
    else:
        print("Using ChromaDB default embeddings (all-MiniLM-L6-v2)")
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    total = len(chunks)
    for start in range(0, total, BATCH_SIZE):
        end = min(start + BATCH_SIZE, total)
        batch = chunks[start:end]

        ids = [c["id"] for c in batch]
        documents = [c["text"] for c in batch]
        metadatas = []
        for c in batch:
            metadatas.append({
                "source": c["source"],
                "source_type": c["source_type"],
                "categories": ",".join(c["categories"]),
                "page": c["page"],
                "page_end": c.get("page_end", c["page"]),
                "chunk_index": c["chunk_index"],
                "total_chunks": c["total_chunks"],
                "tokens": c["tokens"],
            })

        if embedding_fn:
            try:
                embeddings = embedding_fn(documents)
            except Exception as e:
                if "429" in str(e) or "rate" in str(e).lower():
                    print(f"  Rate limited, waiting 60s...", flush=True)
                    time.sleep(60)
                    embeddings = embedding_fn(documents)
                else:
                    raise
            collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
        else:
            collection.add(ids=ids, documents=documents, metadatas=metadatas)

        print(f"  Indexed {end}/{total} chunks...", flush=True)

    print(f"\nCollection '{COLLECTION_NAME}' created with {collection.count()} chunks")
    return collection


def main():
    load_env()

    if not CHUNKS_PATH.exists():
        print(f"Chunks file not found: {CHUNKS_PATH}")
        print("Run 02_chunk.py first!")
        sys.exit(1)

    use_local = os.environ.get("USE_LOCAL", "0") == "1"

    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks\n")

    VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
    build_index(chunks, use_local=use_local)

    print(f"\nVector store saved to: {VECTOR_STORE_PATH}")
    print("Done!")


if __name__ == "__main__":
    main()
