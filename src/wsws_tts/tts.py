from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ModelName = Literal["chatterbox", "multilingual", "turbo"]


@dataclass(frozen=True)
class TTSConfig:
    model: ModelName = "chatterbox"
    device: str = "auto"  # auto|cpu|cuda
    language_id: str | None = None  # multilingual only
    voice_ref: str | None = None  # turbo only


def resolve_device(device: str) -> str:
    import torch

    device = device.strip().lower()
    if device not in {"auto", "cpu", "cuda"}:
        raise ValueError("device must be one of: auto, cpu, cuda")
    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("--device cuda was requested but CUDA is not available")
    return device


def synthesize_chunks_to_wav_tensor(
    chunks: list[str],
    *,
    config: TTSConfig,
) -> tuple["torch.Tensor", int]:
    import torch

    device = resolve_device(config.device)
    model_name = config.model

    if model_name == "chatterbox":
        from chatterbox.tts import ChatterboxTTS

        model = ChatterboxTTS.from_pretrained(device=device)
        sr = int(model.sr)
        wavs = []
        for chunk in chunks:
            wav = model.generate(chunk)
            wavs.append(_ensure_2d(wav))
        return torch.cat(wavs, dim=-1), sr

    if model_name == "multilingual":
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS

        model = ChatterboxMultilingualTTS.from_pretrained(device=device)
        sr = int(model.sr)
        language_id = config.language_id or "en"
        wavs = []
        for chunk in chunks:
            wav = model.generate(chunk, language_id=language_id)
            wavs.append(_ensure_2d(wav))
        return torch.cat(wavs, dim=-1), sr

    if model_name == "turbo":
        from chatterbox.tts_turbo import ChatterboxTurboTTS

        if not config.voice_ref:
            raise ValueError("turbo model requires --voice-ref path to a reference WAV")
        model = ChatterboxTurboTTS.from_pretrained(device=device)
        sr = int(model.sr)
        wavs = []
        for chunk in chunks:
            wav = model.generate(chunk, audio_prompt_path=config.voice_ref)
            wavs.append(_ensure_2d(wav))
        return torch.cat(wavs, dim=-1), sr

    raise ValueError(f"Unknown model: {model_name}")


def _ensure_2d(wav: "torch.Tensor") -> "torch.Tensor":
    import torch

    if not isinstance(wav, torch.Tensor):
        wav = torch.as_tensor(wav)
    if wav.ndim == 1:
        return wav.unsqueeze(0)
    return wav
