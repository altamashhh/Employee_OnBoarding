"""RAG service — store chunks, retrieve context, and query Gemini with conversation history."""

from collections import defaultdict

from google import genai

from core.config import settings
from db.chroma_client import get_or_create_collection
from services.embedding_service import get_query_embedding
from models.schemas import ChatResponse, SourceChunk

# ── In-memory conversation history per user ─────────────────
_history: dict[str, list[dict]] = defaultdict(list)

# ── Gemini client ───────────────────────────────────────────
_gemini_client: genai.Client | None = None


def _get_gemini_client() -> genai.Client:
    """Lazy-load the Gemini client."""
    global _gemini_client
    if _gemini_client is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set. Please add it to your .env file.")
        _gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _gemini_client


# ── Store chunks in ChromaDB ────────────────────────────────
def store_chunks(chunks: list[dict], embeddings: list[list[float]]) -> int:
    """Store document chunks with their embeddings in ChromaDB."""
    collection = get_or_create_collection()

    ids = [c["chunk_id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [{"filename": c["filename"], "chunk_id": c["chunk_id"]} for c in chunks]

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(chunks)


def get_uploaded_documents() -> list[str]:
    """Return a list of unique filenames stored in ChromaDB."""
    collection = get_or_create_collection()
    results = collection.get(include=["metadatas"])

    filenames = set()
    if results and results.get("metadatas"):
        for meta in results["metadatas"]:
            if meta and "filename" in meta:
                filenames.add(meta["filename"])

    return sorted(filenames)


# ── Retrieve relevant context ──────────────────────────────
def _retrieve_context(question: str) -> list[dict]:
    """Retrieve the top-K most relevant chunks for a question."""
    collection = get_or_create_collection()
    query_embedding = get_query_embedding(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=settings.TOP_K,
        include=["documents", "metadatas"],
    )

    context_chunks = []
    if results and results.get("documents") and results["documents"][0]:
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            context_chunks.append({
                "text": doc,
                "filename": meta.get("filename", "unknown"),
                "chunk_id": meta.get("chunk_id", "unknown"),
            })

    return context_chunks


# ── Conversation history helpers ────────────────────────────
def get_chat_history(user_id: str) -> list[dict]:
    """Return conversation history for a user."""
    return list(_history.get(user_id, []))


def clear_history(user_id: str) -> None:
    """Clear conversation history for a user."""
    _history.pop(user_id, None)


def _add_to_history(user_id: str, role: str, content: str) -> None:
    """Add a message to the user's conversation history."""
    _history[user_id].append({"role": role, "content": content})
    # Trim to max turns (each turn = 2 messages: user + assistant)
    max_messages = settings.MAX_HISTORY_TURNS * 2
    if len(_history[user_id]) > max_messages:
        _history[user_id] = _history[user_id][-max_messages:]


# ── Main query function ────────────────────────────────────
def query(question: str, user_id: str) -> ChatResponse:
    """RAG query: retrieve context, build prompt with history, call Gemini."""
    # Retrieve relevant document chunks
    context_chunks = _retrieve_context(question)

    # Build context string
    context_text = "\n\n---\n\n".join(
        f"[Source: {c['filename']}]\n{c['text']}" for c in context_chunks
    )

    # Build conversation history string
    history_text = ""
    user_history = _history.get(user_id, [])
    if user_history:
        history_lines = []
        for msg in user_history:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            history_lines.append(f"{role_label}: {msg['content']}")
        history_text = "\n".join(history_lines)

    # Build the prompt
    prompt = f"""You are an AI onboarding assistant for a company. Your job is to help new employees by answering their questions based on company documents.

Use the following context from company documents to answer the user's question. If the context doesn't contain enough information, say so honestly — do not make up information.

--- COMPANY DOCUMENTS CONTEXT ---
{context_text if context_text else "No relevant documents found."}
--- END CONTEXT ---
"""

    if history_text:
        prompt += f"""
--- CONVERSATION HISTORY ---
{history_text}
--- END HISTORY ---
"""

    prompt += f"""
User's Question: {question}

Please provide a helpful, accurate answer based on the company documents. If you reference specific information, mention which document it came from."""

    # Call Gemini
    try:
        client = _get_gemini_client()
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )
        answer = response.text or "I'm sorry, I couldn't generate a response."
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {e}")

    # Update conversation history
    _add_to_history(user_id, "user", question)
    _add_to_history(user_id, "assistant", answer)

    # Build source list
    sources = [
        SourceChunk(text=c["text"][:200], filename=c["filename"], chunk_id=c["chunk_id"])
        for c in context_chunks
    ]

    return ChatResponse(answer=answer, sources=sources)
