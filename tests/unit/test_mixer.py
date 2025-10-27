"""Tests for mastering mixer module."""

import struct
import wave

from app.packages.mastering import mixer
from app.packages.tts import synthesizer


def test_apply_mock_normalization_limits_peak():
    frames = struct.pack("<hhh", 10_000, -32_000, 32_000)
    normalized = mixer.apply_mock_normalization(frames)

    values = [sample[0] for sample in struct.iter_unpack("<h", normalized)]
    assert max(abs(v) for v in values) <= 32767


def test_mix_stems_creates_output_wave(tmp_path):
    stems_dir = tmp_path / "stems"
    stems_dir.mkdir()
    host = synthesizer.load_hosts_config()[0]

    synthesizer.synthesize_text("Hello", host, stems_dir / "stem0.wav")
    synthesizer.synthesize_text("World", host, stems_dir / "stem1.wav")

    output = tmp_path / "mix.wav"
    mixer.mix_stems(stems_dir, output)

    assert output.exists()
    with wave.open(str(output), "rb") as wav:
        assert wav.getnframes() > 0