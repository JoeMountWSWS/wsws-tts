# Contributing to wsws-tts

Thank you for your interest in contributing to wsws-tts! This document provides guidelines and instructions for setting up your development environment and contributing to the project.

## Development Environment Setup

### Prerequisites

- Python 3.10 or higher
- Git
- (Optional but recommended) CUDA-capable GPU for faster TTS processing

### Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wsws-tts.git
cd wsws-tts
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Upgrade pip and install build tools:
```bash
pip install -U pip setuptools wheel
```

4. Pre-install build dependencies:
```bash
# pkuseg has broken build isolation, so we need to install its dependencies first
pip install 'numpy<2.0' Cython
```

5. Install the package in editable mode with development dependencies:
```bash
pip install --no-build-isolation -e ".[dev]"
```

The `--no-build-isolation` flag is required due to a pkuseg build issue.

### Verify Installation

Test that the CLI works:
```bash
wsws-tts --help
```

## Development Workflow

### Code Style

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting. Before submitting a PR, ensure your code passes all checks:

```bash
# Check for linting issues
ruff check

# Auto-fix fixable issues
ruff check --fix

# Format code
ruff format
```

### Running Tests

Run the test suite with pytest:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_chunking.py

# Run with verbose output
pytest -v
```

Tests focus on core logic without external dependencies:
- `test_extract.py`: Tests JSON parsing with mock HTML (no live HTTP calls)
- `test_chunking.py`: Verifies chunk size boundaries and paragraph grouping
- No TTS model tests (too slow and requires model downloads)

### Testing Your Changes Manually

You can test the full pipeline with a real WSWS article:

```bash
# Dry run (extract text only, no TTS)
wsws-tts "https://www.wsws.org/en/articles/..." --dry-run

# Full run (generates audio)
wsws-tts "https://www.wsws.org/en/articles/..." --out test.wav

# Test different models
wsws-tts URL --model multilingual --language-id fr
wsws-tts URL --model turbo --voice-ref reference.wav
```

## Project Architecture

Understanding the codebase structure will help you contribute effectively:

### Data Flow Pipeline

The application follows a linear pipeline:

1. **URL → HTML** (`extract.py`): Downloads WSWS article
2. **HTML → Article** (`extract.py`): Extracts structured data from `__NEXT_DATA__` script tag
3. **Article → Chunks** (`chunking.py`): Splits paragraphs into TTS-friendly chunks
4. **Chunks → Audio** (`tts.py`): Synthesizes speech using Chatterbox models
5. **Audio → WAV** (`audio.py`): Saves as 16-bit PCM WAV file

### Key Modules

- **extract.py**: WSWS-specific HTML scraper
- **chunking.py**: Text segmentation for TTS (max 900 chars per chunk)
- **tts.py**: TTS model abstraction layer (supports chatterbox, multilingual, turbo)
- **audio.py**: WAV file I/O
- **cli.py**: Argument parsing and orchestration

See `CLAUDE.md` for detailed architecture documentation.

## Submitting Changes

### Before Submitting a PR

1. Ensure all tests pass: `pytest`
2. Ensure code is formatted: `ruff format .`
3. Ensure no linting issues: `ruff check .`
4. Add tests for new functionality
5. Update documentation if needed

### Pull Request Process

1. Fork the repository and create a new branch from `main`
2. Make your changes with clear, descriptive commit messages
3. Push your branch and open a pull request
4. Describe what your changes do and why they're needed
5. Link any related issues

### Commit Messages

Use clear, descriptive commit messages:
- Good: "Fix chunking bug with short paragraphs"
- Good: "Add support for multilingual model voice cloning"
- Bad: "fix bug"
- Bad: "updates"

## Reporting Issues

When reporting bugs, please include:
- Python version
- Operating system
- Full error message and stack trace
- Minimal reproduction steps
- WSWS article URL if relevant (for extraction issues)

## Questions?

If you have questions about contributing, feel free to open an issue for discussion.

## License

By contributing to wsws-tts, you agree that your contributions will be licensed under the same license as the project.
