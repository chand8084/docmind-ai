
import re


def split_into_chunks(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150
):
    """
    Split text into smaller chunks with overlap.
    """

    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "Overlap must be non-negative and smaller than chunk size."
        )

    text = re.sub(r"\s+", " ", text).strip()

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(start + chunk_size, text_length)

        # Try to end at a sentence or word boundary.
        if end < text_length:
            boundary = max(
                text.rfind(". ", start, end),
                text.rfind("? ", start, end),
                text.rfind("! ", start, end),
                text.rfind(" ", start, end)
            )

            if boundary > start:
                end = boundary + 1

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        next_start = end - overlap

        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


def create_document_chunks(
    pages: list,
    chunk_size: int = 1000,
    overlap: int = 150
):
    """
    Create chunks while preserving PDF page information.
    """

    document_chunks = []

    for page in pages:

        page_number = page["page_number"]
        page_text = page.get("text", "")

        chunks = split_into_chunks(
            page_text,
            chunk_size,
            overlap
        )

        for index, chunk_text in enumerate(chunks):

            document_chunks.append({
                "chunk_id": f"page_{page_number}_chunk_{index + 1}",
                "page_number": page_number,
                "text": chunk_text,
                "character_count": len(chunk_text)
            })

    return document_chunks
