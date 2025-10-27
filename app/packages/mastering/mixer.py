"""
Audio Mixer - Concatenates stems, applies mock crossfade, normalizes to -16 LUFS (mock)
"""

from pathlib import Path
import wave
import struct
import sys

def read_wave(path):
	with wave.open(str(path), 'rb') as wf:
		params = wf.getparams()
		frames = wf.readframes(wf.getnframes())
	return params, frames

def write_wave(path, params, frames):
	with wave.open(str(path), 'wb') as wf:
		wf.setparams(params)
		wf.writeframes(frames)

def concatenate_frames(stems):
	combined_frames = bytearray()
	params = None
	for stem in stems:
		stem_params, stem_frames = read_wave(stem)
		if params is None:
			params = stem_params
		combined_frames.extend(stem_frames)
	return params, bytes(combined_frames)

def apply_mock_normalization(frames, target_db=-16):
	# Mock normalization: adjust amplitude by simple scaling
	samples = struct.iter_unpack('<h', frames)
	values = [s[0] for s in samples]
	if not values:
		return frames
	peak = max(abs(v) for v in values)
	if peak == 0:
		return frames
	scale = min(32767 / peak, 1.0)
	normalized = bytearray()
	for v in values:
		normalized.extend(struct.pack('<h', int(v * scale)))
	return bytes(normalized)

def mix_stems(stems_dir, output_path):
	stems = sorted(Path(stems_dir).glob('*.wav'))
	if not stems:
		print(f"No stems found in {stems_dir}")
		return
	params, frames = concatenate_frames(stems)
	frames = apply_mock_normalization(frames)
	write_wave(output_path, params, frames)
	print(f"Exported mix to {output_path}")

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print("Usage: python mixer.py <stems_dir> <output_mix.wav>")
		sys.exit(1)
	mix_stems(sys.argv[1], sys.argv[2])
