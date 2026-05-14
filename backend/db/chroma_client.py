"""Singleton ChromaDB persistent client and collection helper."""

from core.config import settings

_client = None


def get_chroma_client():
    """Return a singleton persistent ChromaDB client."""
    global _client
    if _client is None:
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        _client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client


def get_or_create_collection():
    """Get (or create) the main document collection."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )

