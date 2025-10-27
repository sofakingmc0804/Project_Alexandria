"""Batch synthesizer orchestrating per-speaker waveform generation."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
	# Allow running as standalone script without installing the package
	sys.path.append(str(Path(__file__).resolve().parents[2]))
	from app.packages.tts import synthesizer  # type: ignore  # pragma: no cover
else:
	from . import synthesizer


def synthesize_batch(script_path: str, stems_dir: str, config_path: str = "configs/hosts.yaml") -> list[Path]:
	"""Generate WAV stems for the provided script."""

	generated = synthesizer.synthesize_script(Path(script_path), Path(stems_dir), config_path)
	print(f"Batch synthesis complete. {len(generated)} stems in {stems_dir}")
	return generated


if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage: python batch_synth.py <script.md> <stems_dir> [config.yaml]")
		sys.exit(1)

	config = sys.argv[3] if len(sys.argv) > 3 else "configs/hosts.yaml"
	synthesize_batch(sys.argv[1], sys.argv[2], config)
