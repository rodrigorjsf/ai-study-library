# tools/harness-kb/src/harness_kb/chunking.py
from __future__ import annotations
import re
from dataclasses import dataclass


@dataclass
class Chunk:
    path: str
    heading: str
    char_start: int
    char_end: int
    token_count: int
    text: str


_WORD_RE = re.compile(r"\w+", re.UNICODE)


def count_tokens(text: str) -> int:
    return len(_WORD_RE.findall(text))


def _find_headings(text: str) -> list[tuple[int, int, str]]:
    """Return [(start_offset, level, heading_text)] for H2/H3 headings."""
    out = []
    for m in re.finditer(r"^(#{2,3})\s+(.+?)\s*$", text, re.MULTILINE):
        out.append((m.start(), len(m.group(1)), m.group(2).strip()))
    return out


def _split_long_paragraph(
    para: str, base_offset: int, max_tokens: int, overlap_tokens: int
) -> list[tuple[int, int, str]]:
    """Split a single long paragraph at word boundaries."""
    words = para.split()
    out = []
    cur_buf: list[str] = []
    cur_token_count = 0
    cur_start = 0

    for word in words:
        wtokens = count_tokens(word)
        if cur_token_count + wtokens > max_tokens and cur_buf:
            chunk_text = " ".join(cur_buf)
            chunk_start = base_offset + para.find(chunk_text, cur_start)
            chunk_end = chunk_start + len(chunk_text)
            out.append((chunk_start, chunk_end, chunk_text))
            # overlap: keep last words whose token count sums to ~overlap_tokens
            kept: list[str] = []
            kept_tokens = 0
            for w in reversed(cur_buf):
                if kept_tokens >= overlap_tokens:
                    break
                kept.insert(0, w)
                kept_tokens += count_tokens(w)
            cur_buf = kept[:]
            cur_token_count = kept_tokens
            cur_start = chunk_end - base_offset
        cur_buf.append(word)
        cur_token_count += wtokens

    if cur_buf:
        chunk_text = " ".join(cur_buf)
        chunk_start = base_offset + para.find(chunk_text, cur_start)
        chunk_end = chunk_start + len(chunk_text)
        out.append((chunk_start, chunk_end, chunk_text))

    return out


def _split_long_section(
    text: str, base_offset: int, max_tokens: int, overlap_tokens: int
) -> list[tuple[int, int, str]]:
    """Split a section's body at paragraph boundaries; return [(start, end, text)]."""
    paragraphs = re.split(r"\n\s*\n", text)
    out = []
    cur_para_buf: list[str] = []
    cur_token_count = 0
    cur_start = 0

    for para in paragraphs:
        ptokens = count_tokens(para)
        # If adding this paragraph would exceed max_tokens and we have content buffered
        if cur_token_count + ptokens > max_tokens and cur_para_buf:
            chunk_text = "\n\n".join(cur_para_buf)
            chunk_start = base_offset + text.find(chunk_text, cur_start)
            chunk_end = chunk_start + len(chunk_text)
            out.append((chunk_start, chunk_end, chunk_text))
            # overlap: keep last paragraphs whose token count sums up to ~overlap_tokens
            kept: list[str] = []
            kept_tokens = 0
            for p in reversed(cur_para_buf):
                if kept_tokens >= overlap_tokens:
                    break
                kept.insert(0, p)
                kept_tokens += count_tokens(p)
            cur_para_buf = kept[:]
            cur_token_count = kept_tokens
            cur_start = chunk_end - base_offset

        # If this single paragraph exceeds max_tokens, split it at word boundaries
        if ptokens > max_tokens:
            # First, add any buffered paragraphs if not empty
            if cur_para_buf:
                chunk_text = "\n\n".join(cur_para_buf)
                chunk_start = base_offset + text.find(chunk_text, cur_start)
                chunk_end = chunk_start + len(chunk_text)
                out.append((chunk_start, chunk_end, chunk_text))
                cur_para_buf = []
                cur_token_count = 0
                cur_start = text.find(para, cur_start)
            # Split the long paragraph
            sub = _split_long_paragraph(para, base_offset + text.find(para, cur_start), max_tokens, overlap_tokens)
            out.extend(sub)
            cur_start = text.find(para, cur_start) + len(para)
        else:
            cur_para_buf.append(para)
            cur_token_count += ptokens

    if cur_para_buf:
        chunk_text = "\n\n".join(cur_para_buf)
        chunk_start = base_offset + text.find(chunk_text, cur_start)
        chunk_end = chunk_start + len(chunk_text)
        out.append((chunk_start, chunk_end, chunk_text))

    return out


def chunk_markdown(
    text: str, path: str, max_tokens: int = 800, overlap_tokens: int = 50
) -> list[Chunk]:
    headings = _find_headings(text)

    if not headings:
        return [Chunk(
            path=path, heading="", char_start=0, char_end=len(text),
            token_count=count_tokens(text), text=text,
        )]

    chunks: list[Chunk] = []
    for i, (h_start, _level, h_text) in enumerate(headings):
        next_start = headings[i + 1][0] if i + 1 < len(headings) else len(text)
        # body of this heading = text from end-of-heading-line through next heading
        line_end = text.find("\n", h_start)
        if line_end < 0:
            line_end = h_start
        body_start = line_end + 1
        body = text[body_start:next_start]
        body_tokens = count_tokens(body)

        if body_tokens <= max_tokens:
            chunks.append(Chunk(
                path=path,
                heading=h_text,
                char_start=h_start,
                char_end=next_start,
                token_count=count_tokens(text[h_start:next_start]),
                text=text[h_start:next_start],
            ))
        else:
            # split body, keep heading prepended on first sub-chunk
            sub = _split_long_section(body, body_start, max_tokens, overlap_tokens)
            for j, (s, e, t) in enumerate(sub):
                if j == 0:
                    full_start = h_start
                    full_text = text[h_start:e]
                else:
                    full_start = s
                    full_text = t
                chunks.append(Chunk(
                    path=path,
                    heading=h_text,
                    char_start=full_start,
                    char_end=e,
                    token_count=count_tokens(full_text),
                    text=full_text,
                ))
    return chunks
