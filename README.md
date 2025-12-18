# WSWS Text-to-Speech

This tool reads articles from the *[World Socialist Web Site](https://wsws.org/)* by converting the text to audio files.

It is a command-line tool that:

1. Downloads an article from `https://www.wsws.org/en/...`
2. Extracts the article text (via the page’s embedded Next.js `__NEXT_DATA__` JSON)
3. Converts the text to speech using **Resemble AI’s** open-source **[Chatterbox](https://github.com/resemble-ai/chatterbox)** models

## Install

Python 3.11 is recommended (Chatterbox is developed/tested on 3.11), but versions newer than 3.10 generally work.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip setuptools wheel

# Pre-install build dependencies (required due to pkuseg build issue)
pip install 'numpy<2.0' Cython

# Install this project
pip install --no-build-isolation -e .
```

Notes:

- The `--no-build-isolation` flag is required due to a build issue in `pkuseg` (a transitive dependency)
- Chatterbox uses PyTorch; CPU works but is slow.
- If you have CUDA, install the appropriate `torch` wheels for your system.
- **First run**: The Transformers library will download Chatterbox models and data files (several GB). Subsequent runs use the cached models.

## Usage

Generate a WAV file from a WSWS article:

```bash
wsws-tts "https://www.wsws.org/en/articles/2025/12/18/sjdn-d18.html"
```

For a list of command-line options, please run `wsws-tts --help`.

Specify a filename:

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
