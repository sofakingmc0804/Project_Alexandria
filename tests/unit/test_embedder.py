#!/usr/bin/env python3
"""Unit tests for text embedder (Phase 2).

Tests embedding generation with sentence-transformers.
"""

import json
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from app.packages.embed import embedder


@pytest.fixture
def sample_segments():
    """Create sample segments for embedding."""
    return [
        {
            'id': 'seg1',
            'start_ms': 0,
            'end_ms': 20000,
            'text': 'This is the first segment about testing.',
            'lang': 'en',
            'confidence': 0.9
        },
        {
            'id': 'seg2',
            'start_ms': 20000,
            'end_ms': 40000,
            'text': 'This is the second segment covering more topics.',
            'lang': 'en',
            'confidence': 0.85
        }
    ]


@pytest.fixture
def job_directory_with_segments(tmp_path, sample_segments):
    """Create a job directory with segments.json."""
    job_dir = tmp_path / "job_001"
    job_dir.mkdir()
    
    segments_data = {
        'job_id': 'job_001',
        'segments': sample_segments,
        'segment_count': len(sample_segments)
    }
    
    segments_path = job_dir / "segments.json"
    with open(segments_path, 'w', encoding='utf-8') as f:
        json.dump(segments_data, f, indent=2)
    
    return job_dir


class TestLoadEmbeddingModel:
    """Tests for load_embedding_model() function."""
    
    # Note: Skipping tests that require sentence_transformers since it's an optional dependency
    
    def test_load_model_missing_library(self):
        """Should raise RuntimeError when sentence-transformers not installed."""
        with patch.dict('sys.modules', {'sentence_transformers': None}):
            with pytest.raises(RuntimeError, match="sentence-transformers is required"):
                embedder.load_embedding_model()


class TestEmbedSegments:
    """Tests for embed_segments() function."""
    
    def test_embed_segments_success(self, sample_segments):
        """Should successfully embed segments."""
        mock_model = MagicMock()
        mock_model.name_or_path = 'test-model'
        
        # Mock embeddings (2 segments, 384 dimensions)
        mock_embeddings = np.random.randn(2, 384).astype(np.float32)
        mock_model.encode.return_value = mock_embeddings
        
        result = embedder.embed_segments(sample_segments, mock_model)
        
        assert len(result) == 2
        assert 'embedding' in result[0]
        assert 'embedding_model' in result[0]
        assert 'embedding_dim' in result[0]
        assert result[0]['embedding_model'] == 'test-model'
        assert result[0]['embedding_dim'] == 384
        assert len(result[0]['embedding']) == 384
        
        mock_model.encode.assert_called_once()
    
    def test_embed_segments_empty_list(self):
        """Should handle empty segment list."""
        mock_model = MagicMock()
        
        result = embedder.embed_segments([], mock_model)
        
        assert result == []
        mock_model.encode.assert_not_called()
    
    def test_embed_segments_no_model(self, sample_segments):
        """Should raise error when model is None."""
        with pytest.raises(RuntimeError, match="Embedding model must be provided"):
            embedder.embed_segments(sample_segments, None)
    
    def test_embed_segments_preserves_original_fields(self, sample_segments):
        """Should preserve original segment fields."""
        mock_model = MagicMock()
        mock_model.name_or_path = 'test-model'
        mock_embeddings = np.random.randn(2, 128).astype(np.float32)
        mock_model.encode.return_value = mock_embeddings
        
        result = embedder.embed_segments(sample_segments, mock_model)
        
        assert result[0]['id'] == 'seg1'
        assert result[0]['text'] == 'This is the first segment about testing.'
        assert result[0]['lang'] == 'en'
        assert result[0]['confidence'] == 0.9


class TestEmbedJob:
    """Tests for embed_job() function."""
    
    @patch('app.packages.embed.embedder.load_embedding_model')
    @patch('app.packages.embed.embedder.embed_segments')
    def test_embed_job_success(self, mock_embed_segments, mock_load_model, job_directory_with_segments):
        """Should successfully embed job segments."""
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        
        # Mock embedded segments
        embedded_segs = [
            {
                'id': 'seg1',
                'text': 'Test',
                'embedding': [0.1] * 384,
                'embedding_model': 'test-model',
                'embedding_dim': 384
            },
            {
                'id': 'seg2',
                'text': 'Test2',
                'embedding': [0.2] * 384,
                'embedding_model': 'test-model',
                'embedding_dim': 384
            }
        ]
        mock_embed_segments.return_value = embedded_segs
        
        result = embedder.embed_job(str(job_directory_with_segments))
        
        assert result['job_id'] == 'job_001'
        assert len(result['segments']) == 2
        assert result['embedding_model'] == 'test-model'
        assert result['embedding_dim'] == 384
        
        # Verify output file was created
        output_path = job_directory_with_segments / "segments_embedded.json"
        assert output_path.exists()
        
        with open(output_path, 'r', encoding='utf-8') as f:
            output_data = json.load(f)
        
        assert output_data['job_id'] == 'job_001'
        assert len(output_data['segments']) == 2
    
    def test_embed_job_missing_segments_file(self, tmp_path):
        """Should raise error when segments.json doesn't exist."""
        job_dir = tmp_path / "job_no_segments"
        job_dir.mkdir()
        
        with pytest.raises(FileNotFoundError):
            embedder.embed_job(str(job_dir))
    
    @patch('app.packages.embed.embedder.load_embedding_model')
    def test_embed_job_empty_segments(self, mock_load_model, tmp_path):
        """Should handle empty segments list."""
        job_dir = tmp_path / "job_empty"
        job_dir.mkdir()
        
        segments_data = {
            'job_id': 'job_empty',
            'segments': []
        }
        
        segments_path = job_dir / "segments.json"
        with open(segments_path, 'w', encoding='utf-8') as f:
            json.dump(segments_data, f)
        
        result = embedder.embed_job(str(job_dir))
        
        assert result['job_id'] == 'job_empty'
        assert result['segments'] == []
        assert result['embedding_model'] == 'none'
        assert result['embedding_dim'] == 0
        
        # Should not try to load model for empty segments
        mock_load_model.assert_not_called()
    
    @patch('app.packages.embed.embedder.load_embedding_model')
    @patch('app.packages.embed.embedder.embed_segments')
    def test_embed_job_custom_model(self, mock_embed_segments, mock_load_model, job_directory_with_segments):
        """Should use custom model when specified."""
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        
        embedded_segs = [
            {
                'id': 'seg1',
                'embedding': [0.1] * 128,
                'embedding_model': 'custom-model',
                'embedding_dim': 128
            }
        ]
        mock_embed_segments.return_value = embedded_segs
        
        embedder.embed_job(str(job_directory_with_segments), model_name='custom-model')
        
        mock_load_model.assert_called_once_with('custom-model')
