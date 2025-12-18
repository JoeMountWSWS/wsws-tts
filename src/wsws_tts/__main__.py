from __future__ import annotations

import argparse
import re
from pathlib import Path

from wsws_tts.audio import save_wav_pcm16
from wsws_tts.chunking import chunk_paragraphs
from wsws_tts.extract import ExtractionError, extract_wsws_article
from wsws_tts.tts import TTSConfig, synthesize_chunks_to_wav_tensor


def _safe_slug(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "article"


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="wsws-tts",
        description="Extract a WSWS (wsws.org/en) article and convert it to speech using Chatterbox.",
    )
    p.add_argument(
        "url", help="WSWS article URL (must start with https://www.wsws.org/en/)"
    )
    p.add_argument(
        "--out",
        default=None,
        help="Output WAV path (default: derived from article title)",
    )
    p.add_argument(
        "--model",
        default="chatterbox",
        choices=["chatterbox", "multilingual", "turbo"],
        help="Which Chatterbox model family to use",
    )
    p.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "cuda"],
        help="Device for inference",
    )
    p.add_argument(
        "--language-id",
        default=None,
        help="Language code for multilingual model (e.g., en, fr, zh). Only used with --model multilingual.",
    )
    p.add_argument(
        "--voice-ref",
        default=None,
        help="Reference audio clip (.wav) for Turbo voice cloning. Only used with --model turbo.",
    )
    p.add_argument(
        "--max-chars-per-chunk",
        type=int,
        default=900,
        help="Chunk size for long articles (smaller is safer but slower).",
    )
    p.add_argument(
        "--include-title",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include the article title as the first spoken line.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Extract and print text only; do not run TTS.",
    )
    return p


def main() -> None:
    args = build_argparser().parse_args()

    try:
        article = extract_wsws_article(args.url)
    except ExtractionError as e:
        raise SystemExit(f"Extraction failed: {e}")

    paragraphs = list(article.paragraphs)
    if args.include_title:
        meta_bits = [article.title]
        if article.authors:
            meta_bits.append("By " + ", ".join(article.authors))
        if article.published:
            meta_bits.append("Published " + str(article.published))
        paragraphs = [". ".join(meta_bits) + "."] + paragraphs

    if args.dry_run:
        print(f"Title: {article.title}")
        if article.authors:
            print("Authors: " + ", ".join(article.authors))
        if article.published:
            print(f"Published: {article.published}")
        print("\n" + "=" * 80 + "\n")
        print("\n\n".join(paragraphs))
        return

    out_path = Path(args.out) if args.out else Path(f"{_safe_slug(article.title)}.wav")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    chunks = chunk_paragraphs(paragraphs, max_chars=args.max_chars_per_chunk)
    print(
        f"Extracted {len(article.paragraphs)} paragraphs; synthesizing {len(chunks)} chunks..."
    )

    wav, sr = synthesize_chunks_to_wav_tensor(
        chunks,
        config=TTSConfig(
            model=args.model,
            device=args.device,
            language_id=args.language_id,
            voice_ref=args.voice_ref,
        ),
    )

    import torch

    save_wav_pcm16(
        out_path,
        audio=wav.detach().cpu().to(torch.float32).numpy(),
        sample_rate=sr,
    )
    print(f"Saved: {out_path.resolve()}")


if __name__ == "__main__":
    main()
