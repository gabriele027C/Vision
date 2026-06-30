"""
Step 3: Embed chunks and index them in ChromaDB.
Reads chunks from docs/chunks/all_chunks.json and creates a vector store.

Uses Google gemini-embedding-2 by default.
Set GOOGLE_API_KEY as environment variable or in a .env file at project root.

Supports resume: if the collection already has chunks, only indexes the remaining ones.
Use --fresh to force a full re-index from scratch.

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
MIN_INDEX_TOKENS = 120  # Omit micro-fragments that pollute semantic search

BATCH_SIZE = 20  # Google API limit per request
MAX_RETRIES = 5
RETRY_BASE_DELAY = 10  # seconds


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


def embed_with_retry(embedding_fn, documents):
    """Call embedding function with exponential backoff on transient errors."""
    for attempt in range(MAX_RETRIES):
        try:
            return embedding_fn(documents)
        except Exception as e:
            err_str = str(e)
            is_transient = any(code in err_str for code in ["429", "503", "500", "UNAVAILABLE", "rate"])
            if is_transient and attempt < MAX_RETRIES - 1:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                print(f"  [Retry {attempt+1}/{MAX_RETRIES}] {err_str[:80]}... waiting {delay}s", flush=True)
                time.sleep(delay)
            else:
                raise


def build_index(chunks: list[dict], use_local: bool = False, fresh: bool = False):
    import chromadb

    client = chromadb.PersistentClient(path=str(VECTOR_STORE_PATH))

    existing = [c.name for c in client.list_collections()]

    embedding_fn = None
    if not use_local:
        embedding_fn = get_google_embedding_fn()
        if embedding_fn:
            print("Using Google gemini-embedding-2")
        else:
            print("No GOOGLE_API_KEY found, falling back to local embeddings")

    # Resume logic: check what's already indexed
    already_indexed = set()
    if COLLECTION_NAME in existing and not fresh:
        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_fn if embedding_fn else None,
        )
        current_count = collection.count()
        if current_count > 0:
            existing_ids = collection.get(include=[])["ids"]
            already_indexed = set(existing_ids)
            print(f"Resuming: {len(already_indexed)} chunks already indexed, {len(chunks) - len(already_indexed)} remaining")
    elif COLLECTION_NAME in existing and fresh:
        print(f"Deleting existing collection '{COLLECTION_NAME}'...")
        client.delete_collection(COLLECTION_NAME)
        collection = None

    # Create collection if needed
    if COLLECTION_NAME not in existing or fresh:
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

    # Filter out already-indexed chunks
    if already_indexed:
        chunks_to_index = [c for c in chunks if c["id"] not in already_indexed]
    else:
        chunks_to_index = chunks

    def _chunk_tokens(c: dict) -> int:
        try:
            return int(c.get("tokens") or 0)
        except (TypeError, ValueError):
            return 0

    _before_skip = len(chunks_to_index)
    chunks_to_index = [c for c in chunks_to_index if _chunk_tokens(c) >= MIN_INDEX_TOKENS]
    _skipped = _before_skip - len(chunks_to_index)
    if _skipped:
        print(f"Skipping {_skipped} chunks with tokens < {MIN_INDEX_TOKENS} (not indexed)")

    if not chunks_to_index:
        print("All chunks already indexed. Nothing to do.")
        print(f"Collection '{COLLECTION_NAME}' has {collection.count()} chunks")
        return collection

    total = len(chunks)
    indexed_so_far = len(already_indexed)

    for start in range(0, len(chunks_to_index), BATCH_SIZE):
        end = min(start + BATCH_SIZE, len(chunks_to_index))
        batch = chunks_to_index[start:end]

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
            embeddings = embed_with_retry(embedding_fn, documents)
            collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
        else:
            collection.add(ids=ids, documents=documents, metadatas=metadatas)

        indexed_so_far += len(batch)
        print(f"  Indexed {indexed_so_far}/{total} chunks...", flush=True)

    print(f"\nCollection '{COLLECTION_NAME}' ready with {collection.count()} chunks")
    return collection


def main():
    load_env()

    if not CHUNKS_PATH.exists():
        print(f"Chunks file not found: {CHUNKS_PATH}")
        print("Run 02_chunk.py first!")
        sys.exit(1)

    use_local = os.environ.get("USE_LOCAL", "0") == "1"
    fresh = "--fresh" in sys.argv

    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks\n")

    VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
    build_index(chunks, use_local=use_local, fresh=fresh)

    print(f"\nVector store saved to: {VECTOR_STORE_PATH}")
    print("Done!")


if __name__ == "__main__":
    main()
