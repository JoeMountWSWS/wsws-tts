from __future__ import annotations

import re


def chunk_paragraphs(paragraphs: list[str], *, max_chars: int = 900) -> list[str]:
    if max_chars < 200:
        raise ValueError("max_chars must be >= 200")

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    def flush() -> None:
        nonlocal current, current_len
        if current:
            chunks.append("\n\n".join(current).strip())
            current = []
            current_len = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If a single paragraph is too long, split by sentences.
        if len(para) > max_chars:
            flush()
            sentences = re.split(r"(?<=[.!?])\s+", para)
            buf = ""
            for s in sentences:
                if not s:
                    continue
                if not buf:
                    buf = s
                    continue
                if len(buf) + 1 + len(s) <= max_chars:
                    buf = f"{buf} {s}"
                else:
                    chunks.append(buf.strip())
                    buf = s
            if buf:
                chunks.append(buf.strip())
            continue

        add_len = len(para) + (2 if current else 0)
        if current_len + add_len > max_chars:
            flush()
        current.append(para)
        current_len += add_len

    flush()
    return [c for c in chunks if c]
