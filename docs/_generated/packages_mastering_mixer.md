# app.packages.mastering.mixer

Audio Mixer - Concatenates stems, applies mock crossfade, normalizes to -16 LUFS (mock)

## Members
- Path(*args, **kwargs)
- apply_mock_normalization(frames, target_db=-16)
- concatenate_frames(stems)
- mix_stems(stems_dir, output_path)
- read_wave(path)
- write_wave(path, params, frames)
