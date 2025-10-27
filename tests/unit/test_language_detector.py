#!/usr/bin/env python3
"""Unit tests for language detector (Phase 1).

Tests language detection from transcripts using langdetect.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from app.packages.asr import language_detector


@pytest.fixture
def job_directory_with_transcript(tmp_path):
    """Create a job directory with manifest and transcript."""
    job_dir = tmp_path / "job_001"
    job_dir.mkdir()
    
    # Create transcript directory and file
    transcript_dir = job_dir / "transcript"
    transcript_dir.mkdir()
    
    transcript_data = {
        "segments": [
            {"id": 0, "start": 0.0, "end": 2.0, "text": "This is a test."},
            {"id": 1, "start": 2.0, "end": 4.0, "text": "Testing language detection."}
        ],
        "words": [],
        "duration": 4.0
    }
    
    transcript_path = transcript_dir / "transcript.json"
    with open(transcript_path, 'w', encoding='utf-8') as f:
        json.dump(transcript_data, f, indent=2)
    
    # Create manifest
    manifest = {
        "job_id": "job_001",
        "pipeline_stage": "transcribed",
        "metadata": {},
        "transcript": {
            "json_path": str(transcript_path),
            "srt_path": str(transcript_dir / "transcript.srt"),
            "segments_count": 2
        }
    }
    
    manifest_path = job_dir / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    return job_dir


class TestDetectLanguage:
    """Tests for detect_language() function."""
    
    @patch('app.packages.asr.language_detector.LANGDETECT_AVAILABLE', False)
    def test_detect_language_fallback(self):
        """Should return 'en' when langdetect not available."""
        lang, confidence = language_detector.detect_language("Hello world")
        assert lang == 'en'
        assert confidence == 1.0
    
    # Note: Tests requiring langdetect are skipped since it's an optional dependency
    # and we test with the fallback behavior instead.


class TestProcessJob:
    """Tests for process_job() function."""
    
    @patch('app.packages.asr.language_detector.detect_language')
    def test_process_job_success(self, mock_detect, job_directory_with_transcript):
        """Should successfully detect language and update manifest."""
        mock_detect.return_value = ('en', 0.95)
        
        result = language_detector.process_job(job_directory_with_transcript)
        
        assert result is True
        
        # Verify manifest was updated
        manifest_path = job_directory_with_transcript / "manifest.json"
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        assert manifest['metadata']['language'] == 'en'
        assert 'language_detection' in manifest
        assert manifest['language_detection']['language'] == 'en'
        assert manifest['language_detection']['confidence'] == 0.95
        
        # Verify transcript was updated
        transcript_path = Path(manifest['transcript']['json_path'])
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_data = json.load(f)
        
        assert transcript_data['language'] == 'en'
    
    @patch('app.packages.asr.language_detector.detect_language')
    def test_process_job_spanish(self, mock_detect, job_directory_with_transcript):
        """Should correctly detect non-English language."""
        mock_detect.return_value = ('es', 0.92)
        
        language_detector.process_job(job_directory_with_transcript)
        
        manifest_path = job_directory_with_transcript / "manifest.json"
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        assert manifest['metadata']['language'] == 'es'
        assert manifest['language_detection']['language'] == 'es'
        assert manifest['language_detection']['confidence'] == 0.92
    
    def test_process_job_missing_manifest(self, tmp_path):
        """Should return False when manifest doesn't exist."""
        job_dir = tmp_path / "no_manifest"
        job_dir.mkdir()
        
        result = language_detector.process_job(job_dir)
        
        assert result is False
    
    def test_process_job_no_transcript(self, tmp_path):
        """Should return False when manifest doesn't have transcript."""
        job_dir = tmp_path / "job_001"
        job_dir.mkdir()
        
        manifest = {
            "job_id": "job_001",
            "pipeline_stage": "normalized",
            "metadata": {}
        }
        
        manifest_path = job_dir / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f)
        
        result = language_detector.process_job(job_dir)
        
        assert result is False
    
    @patch('app.packages.asr.language_detector.detect_language')
    def test_process_job_missing_transcript_file(self, mock_detect, tmp_path):
        """Should return False when transcript file doesn't exist."""
        job_dir = tmp_path / "job_001"
        job_dir.mkdir()
        
        manifest = {
            "job_id": "job_001",
            "pipeline_stage": "transcribed",
            "metadata": {},
            "transcript": {
                "json_path": "/nonexistent/transcript.json"
            }
        }
        
        manifest_path = job_dir / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f)
        
        result = language_detector.process_job(job_dir)
        
        assert result is False
        mock_detect.assert_not_called()
    
    @patch('app.packages.asr.language_detector.detect_language')
    def test_process_job_empty_transcript(self, mock_detect, tmp_path):
        """Should return False when transcript has no text."""
        job_dir = tmp_path / "job_001"
        job_dir.mkdir()
        
        transcript_dir = job_dir / "transcript"
        transcript_dir.mkdir()
        
        # Empty transcript
        transcript_data = {
            "segments": [],
            "words": []
        }
        
        transcript_path = transcript_dir / "transcript.json"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f)
        
        manifest = {
            "job_id": "job_001",
            "metadata": {},
            "transcript": {
                "json_path": str(transcript_path)
            }
        }
        
        manifest_path = job_dir / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f)
        
        result = language_detector.process_job(job_dir)
        
        assert result is False
        mock_detect.assert_not_called()
    
    @patch('app.packages.asr.language_detector.detect_language')
    def test_process_job_whitespace_only_transcript(self, mock_detect, tmp_path):
        """Should return False when transcript contains only whitespace."""
        job_dir = tmp_path / "job_001"
        job_dir.mkdir()
        
        transcript_dir = job_dir / "transcript"
        transcript_dir.mkdir()
        
        # Whitespace-only transcript
        transcript_data = {
            "segments": [
                {"id": 0, "text": "   "},
                {"id": 1, "text": "\t\n"}
            ]
        }
        
        transcript_path = transcript_dir / "transcript.json"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f)
        
        manifest = {
            "job_id": "job_001",
            "metadata": {},
            "transcript": {
                "json_path": str(transcript_path)
            }
        }
        
        manifest_path = job_dir / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f)
        
        result = language_detector.process_job(job_dir)
        
        assert result is False
        mock_detect.assert_not_called()
