# wsws-tts

A small Python command-line tool that:

1. Downloads an article from `https://www.wsws.org/en/...`
2. Extracts the article text (via the page’s embedded Next.js `__NEXT_DATA__` JSON)
3. Converts the text to speech using **Resemble AI’s** open-source **Chatterbox** models

## Install

Python 3.11 is recommended (Chatterbox is developed/tested on 3.11), but `>=3.10` generally works.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip setuptools wheel

# install this project
pip install -e .
```

Notes:

- Chatterbox uses PyTorch; CPU works but is slow.
- If you have CUDA, install the appropriate `torch` wheels for your system.

## Usage

Generate a WAV file from a WSWS article:

```bash
wsws-tts "https://www.wsws.org/en/articles/2025/12/18/sjdn-d18.html" --out article.wav
```

Print extracted text (no TTS):

```bash
wsws-tts "https://www.wsws.org/en/articles/2025/12/18/sjdn-d18.html" --dry-run
```

Select model/device:

```bash
wsws-tts URL --model chatterbox --device auto
wsws-tts URL --model multilingual --language-id fr --out french.wav
```

Turbo voice-cloning (requires a reference clip):

```bash
wsws-tts URL --model turbo --voice-ref your_10s_ref_clip.wav --out turbo.wav
```

## CLI options (summary)

- `--out PATH`: output `.wav` path
- `--model chatterbox|multilingual|turbo`
- `--device auto|cpu|cuda`
- `--language-id`: only for multilingual
- `--voice-ref`: only for turbo (audio reference)
- `--max-chars-per-chunk`: chunk size for long articles

## Disclaimer

This tool is for personal / educational use. Respect WSWS.org terms of use and applicable copyright law.
