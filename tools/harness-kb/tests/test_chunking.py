# tools/harness-kb/tests/test_chunking.py
from harness_kb.chunking import Chunk, chunk_markdown, count_tokens


def test_count_tokens_simple():
    assert count_tokens("hello world") == 2
    assert count_tokens("") == 0


def test_chunk_markdown_one_section():
    text = "# Title\n\n## Section A\n\nSome content here."
    chunks = chunk_markdown(text, "doc.md")
    assert len(chunks) == 1
    assert chunks[0].heading == "Section A"
    assert chunks[0].path == "doc.md"
    assert "Some content here." in chunks[0].text


def test_chunk_markdown_h3_under_h2():
    text = "## Section A\n\nIntro.\n\n### Sub A1\n\nDetail."
    chunks = chunk_markdown(text, "doc.md")
    headings = [c.heading for c in chunks]
    assert "Section A" in headings
    assert "Sub A1" in headings


def test_chunk_markdown_long_section_subsplit():
    body = "para. " * 1000  # ~1000 tokens
    text = f"## Big Section\n\n{body}"
    chunks = chunk_markdown(text, "doc.md", max_tokens=300, overlap_tokens=20)
    assert len(chunks) > 1
    for c in chunks:
        assert c.heading == "Big Section"
        assert c.token_count <= 320  # max + overlap tolerance


def test_chunk_markdown_no_headings_returns_one_chunk():
    text = "Just plain text with no headings.\n\nMore text."
    chunks = chunk_markdown(text, "doc.md")
    assert len(chunks) == 1
    assert chunks[0].heading == ""


def test_chunk_char_ranges_contiguous():
    text = "## A\n\nfirst.\n\n## B\n\nsecond."
    chunks = chunk_markdown(text, "doc.md")
    for c in chunks:
        assert c.char_end > c.char_start
        assert text[c.char_start:c.char_end] == c.text
