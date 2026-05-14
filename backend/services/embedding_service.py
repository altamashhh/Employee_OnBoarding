"""Embedding service — generate vector embeddings using Gemini text-embedding-004."""

from google import genai
from core.config import settings

_gemini_client: genai.Client | None = None

def _get_gemini_client() -> genai.Client:
    """Lazy-load the Gemini client."""
    global _gemini_client
    if _gemini_client is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set. Please add it to your .env file.")
        _gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _gemini_client


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of text strings."""
    client = _get_gemini_client()
    # Handle empty lists gracefully
    if not texts:
        return []
    
    # Gemini embed_content supports single strings or lists of strings
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=texts,
    )
    # Gemini returns a single embedding object if passed a single string,
    # or a list of embedding objects if passed a list. But the SDK might handle it differently.
    # Typically response.embeddings is a list of objects that have a .values attribute.
    if hasattr(response, 'embeddings') and isinstance(response.embeddings, list):
        return [e.values for e in response.embeddings]
    elif hasattr(response, 'embeddings'):
        # Just in case it returned a single embedding object directly under a different format
        return [response.embeddings.values]
    else:
        # Fallback if structure is slightly different
        return [response.values] if hasattr(response, 'values') else []


def get_query_embedding(text: str) -> list[float]:
    """Generate embedding for a single query string."""
    client = _get_gemini_client()
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
    )
    
    if hasattr(response, 'embeddings') and isinstance(response.embeddings, list):
        return response.embeddings[0].values
    elif hasattr(response, 'embeddings'):
        return response.embeddings.values
    else:
        return response.values if hasattr(response, 'values') else []
