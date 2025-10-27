"""Generate deterministic test audio fixtures for Phase 1 testing."""

import wave
import struct
import math
from pathlib import Path


def generate_test_audio(output_path: Path, duration_sec: float = 5.0, sample_rate: int = 16000) -> None:
    """Generate a simple test audio file with a 440Hz sine wave (A4 note).
    
    Args:
        output_path: Path where WAV file will be saved
        duration_sec: Duration in seconds
        sample_rate: Sample rate in Hz
    """
    num_samples = int(duration_sec * sample_rate)
    frequency = 440.0  # A4 note
    
    # Generate samples
    samples = []
    for i in range(num_samples):
        # Generate sine wave
        t = i / sample_rate
        value = int(32767.0 * 0.5 * math.sin(2.0 * math.pi * frequency * t))
        samples.append(value)
    
    # Write WAV file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output_path), 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack('h' * len(samples), *samples))


if __name__ == "__main__":
    # Generate test fixtures
    fixtures_dir = Path(__file__).parent / "phase1_audio"
    fixtures_dir.mkdir(exist_ok=True)
    
    # Valid 16kHz mono WAV (ideal format)
    generate_test_audio(fixtures_dir / "test_valid_16k.wav", duration_sec=5.0, sample_rate=16000)
    
    # 44.1kHz WAV (needs normalization)
    generate_test_audio(fixtures_dir / "test_44k.wav", duration_sec=3.0, sample_rate=44100)
    
    # 8kHz WAV (low quality)
    generate_test_audio(fixtures_dir / "test_8k.wav", duration_sec=2.0, sample_rate=8000)
    
    print(f"✓ Generated test audio files in {fixtures_dir}")
