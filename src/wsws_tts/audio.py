from __future__ import annotations

import wave
from pathlib import Path

import numpy as np


def save_wav_pcm16(path: str | Path, *, audio: "np.ndarray", sample_rate: int) -> None:
    """Save mono/stereo float audio to 16-bit PCM WAV.

    Expects audio shaped either (channels, time) or (time,). Values should be in [-1, 1].
    """

    path = Path(path)
    if audio.ndim == 1:
        audio = audio[None, :]
    if audio.ndim != 2:
        raise ValueError("audio must have shape (time,) or (channels, time)")

    channels, frames = audio.shape
    clipped = np.clip(audio, -1.0, 1.0)
    pcm = (clipped * 32767.0).astype(np.int16)

    # wave module expects interleaved samples (time, channels)
    interleaved = pcm.T.reshape(frames * channels)

    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(int(channels))
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(int(sample_rate))
        wf.writeframes(interleaved.tobytes())
