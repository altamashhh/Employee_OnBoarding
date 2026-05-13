"""Document loader — extract text from PDF/DOCX and chunk it."""

import io
from pypdf import PdfReader
from docx import Document

from core.config import settings


def extract_text(filename: str, file_bytes: bytes) -> str:
    """Extract raw text from a PDF or DOCX file."""
    ext = filename.rsplit(".", 1)[-1].lower()

    if ext == "pdf":
        return _extract_pdf(file_bytes)
    elif ext in ("docx", "doc"):
        return _extract_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: .{ext}")


def _extract_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes."""
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def _extract_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX bytes."""
    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def chunk_text(text: str, filename: str) -> list[dict]:
    """Split text into overlapping chunks with metadata."""
    chunk_size = settings.CHUNK_SIZE
    overlap = settings.CHUNK_OVERLAP
    chunks = []
    start = 0
    chunk_index = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append({
                "text": chunk.strip(),
                "filename": filename,
                "chunk_id": f"{filename}_chunk_{chunk_index}",
            })
            chunk_index += 1

        start += chunk_size - overlap

    return chunks
