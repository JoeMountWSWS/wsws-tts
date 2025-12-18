from wsws_tts.chunking import chunk_paragraphs


def test_chunk_paragraphs_respects_limit():
    paragraphs = ["a" * 100, "b" * 100, "c" * 100]
    chunks = chunk_paragraphs(paragraphs, max_chars=220)
    assert len(chunks) == 2
    assert "a" in chunks[0] and "b" in chunks[0]
    assert "c" in chunks[1]
