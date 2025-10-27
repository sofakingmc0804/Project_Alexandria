"""Adapters for Silero VAD integration.

This module isolates the Silero dependency so we can gracefully fall back
when the runtime environment does not have torch or the Silero weights
available.  The adapter exposes a tiny surface area used by the segmenter
so it is trivial to monkeypatch during unit tests.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class VadWindow:
    """Represents a speech window in milliseconds."""

    start_ms: float
    end_ms: float


class SileroVadAdapter:
    """Lazy loader around the official Silero VAD implementation.

    The adapter attempts to load the published torch hub weights on
    instantiation.  If torch or the weights are unavailable we keep the
    adapter disabled and let the caller fall back to transcript-based
    segmentation.  Consumers can check the ``enabled`` attribute to
    determine whether VAD is usable.
    """

    def __init__(self, device: str | None = None, repo: str | None = None) -> None:
        self.enabled = False
        self._error: Optional[str] = None
        self._device = device or os.environ.get("ALEXANDRIA_VAD_DEVICE", "cpu")
        self._repo = repo or os.environ.get("ALEXANDRIA_SILERO_REPO", "snakers4/silero-vad")
        self._model = None
        self._get_speech_timestamps = None
        self._torch = None

        try:
            import torch

            self._torch = torch
        except Exception as exc:  # pragma: no cover - exercised in environments without torch
            self._error = f"torch unavailable: {exc}"
            return

        try:
            # ``trust_repo=True`` avoids user prompts when the repo is already
            # available locally.  The first invocation still requires the
            # environment to have downloaded the weights ahead of time.
            model, utils = self._torch.hub.load(
                repo_or_dir=self._repo,
                model="silero_vad",
                source="github",
                trust_repo=True,
            )
            (get_speech_timestamps, *_) = utils
            self._model = model.to(self._device)
            self._get_speech_timestamps = get_speech_timestamps
            self.enabled = True
        except Exception as exc:  # pragma: no cover - depends on runtime env
            self._error = f"silero load failed: {exc}"
            self.enabled = False

    @property
    def error(self) -> Optional[str]:
        return self._error

    def detect(self, audio: "np.ndarray", sample_rate: int) -> List[VadWindow]:
        """Return speech windows (in milliseconds) for the given audio.

        Parameters
        ----------
        audio:
            1-D numpy array of PCM samples in float32 range [-1, 1].
        sample_rate:
            Sampling rate of the array, expected to be 16 kHz for Silero.
        """

        if not self.enabled or self._model is None or self._get_speech_timestamps is None:
            return []

        import numpy as np

        if sample_rate != 16000:
            # Silero expects 16 kHz.  Perform a simple resample using numpy.
            duration = audio.shape[0] / sample_rate
            target_indices = np.linspace(0, audio.shape[0] - 1, int(duration * 16000))
            audio = np.interp(target_indices, np.arange(audio.shape[0]), audio)
            sample_rate = 16000

        tensor = self._torch.from_numpy(audio).float()
        if tensor.ndim == 2:
            tensor = tensor.mean(dim=0)

        timestamps = self._get_speech_timestamps(
            tensor,
            self._model,
            sampling_rate=sample_rate,
        )

        windows: List[VadWindow] = []
        for ts in timestamps:
            start_ms = float(ts["start"]) / sample_rate * 1000.0
            end_ms = float(ts["end"]) / sample_rate * 1000.0
            windows.append(VadWindow(start_ms=start_ms, end_ms=end_ms))
        return windows


__all__ = ["SileroVadAdapter", "VadWindow"]
