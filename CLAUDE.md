# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

wsws-tts is a Python CLI tool that downloads articles from wsws.org, extracts their text, and converts them to speech using Resemble AI's Chatterbox TTS models.

## Development Commands

### Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip setuptools wheel
# Pre-install build dependencies (pkuseg has broken build isolation)
pip install 'numpy<2.0' Cython
# Install with --no-build-isolation due to pkuseg issue
pip install --no-build-isolation -e .
```

### Testing
```bash
pytest                    # Run all tests
pytest tests/test_chunking.py  # Run specific test file
pytest -v                 # Verbose output
```

### Running the CLI
```bash
wsws-tts "https://www.wsws.org/en/articles/..." --out article.wav
wsws-tts URL --dry-run    # Extract text only, no TTS
wsws-tts URL --model multilingual --language-id fr
wsws-tts URL --model turbo --voice-ref reference.wav
```

## Architecture

### Data Flow Pipeline

The application follows a linear pipeline:

1. **URL → HTML** (extract.py): Downloads WSWS article via requests
2. **HTML → Article** (extract.py): Extracts structured data from Next.js `__NEXT_DATA__` script tag
3. **Article → Chunks** (chunking.py): Splits paragraphs into TTS-friendly chunks
4. **Chunks → Audio** (tts.py): Synthesizes speech using Chatterbox models
5. **Audio → WAV** (audio.py): Saves as 16-bit PCM WAV file

### Key Modules

**extract.py**: WSWS-specific scraper
- Parses `__NEXT_DATA__` JSON embedded in WSWS pages
- Navigates structure: `props.pageProps.initialData.page.contentData`
- Recursively extracts text from nested element trees
- Handles element types: p, blockquote, h2, h3, li
- Returns `Article` dataclass with title, authors, published date, paragraphs

**chunking.py**: Text segmentation for TTS
- Combines paragraphs up to `max_chars` limit (default 900)
- Splits oversized paragraphs by sentence boundaries (`(?<=[.!?])\s+`)
- Critical for avoiding Chatterbox model context length issues

**tts.py**: TTS model abstraction layer
- Supports 3 Chatterbox model families: chatterbox (base), multilingual, turbo
- Auto-detects CUDA availability when device="auto"
- Concatenates chunk audio tensors with `torch.cat(wavs, dim=-1)`
- Returns tuple of (Tensor, sample_rate)

**audio.py**: WAV file I/O
- Converts float32 tensors in [-1, 1] to int16 PCM
- Handles both mono and stereo (channels, time) shaped arrays
- Uses Python stdlib `wave` module with interleaved samples

**cli.py**: Argument parsing and orchestration
- Derives output filename from article title via `_safe_slug()` if not specified
- Optionally prepends title/author/date as first spoken chunk
- `--dry-run` extracts text without running TTS (useful for debugging extraction)

### Important Constraints

- **WSWS URL format**: Must start with `https://www.wsws.org/en/`
- **Python version**: Requires >=3.10 (Chatterbox developed on 3.11)
- **PyTorch device**: CPU works but is slow; CUDA recommended for production use
- **Chunk size**: Default 900 chars balances quality and context limits; <200 raises ValueError

### Testing Strategy

Tests focus on core logic, not external dependencies:
- `test_extract.py`: Tests JSON parsing with mock HTML (no live HTTP)
- `test_chunking.py`: Verifies chunk size boundaries and paragraph grouping
- No TTS model tests (too slow, requires model downloads)
