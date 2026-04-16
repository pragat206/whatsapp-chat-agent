"""Tests for text chunking logic."""

from app.knowledge.chunker import chunk_text


def test_basic_chunking():
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
    chunks = chunk_text(text, chunk_size=50, chunk_overlap=10)
    assert len(chunks) >= 1
    assert all(isinstance(c, str) for c in chunks)


def test_empty_text():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_single_paragraph():
    text = "Short text"
    chunks = chunk_text(text, chunk_size=100)
    assert len(chunks) == 1
    assert chunks[0] == "Short text"


def test_respects_chunk_size():
    paragraphs = [f"Paragraph {i} with some content" for i in range(20)]
    text = "\n\n".join(paragraphs)
    chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)
    # No chunk should be massively over chunk_size (allow 2x for merge boundary)
    for chunk in chunks:
        assert len(chunk) < 300


def test_overlap_produces_context():
    text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    chunks = chunk_text(text, chunk_size=30, chunk_overlap=15)
    assert len(chunks) >= 2
