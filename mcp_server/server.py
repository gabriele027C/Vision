"""
Vision Knowledge Base — MCP Server

Exposes the Vision project knowledge base (books + specs) to Cursor.
Three tools:
  - search_vision_docs: semantic search across all manuals
  - get_module_spec: retrieve all chunks for a specific module/source
  - list_sources: list all available sources and categories
"""

import os
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

VECTOR_STORE_PATH = str(Path(r"C:\Users\Gabri\Vision\vector_store"))
COLLECTION_NAME = "vision_docs"

mcp = FastMCP(
    "vision-knowledge",
    instructions=(
        "This server provides access to the Vision project knowledge base. "
        "It contains trading theory books (Wyckoff, Coulling, De Prado, Murphy, etc.) "
        "and project specifications for the Vision crypto/stock monitoring system. "
        "Use search_vision_docs to find information about trading concepts, formulas, "
        "patterns, strategies, and implementation details."
    ),
)

_collection = None
_embedding_fn = None


def _load_env():
    env_file = Path(r"C:\Users\Gabri\Vision\.env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"')
                if k and v and not os.environ.get(k):
                    os.environ[k] = v


def _get_google_embedding_fn():
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


def get_collection():
    global _collection, _embedding_fn
    if _collection is not None:
        return _collection

    import chromadb

    _load_env()
    client = chromadb.PersistentClient(path=VECTOR_STORE_PATH)

    _embedding_fn = _get_google_embedding_fn()
    if _embedding_fn:
        _collection = client.get_collection(COLLECTION_NAME, embedding_function=_embedding_fn)
    else:
        _collection = client.get_collection(COLLECTION_NAME)

    return _collection


def rerank_chroma_query_results(results: dict, min_tokens: int = 120, penalty: float = 0.0012) -> dict:
    """Penalize very short chunks so dense passages rank above caption fragments."""
    if not results or not results.get("documents") or not results["documents"][0]:
        return results
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = list(results["distances"][0])
    n = len(docs)
    ids_list = list(results["ids"][0]) if results.get("ids") else None

    def adjusted(i: int) -> float:
        t = metas[i].get("tokens", 0)
        try:
            ti = int(t)
        except (TypeError, ValueError):
            ti = 0
        return dists[i] + max(0, min_tokens - ti) * penalty

    order = sorted(range(n), key=adjusted)
    out = dict(results)
    out["documents"] = [[docs[i] for i in order]]
    out["metadatas"] = [[metas[i] for i in order]]
    out["distances"] = [[dists[i] for i in order]]
    if ids_list is not None:
        out["ids"] = [[ids_list[i] for i in order]]
    return out


def format_results(results: dict) -> str:
    """Format ChromaDB results into readable text with citations."""
    if not results or not results.get("documents") or not results["documents"][0]:
        return "No results found."

    output = []
    for doc, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        relevance = max(0, 1 - distance)
        source = meta.get("source", "unknown")
        source_type = meta.get("source_type", "unknown")
        categories = meta.get("categories", "")
        page = meta.get("page", "?")
        page_end = meta.get("page_end", page)

        page_str = f"p.{page}" if page == page_end else f"pp.{page}-{page_end}"

        header = f"[{source} | {source_type} | {categories} | {page_str} | relevance: {relevance:.2f}]"
        output.append(f"{header}\n{doc}")

    return "\n\n---\n\n".join(output)


@mcp.tool()
def search_vision_docs(
    query: str,
    n_results: int = 5,
    source_type: str = "",
    category: str = "",
) -> str:
    """Search the Vision project knowledge base (trading books + project specs).

    Use this to find information about trading concepts, formulas, patterns,
    strategies, market microstructure, and Vision project specifications.

    Args:
        query: What you want to find (e.g. "how to recognize Wyckoff accumulation phase")
        n_results: Number of results to return (default 5, max 10)
        source_type: Filter by "theory" (books) or "spec" (project docs). Empty = all.
        category: Filter by category (e.g. "formula", "pattern", "strategy",
                  "volume", "market_microstructure", "architecture"). Empty = all.
    """
    collection = get_collection()
    n_results = min(max(n_results, 1), 10)

    where_filters = []
    if source_type:
        where_filters.append({"source_type": source_type})
    if category:
        where_filters.append({"categories": {"$contains": category}})

    where = None
    if len(where_filters) == 1:
        where = where_filters[0]
    elif len(where_filters) > 1:
        where = {"$and": where_filters}

    kwargs = {
        "query_texts": [query],
        "n_results": n_results,
    }
    if where:
        kwargs["where"] = where

    try:
        results = collection.query(**kwargs)
    except Exception:
        results = collection.query(query_texts=[query], n_results=n_results)

    results = rerank_chroma_query_results(results)
    return format_results(results)


@mcp.tool()
def get_module_spec(source_name: str, max_chunks: int = 20) -> str:
    """Get all chunks from a specific source document, ordered by page.

    Use this when you need the complete content of a specific book or spec document.

    Args:
        source_name: Part of the source filename (e.g. "wyckoff", "coulling", "murphy")
        max_chunks: Maximum chunks to return (default 20)
    """
    collection = get_collection()

    all_results = collection.get(
        where={"source": {"$contains": source_name}},
        include=["documents", "metadatas"],
    )

    if not all_results or not all_results["ids"]:
        results = collection.get(include=["metadatas"])
        sources = set()
        if results and results["metadatas"]:
            for m in results["metadatas"]:
                sources.add(m.get("source", ""))
        matching = [s for s in sources if source_name.lower() in s.lower()]
        if matching:
            all_results = collection.get(
                where={"source": matching[0]},
                include=["documents", "metadatas"],
            )
        else:
            available = "\n".join(f"  - {s}" for s in sorted(sources))
            return f"Source '{source_name}' not found.\n\nAvailable sources:\n{available}"

    pairs = list(zip(all_results["documents"], all_results["metadatas"]))
    pairs.sort(key=lambda x: (x[1].get("page", 0), x[1].get("chunk_index", 0)))
    pairs = pairs[:max_chunks]

    output = []
    for doc, meta in pairs:
        page = meta.get("page", "?")
        output.append(f"[Page {page}]\n{doc}")

    source = pairs[0][1].get("source", source_name) if pairs else source_name
    header = f"Source: {source} ({len(pairs)} chunks)\n{'='*60}\n\n"
    return header + "\n\n---\n\n".join(output)


@mcp.tool()
def list_sources() -> str:
    """List all available sources in the knowledge base with their metadata.

    Use this to discover what books and documents are available before searching.
    """
    collection = get_collection()
    results = collection.get(include=["metadatas"])

    if not results or not results["metadatas"]:
        return "Knowledge base is empty."

    sources = {}
    for meta in results["metadatas"]:
        source = meta.get("source", "unknown")
        if source not in sources:
            sources[source] = {
                "source_type": meta.get("source_type", "unknown"),
                "categories": set(),
                "chunks": 0,
            }
        sources[source]["chunks"] += 1
        for cat in meta.get("categories", "").split(","):
            if cat.strip():
                sources[source]["categories"].add(cat.strip())

    output = ["# Vision Knowledge Base Sources\n"]
    for source_type_label in ["theory", "spec"]:
        matching = {k: v for k, v in sources.items() if v["source_type"] == source_type_label}
        if not matching:
            continue
        output.append(f"\n## {source_type_label.upper()}\n")
        for source, info in sorted(matching.items()):
            cats = ", ".join(sorted(info["categories"]))
            output.append(f"- **{source}** ({info['chunks']} chunks) [{cats}]")

    total = sum(v["chunks"] for v in sources.values())
    output.append(f"\n\nTotal: {len(sources)} sources, {total} chunks")
    return "\n".join(output)


if __name__ == "__main__":
    mcp.run(transport="stdio")
