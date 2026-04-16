"""Text chunking for knowledge base ingestion."""


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    separator: str = "\n\n",
) -> list[str]:
    """Split text into overlapping chunks.

    Strategy:
    1. Split on paragraph boundaries first
    2. Merge small paragraphs into chunks up to chunk_size
    3. Maintain overlap between chunks for context continuity
    """
    if not text.strip():
        return []

    paragraphs = text.split(separator)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_length = 0

    for para in paragraphs:
        para_len = len(para)

        if current_length + para_len > chunk_size and current_chunk:
            chunks.append(separator.join(current_chunk))

            # Keep overlap
            overlap_text = ""
            overlap_parts: list[str] = []
            for part in reversed(current_chunk):
                if len(overlap_text) + len(part) <= chunk_overlap:
                    overlap_parts.insert(0, part)
                    overlap_text += part
                else:
                    break

            current_chunk = overlap_parts
            current_length = len(overlap_text)

        current_chunk.append(para)
        current_length += para_len

    if current_chunk:
        chunks.append(separator.join(current_chunk))

    # Handle case where single paragraph exceeds chunk_size
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > chunk_size * 2:
            # Force split on sentence boundaries
            sentences = chunk.replace(". ", ".\n").split("\n")
            sub_chunk = ""
            for sentence in sentences:
                if len(sub_chunk) + len(sentence) > chunk_size and sub_chunk:
                    final_chunks.append(sub_chunk.strip())
                    sub_chunk = sentence
                else:
                    sub_chunk += " " + sentence
            if sub_chunk.strip():
                final_chunks.append(sub_chunk.strip())
        else:
            final_chunks.append(chunk)

    return final_chunks
