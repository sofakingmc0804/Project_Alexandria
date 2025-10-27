#!/usr/bin/env python3
"""Unit tests for knowledge graph builder (Phase 2).

Tests graph construction from embedded segments.
"""

import json
import pytest
import numpy as np
from pathlib import Path

from app.packages.graph import builder


@pytest.fixture
def sample_embeddings():
    """Create sample embeddings for testing."""
    # Create 3 embeddings where 0 and 1 are similar, 2 is different
    emb1 = np.array([1.0, 0.0, 0.0, 0.0])
    emb2 = np.array([0.9, 0.1, 0.0, 0.0])  # Similar to emb1
    emb3 = np.array([0.0, 0.0, 1.0, 0.0])  # Different
    
    # Normalize
    emb1 = emb1 / np.linalg.norm(emb1)
    emb2 = emb2 / np.linalg.norm(emb2)
    emb3 = emb3 / np.linalg.norm(emb3)
    
    return np.array([emb1, emb2, emb3], dtype=np.float32)


@pytest.fixture
def sample_segments():
    """Create sample segments with embeddings."""
    return [
        {
            'id': 'seg1',
            'start_ms': 0,
            'end_ms': 20000,
            'text': 'First segment about testing',
            'lang': 'en',
            'embedding': [1.0, 0.0, 0.0, 0.0]
        },
        {
            'id': 'seg2',
            'start_ms': 20000,
            'end_ms': 40000,
            'text': 'Second segment also about testing',
            'lang': 'en',
            'embedding': [0.9, 0.1, 0.0, 0.0]
        },
        {
            'id': 'seg3',
            'start_ms': 40000,
            'end_ms': 60000,
            'text': 'Third segment about different topic',
            'lang': 'en',
            'embedding': [0.0, 0.0, 1.0, 0.0]
        }
    ]


@pytest.fixture
def job_directory_with_embeddings(tmp_path):
    """Create a job directory with embedded segments."""
    job_dir = tmp_path / "job_001"
    job_dir.mkdir()
    
    # Use plain Python lists instead of numpy arrays to avoid serialization issues
    segments = [
        {
            'id': 'seg1',
            'start_ms': 0,
            'end_ms': 20000,
            'text': 'First segment about testing',
            'lang': 'en',
            'embedding': [1.0, 0.0, 0.0, 0.0]
        },
        {
            'id': 'seg2',
            'start_ms': 20000,
            'end_ms': 40000,
            'text': 'Second segment also about testing',
            'lang': 'en',
            'embedding': [0.9, 0.1, 0.0, 0.0]
        }
    ]
    
    data = {
        'job_id': 'job_001',
        'segments': segments,
        'embedding_model': 'test-model',
        'embedding_dim': 4
    }
    
    segments_path = job_dir / "segments_embedded.json"
    with open(segments_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    return job_dir


class TestComputeSimilarityMatrix:
    """Tests for compute_similarity_matrix() function."""
    
    def test_similarity_matrix_shape(self, sample_embeddings):
        """Should return correct shape similarity matrix."""
        result = builder.compute_similarity_matrix(sample_embeddings)
        
        assert result.shape == (3, 3)
    
    def test_similarity_matrix_diagonal(self, sample_embeddings):
        """Should have 1.0 on diagonal (self-similarity)."""
        result = builder.compute_similarity_matrix(sample_embeddings)
        
        np.testing.assert_allclose(np.diag(result), 1.0, rtol=1e-5)
    
    def test_similarity_matrix_symmetric(self, sample_embeddings):
        """Should be symmetric matrix."""
        result = builder.compute_similarity_matrix(sample_embeddings)
        
        np.testing.assert_allclose(result, result.T, rtol=1e-5)
    
    def test_similarity_matrix_values_range(self, sample_embeddings):
        """Should have values between -1 and 1."""
        result = builder.compute_similarity_matrix(sample_embeddings)
        
        assert np.all(result >= -1.0)
        assert np.all(result <= 1.0)
    
    def test_similarity_matrix_zero_vector(self):
        """Should handle zero vectors without division by zero."""
        embeddings = np.array([[0.0, 0.0], [1.0, 0.0]], dtype=np.float32)
        
        result = builder.compute_similarity_matrix(embeddings)
        
        assert not np.isnan(result).any()
        assert not np.isinf(result).any()


class TestFindDuplicates:
    """Tests for find_duplicates() function."""
    
    def test_find_duplicates_with_high_similarity(self):
        """Should find duplicate pairs above threshold."""
        # Create similarity matrix with one high similarity pair
        similarity_matrix = np.array([
            [1.0, 0.95, 0.5],
            [0.95, 1.0, 0.4],
            [0.5, 0.4, 1.0]
        ], dtype=np.float32)
        
        duplicates = builder.find_duplicates(similarity_matrix, threshold=0.90)
        
        assert len(duplicates) == 1
        assert duplicates[0][0] == 0
        assert duplicates[0][1] == 1
        assert abs(duplicates[0][2] - 0.95) < 0.01  # Floating point tolerance
    
    def test_find_duplicates_no_matches(self):
        """Should return empty list when no duplicates."""
        similarity_matrix = np.array([
            [1.0, 0.5, 0.3],
            [0.5, 1.0, 0.4],
            [0.3, 0.4, 1.0]
        ], dtype=np.float32)
        
        duplicates = builder.find_duplicates(similarity_matrix, threshold=0.90)
        
        assert len(duplicates) == 0
    
    def test_find_duplicates_custom_threshold(self):
        """Should respect custom threshold."""
        similarity_matrix = np.array([
            [1.0, 0.75, 0.65],
            [0.75, 1.0, 0.55],
            [0.65, 0.55, 1.0]
        ], dtype=np.float32)
        
        # With high threshold, no matches
        duplicates_high = builder.find_duplicates(similarity_matrix, threshold=0.80)
        assert len(duplicates_high) == 0
        
        # With lower threshold, should find matches
        duplicates_low = builder.find_duplicates(similarity_matrix, threshold=0.70)
        assert len(duplicates_low) == 1  # Only (0, 1) with 0.75
    
    def test_find_duplicates_excludes_self(self):
        """Should not include self-similarity (diagonal)."""
        similarity_matrix = np.eye(2, dtype=np.float32)
        
        duplicates = builder.find_duplicates(similarity_matrix, threshold=0.50)
        
        assert len(duplicates) == 0


class TestBuildGraph:
    """Tests for build_graph() function."""
    
    def test_build_graph_creates_nodes(self, sample_segments, sample_embeddings):
        """Should create node for each segment."""
        similarity_matrix = builder.compute_similarity_matrix(sample_embeddings)
        
        graph = builder.build_graph(sample_segments, similarity_matrix)
        
        assert len(graph['nodes']) == 3
        assert graph['num_nodes'] == 3
        assert graph['nodes'][0]['id'] == 'seg1'
        assert graph['nodes'][0]['index'] == 0
        assert 'text_preview' in graph['nodes'][0]
    
    def test_build_graph_creates_edges(self, sample_segments, sample_embeddings):
        """Should create edges for similar segments."""
        similarity_matrix = builder.compute_similarity_matrix(sample_embeddings)
        
        graph = builder.build_graph(
            sample_segments,
            similarity_matrix,
            similarity_threshold=0.70
        )
        
        assert 'edges' in graph
        assert graph['num_edges'] == len(graph['edges'])
        
        # Each edge should have required fields
        for edge in graph['edges']:
            assert 'source' in edge
            assert 'target' in edge
            assert 'similarity' in edge
            assert 'is_duplicate' in edge
    
    def test_build_graph_respects_similarity_threshold(self, sample_segments, sample_embeddings):
        """Should only create edges above threshold."""
        similarity_matrix = builder.compute_similarity_matrix(sample_embeddings)
        
        # With high threshold, few edges
        graph_high = builder.build_graph(
            sample_segments,
            similarity_matrix,
            similarity_threshold=0.95
        )
        
        # With low threshold, more edges
        graph_low = builder.build_graph(
            sample_segments,
            similarity_matrix,
            similarity_threshold=0.10
        )
        
        assert graph_low['num_edges'] >= graph_high['num_edges']
    
    def test_build_graph_flags_duplicates(self, sample_segments, sample_embeddings):
        """Should flag high-similarity edges as duplicates."""
        similarity_matrix = builder.compute_similarity_matrix(sample_embeddings)
        
        graph = builder.build_graph(
            sample_segments,
            similarity_matrix,
            similarity_threshold=0.50,
            duplicate_threshold=0.90
        )
        
        assert 'duplicates' in graph
        assert 'num_duplicates' in graph
        assert graph['num_duplicates'] == len(graph['duplicates'])
    
    def test_build_graph_text_preview_truncation(self):
        """Should truncate long text in node preview."""
        long_text = "x" * 200
        segments = [{
            'id': 'seg1',
            'start_ms': 0,
            'end_ms': 1000,
            'text': long_text,
            'lang': 'en'
        }]
        embeddings = np.array([[1.0, 0.0]], dtype=np.float32)
        similarity_matrix = builder.compute_similarity_matrix(embeddings)
        
        graph = builder.build_graph(segments, similarity_matrix)
        
        preview = graph['nodes'][0]['text_preview']
        assert len(preview) <= 103  # 100 + "..."
        assert preview.endswith('...')


class TestBuildSegmentGraph:
    """Tests for build_segment_graph() function."""
    
    def test_build_segment_graph_success(self, job_directory_with_embeddings):
        """Should successfully build graph from job directory."""
        result = builder.build_segment_graph(str(job_directory_with_embeddings))
        
        assert result['job_id'] == 'job_001'
        assert 'nodes' in result
        assert 'edges' in result
        assert 'num_nodes' in result
        assert 'num_edges' in result
        
        # Verify output file was created
        output_path = job_directory_with_embeddings / "graph.json"
        assert output_path.exists()
        
        with open(output_path, 'r', encoding='utf-8') as f:
            output_data = json.load(f)
        
        assert output_data['job_id'] == 'job_001'
    
    def test_build_segment_graph_missing_embeddings(self, tmp_path):
        """Should raise error when embeddings file doesn't exist."""
        job_dir = tmp_path / "job_no_embeddings"
        job_dir.mkdir()
        
        with pytest.raises(FileNotFoundError):
            builder.build_segment_graph(str(job_dir))
    
    def test_build_segment_graph_empty_segments(self, tmp_path):
        """Should handle empty segments gracefully."""
        job_dir = tmp_path / "job_empty"
        job_dir.mkdir()
        
        data = {
            'job_id': 'job_empty',
            'segments': []
        }
        
        segments_path = job_dir / "segments_embedded.json"
        with open(segments_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
        result = builder.build_segment_graph(str(job_dir))
        
        assert result['job_id'] == 'job_empty'
        assert result['num_nodes'] == 0
        assert result['num_edges'] == 0
        assert result['num_duplicates'] == 0
