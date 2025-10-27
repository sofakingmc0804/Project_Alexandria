#!/usr/bin/env python3
"""Unit tests for audio normalizer (Phase 1).

Tests audio normalization to 16kHz mono WAV format.
Mocks subprocess calls to avoid ffmpeg dependency.
"""

import json
import pytest
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from app.packages.ingest import normalizer


@pytest.fixture
def temp_audio_file(tmp_path):
    """Create a temporary mock audio file."""
    audio_file = tmp_path / "test_audio.mp3"
    audio_file.write_bytes(b"fake audio data" * 100)
    return audio_file


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def job_directory_with_manifest(tmp_path, temp_audio_file):
    """Create a job directory with valid manifest.json."""
    job_dir = tmp_path / "job_001"
    job_dir.mkdir()
    
    manifest = {
        "job_id": "job_001",
        "input_file": {
            "path": str(temp_audio_file),
            "format": "mp3",
            "size_bytes": temp_audio_file.stat().st_size
        },
        "pipeline_stage": "validated"
    }
    
    manifest_path = job_dir / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    return job_dir


class TestGetFfmpegCommand:
    """Tests for get_ffmpeg_command() platform detection."""
    
    def test_returns_wsl_on_windows_when_enabled(self, monkeypatch):
        """Should return 'wsl' on Windows when USE_WSL_AUDIO is true."""
        monkeypatch.setattr('sys.platform', 'win32')
        monkeypatch.setenv('USE_WSL_AUDIO', 'true')
        
        # Re-import to pick up environment changes
        import importlib
        importlib.reload(normalizer)
        
        result = normalizer.get_ffmpeg_command()
        assert result == 'wsl'
    
    def test_returns_ffmpeg_on_linux(self, monkeypatch):
        """Should return 'ffmpeg' on non-Windows platforms."""
        monkeypatch.setattr('sys.platform', 'linux')
        monkeypatch.setenv('USE_WSL_AUDIO', 'true')
        
        import importlib
        importlib.reload(normalizer)
        
        result = normalizer.get_ffmpeg_command()
        assert result == 'ffmpeg'
    
    def test_returns_ffmpeg_when_wsl_disabled(self, monkeypatch):
        """Should return 'ffmpeg' when USE_WSL_AUDIO is false."""
        monkeypatch.setattr('sys.platform', 'win32')
        monkeypatch.setenv('USE_WSL_AUDIO', 'false')
        
        import importlib
        importlib.reload(normalizer)
        
        result = normalizer.get_ffmpeg_command()
        assert result == 'ffmpeg'


class TestNormalizeAudio:
    """Tests for normalize_audio() function."""
    
    @patch('subprocess.run')
    def test_normalize_audio_success(self, mock_run, temp_audio_file, temp_output_dir):
        """Should successfully normalize audio and return True."""
        output_file = temp_output_dir / "output.wav"
        
        # Mock successful ffmpeg execution
        mock_run.return_value = Mock(returncode=0, stderr="")
        
        # Create fake output file to simulate ffmpeg output
        output_file.write_bytes(b"fake wav data" * 1000)
        
        result = normalizer.normalize_audio(temp_audio_file, output_file)
        
        assert result is True
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_normalize_audio_ffmpeg_failure(self, mock_run, temp_audio_file, temp_output_dir):
        """Should return False when ffmpeg returns non-zero exit code."""
        output_file = temp_output_dir / "output.wav"
        
        # Mock failed ffmpeg execution
        mock_run.return_value = Mock(returncode=1, stderr="ffmpeg: error processing audio")
        
        result = normalizer.normalize_audio(temp_audio_file, output_file)
        
        assert result is False
    
    @patch('subprocess.run')
    def test_normalize_audio_creates_output_directory(self, mock_run, temp_audio_file, tmp_path):
        """Should create output directory if it doesn't exist."""
        output_file = tmp_path / "nested" / "dirs" / "output.wav"
        
        mock_run.return_value = Mock(returncode=0, stderr="")
        
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'stat') as mock_stat:
                mock_stat.return_value.st_size = 128000
                normalizer.normalize_audio(temp_audio_file, output_file)
        
        assert output_file.parent.exists()
    
    @patch('subprocess.run')
    def test_normalize_audio_with_custom_sample_rate(self, mock_run, temp_audio_file, temp_output_dir):
        """Should use custom sample rate when specified."""
        output_file = temp_output_dir / "output.wav"
        
        mock_run.return_value = Mock(returncode=0, stderr="")
        
        # Create fake output file
        output_file.write_bytes(b"fake wav data" * 1000)
        
        normalizer.normalize_audio(temp_audio_file, output_file, sample_rate=48000)
        
        # Verify sample rate in command
        call_args = mock_run.call_args[0][0]
        assert '48000' in ' '.join(str(arg) for arg in call_args)
    
    @patch('subprocess.run')
    def test_normalize_audio_output_not_created(self, mock_run, temp_audio_file, temp_output_dir):
        """Should return False if output file doesn't exist after ffmpeg."""
        output_file = temp_output_dir / "output.wav"
        
        mock_run.return_value = Mock(returncode=0, stderr="")
        
        # Simulate output file not being created
        with patch.object(Path, 'exists', return_value=False):
            result = normalizer.normalize_audio(temp_audio_file, output_file)
        
        assert result is False
    
    @patch('subprocess.run')
    def test_normalize_audio_ffmpeg_not_found(self, mock_run, temp_audio_file, temp_output_dir):
        """Should return False when ffmpeg is not installed."""
        output_file = temp_output_dir / "output.wav"
        
        # Simulate ffmpeg not found
        mock_run.side_effect = FileNotFoundError("ffmpeg not found")
        
        result = normalizer.normalize_audio(temp_audio_file, output_file)
        
        assert result is False
    
    @patch('subprocess.run')
    def test_normalize_audio_unexpected_error(self, mock_run, temp_audio_file, temp_output_dir):
        """Should return False on unexpected exceptions."""
        output_file = temp_output_dir / "output.wav"
        
        # Simulate unexpected error
        mock_run.side_effect = Exception("Unexpected error")
        
        result = normalizer.normalize_audio(temp_audio_file, output_file)
        
        assert result is False


class TestProcessJob:
    """Tests for process_job() function."""
    
    @patch('app.packages.ingest.normalizer.normalize_audio')
    def test_process_job_success(self, mock_normalize, job_directory_with_manifest):
        """Should successfully process job and update manifest."""
        mock_normalize.return_value = True
        
        # Create the expected output file
        normalized_dir = job_directory_with_manifest / "normalized"
        normalized_dir.mkdir()
        output_file = normalized_dir / "test_audio_normalized.wav"
        output_file.write_bytes(b"normalized audio data" * 100)
        
        result = normalizer.process_job(job_directory_with_manifest)
        
        assert result is True
        
        # Verify manifest was updated
        manifest_path = job_directory_with_manifest / "manifest.json"
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        assert manifest['pipeline_stage'] == 'normalized'
        assert 'normalized_audio' in manifest
        assert manifest['normalized_audio']['sample_rate'] == 16000
        assert manifest['normalized_audio']['channels'] == 1
        assert manifest['normalized_audio']['format'] == 'wav'
    
    @patch('app.packages.ingest.normalizer.normalize_audio')
    def test_process_job_custom_sample_rate(self, mock_normalize, job_directory_with_manifest):
        """Should use custom sample rate when specified."""
        mock_normalize.return_value = True
        
        normalized_dir = job_directory_with_manifest / "normalized"
        normalized_dir.mkdir()
        output_file = normalized_dir / "test_audio_normalized.wav"
        output_file.write_bytes(b"normalized audio data" * 100)
        
        normalizer.process_job(job_directory_with_manifest, sample_rate=48000)
        
        # Verify sample rate in manifest
        manifest_path = job_directory_with_manifest / "manifest.json"
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        assert manifest['normalized_audio']['sample_rate'] == 48000
    
    def test_process_job_missing_manifest(self, tmp_path):
        """Should return False when manifest.json doesn't exist."""
        job_dir = tmp_path / "job_no_manifest"
        job_dir.mkdir()
        
        result = normalizer.process_job(job_dir)
        
        assert result is False
    
    @patch('app.packages.ingest.normalizer.normalize_audio')
    def test_process_job_missing_input_file(self, mock_normalize, job_directory_with_manifest):
        """Should return False when input file doesn't exist."""
        # Modify manifest to point to non-existent file
        manifest_path = job_directory_with_manifest / "manifest.json"
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        manifest['input_file']['path'] = "/nonexistent/file.mp3"
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f)
        
        result = normalizer.process_job(job_directory_with_manifest)
        
        assert result is False
        mock_normalize.assert_not_called()
    
    @patch('app.packages.ingest.normalizer.normalize_audio')
    def test_process_job_normalization_fails(self, mock_normalize, job_directory_with_manifest):
        """Should return False when normalize_audio fails."""
        mock_normalize.return_value = False
        
        result = normalizer.process_job(job_directory_with_manifest)
        
        assert result is False
        
        # Verify manifest was not updated with normalized_audio
        manifest_path = job_directory_with_manifest / "manifest.json"
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        assert 'normalized_audio' not in manifest
        assert manifest['pipeline_stage'] == 'validated'  # unchanged
