"""Lightweight, testable mock TTS synthesizer used during development.

The real product will integrate F5-TTS and/or Piper. Until then we
generate deterministic sine-wave audio so the rest of the pipeline can
be exercised and verified by tests.
"""

from __future__ import annotations

import math
import os
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

import numpy as np
import yaml


DEFAULT_SAMPLE_RATE = 16_000
DEFAULT_AMPLITUDE = 16_000
DEFAULT_EMBED_DIM = 512
DEFAULT_CACHE_DIR = "tmp/voice_cache"


# Language-to-voice mapping for multilingual TTS support
# Maps ISO 639-1 language codes to default voice IDs
DEFAULT_VOICE_MAP = {
	'en': 'f5:en_male_01',
	'es': 'f5:es_male_01',
	'fr': 'f5:fr_male_01',
	'de': 'f5:de_male_01',
	'zh': 'f5:zh_male_01',
	'ja': 'f5:ja_male_01',
	'ko': 'f5:ko_male_01',
	'pt': 'f5:pt_male_01',
	'ru': 'f5:ru_male_01',
	'ar': 'f5:ar_male_01',
	'hi': 'f5:hi_male_01',
	'it': 'f5:it_male_01',
}


@dataclass(frozen=True)
class HostConfig:
	"""Normalized host configuration record."""

	id: str
	name: str
	voice: str
	fallback: str
	rate: float
	pitch: float
	seed: int
	language: str = "en"  # Language code for voice selection


def get_voice_for_language(base_voice: str, language: str) -> str:
	"""
	Get appropriate voice ID for a target language.
	
	Args:
		base_voice: Original voice ID (e.g., "f5:en_male_01")
		language: Target language code (e.g., "es", "fr")
		
	Returns:
		Language-appropriate voice ID (e.g., "f5:es_male_01")
	"""
	if language == "en" or language not in DEFAULT_VOICE_MAP:
		return base_voice
	
	# Extract voice characteristics from base voice
	# Format: "provider:lang_gender_number"
	parts = base_voice.split(":")
	if len(parts) != 2:
		return base_voice
	
	provider = parts[0]
	voice_parts = parts[1].split("_")
	
	if len(voice_parts) >= 3:
		# Has lang_gender_number format
		gender = voice_parts[1]  # male/female
		number = voice_parts[2]  # 01, 02, etc.
		return f"{provider}:{language}_{gender}_{number}"
	
	# Use default for language
	return DEFAULT_VOICE_MAP.get(language, base_voice)


def load_hosts_config(config_path: str = "configs/hosts.yaml") -> list[HostConfig]:
	"""Load host configuration file and return normalized HostConfig list."""

	with open(config_path, "r", encoding="utf-8") as handle:
		raw = yaml.safe_load(handle)

	# Get default language from config
	default_language = raw.get("language", "en")

	hosts: list[HostConfig] = []
	for entry in raw.get("hosts", []):
		hosts.append(
			HostConfig(
				id=entry["id"],
				name=entry["name"],
				voice=entry.get("voice", "f5:en_male_01"),
				fallback=entry.get("fallback", ""),
				rate=float(entry.get("rate", 1.0)),
				pitch=float(entry.get("pitch", 0.0)),
				seed=int(entry.get("seed", 42)),
				language=entry.get("language", default_language),
			)
		)
	return hosts


def cache_voice_embedding(host: HostConfig, cache_dir: str | Path | None = None) -> Path:
	"""Persist deterministic mock voice embedding for repeatability.

	When ``cache_dir`` is ``None`` the location defaults to the
	``ALEXANDRIA_VOICE_CACHE_DIR`` environment variable or
	``tmp/voice_cache`` if unset. Tests can override via env without
	touching the repository tree.
	"""

	base_dir = Path(cache_dir) if cache_dir is not None else Path(os.environ.get("ALEXANDRIA_VOICE_CACHE_DIR", DEFAULT_CACHE_DIR))
	base_dir.mkdir(parents=True, exist_ok=True)
	target = base_dir / f"{host.id}_{host.seed}.npy"

	if not target.exists():
		rng = np.random.default_rng(host.seed)
		embedding = rng.normal(0, 1, DEFAULT_EMBED_DIM).astype(np.float32)
		np.save(target, embedding)
	return target


def _generate_samples(text: str, host: HostConfig) -> Iterator[int]:
	"""Yield 16-bit PCM samples representing a deterministic sine wave."""

	duration_seconds = max(1.0, len(text) / 20.0) / host.rate
	total_samples = int(duration_seconds * DEFAULT_SAMPLE_RATE)
	freq = 220 + (host.seed % 400) + host.pitch * 10
	angular_freq = 2 * math.pi * freq / DEFAULT_SAMPLE_RATE

	for i in range(total_samples):
		sample = math.sin(i * angular_freq)
		yield int(DEFAULT_AMPLITUDE * sample)


def synthesize_text(text: str, host: HostConfig, output_path: Path) -> Path:
	"""Synthesize text for a host into ``output_path``.

	The resulting waveform is deterministic for the (text, host) pair so
	tests can assert byte identity.
	"""

	cache_voice_embedding(host)  # ensure cache exists even if unused yet
	samples = list(_generate_samples(text, host))

	with wave.open(str(output_path), "wb") as wav:
		wav.setnchannels(1)
		wav.setsampwidth(2)
		wav.setframerate(DEFAULT_SAMPLE_RATE)
		# Convert to bytes in a single write for speed
		wav.writeframes(np.array(samples, dtype=np.int16).tobytes())
	return output_path


def parse_script_lines(script_path: Path) -> Iterable[tuple[str, str]]:
	"""Yield (speaker, text) pairs from a script markdown file."""

	with open(script_path, "r", encoding="utf-8") as handle:
		for raw_line in handle:
			line = raw_line.strip()
			if not line or line.startswith("#"):
				continue
			if ":" in line:
				speaker, text = line.split(":", 1)
				yield speaker.strip(), text.strip()
			else:
				yield "Narrator", line


def select_host(hosts: list[HostConfig], speaker: str) -> HostConfig:
	"""Return best host match for a speaker label."""

	speaker_lower = speaker.lower()
	for host in hosts:
		if host.name.lower() in speaker_lower or host.id.lower() in speaker_lower:
			return host
	return hosts[0]


def synthesize_script(script_path: Path, output_dir: Path, config_path: str = "configs/hosts.yaml", target_language: str | None = None) -> list[Path]:
	"""Synthesize every utterance in ``script_path`` into ``output_dir``.
	
	Args:
		script_path: Path to script markdown file
		output_dir: Directory for output audio files
		config_path: Path to hosts configuration
		target_language: Optional language code for multilingual synthesis
		
	Returns list of generated file paths for convenience/testing.
	"""

	hosts = load_hosts_config(config_path)
	if not hosts:
		raise ValueError("No hosts defined in hosts.yaml")

	# Apply language override if provided
	if target_language:
		hosts = [
			HostConfig(
				id=h.id,
				name=h.name,
				voice=get_voice_for_language(h.voice, target_language),
				fallback=h.fallback,
				rate=h.rate,
				pitch=h.pitch,
				seed=h.seed,
				language=target_language,
			)
			for h in hosts
		]

	output_dir.mkdir(parents=True, exist_ok=True)
	generated: list[Path] = []

	for speaker, text in parse_script_lines(script_path):
		host = select_host(hosts, speaker)
		filename = f"{host.id}_{host.seed}_{abs(hash(text)) % 10_000}.wav"
		path = output_dir / filename
		generated.append(synthesize_text(text, host, path))

	return generated


def main(script_path: str, out_dir: str, config_path: str = "configs/hosts.yaml") -> None:
	synthesize_script(Path(script_path), Path(out_dir), config_path)
	print(f"Synthesized lines to {out_dir}")


if __name__ == "__main__":
	import sys

	if len(sys.argv) < 3:
		print("Usage: python synthesizer.py <script.md> <output_dir> [config.yaml]")
		sys.exit(1)

	cfg = sys.argv[3] if len(sys.argv) > 3 else "configs/hosts.yaml"
	main(sys.argv[1], sys.argv[2], cfg)
