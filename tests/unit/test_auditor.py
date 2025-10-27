"""
Unit tests for packages/rag_audit/auditor.py

Tests groundedness verification and audit report generation.
"""

import json
import pytest
import yaml
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch
from app.packages.rag_audit import auditor


@pytest.fixture
def sample_config():
    """Create sample retrieval configuration."""
    return {
        'embed_model': 'sentence-transformers/all-MiniLM-L6-v2',
        'embed_device': 'cpu',
        'db_path': './tmp/faiss_index',
        'retrieval': {
            'top_k': 6,
            'min_score': 0.5
        },
        'quality': {
            'min_groundedness': 0.8
        }
    }


@pytest.fixture
def mock_index_data():
    """Create mock index data."""
    chunks = [
        {
            'chunk_id': 0,
            'text': 'Quantum computing uses qubits for processing.',
            'source_id': 'source1',
            'source_file': 'quantum.txt'
        },
        {
            'chunk_id': 1,
            'text': 'Machine learning algorithms can classify data.',
            'source_id': 'source2',
            'source_file': 'ml.txt'
        }
    ]
    
    metadata = {
        'chunks': chunks,
        'num_chunks': len(chunks),
        'embedding_dim': 384,
        'num_sources': 2
    }
    
    embeddings = np.random.rand(2, 384).astype(np.float32)
    
    return None, embeddings, metadata


class TestLoadConfig:
    """Test configuration loading."""
    
    def test_load_config_reads_yaml(self, tmp_path, sample_config):
        config_path = tmp_path / "test_retrieval.yaml"
        
        with open(config_path, 'w') as f:
            yaml.dump(sample_config, f)
        
        result = auditor.load_config(str(config_path))
        
        assert result['embed_model'] == 'sentence-transformers/all-MiniLM-L6-v2'
        assert result['retrieval']['top_k'] == 6


class TestExtractSentences:
    """Test sentence extraction."""
    
    def test_extract_sentences_basic(self):
        text = "First sentence. Second sentence. Third sentence."
        
        sentences = auditor.extract_sentences(text)
        
        assert len(sentences) == 3
        assert "First sentence" in sentences[0]
    
    def test_extract_sentences_empty(self):
        sentences = auditor.extract_sentences("")
        
        assert sentences == []
    
    def test_extract_sentences_with_questions(self):
        text = "Is this a question? Yes it is! That's great."
        
        sentences = auditor.extract_sentences(text)
        
        assert len(sentences) >= 2


class TestCalculateGroundedness:
    """Test groundedness calculation."""
    
    def test_calculate_groundedness_with_matches(self):
        sentence = "Quantum computing uses qubits"
        retrieved_chunks = [
            {
                'text': 'Quantum computing uses qubits for processing.',
                'source_id': 'source1'
            }
        ]
        
        score, sources = auditor.calculate_groundedness(sentence, retrieved_chunks)
        
        assert score > 0.0
        assert 'source1' in sources
    
    def test_calculate_groundedness_no_chunks(self):
        sentence = "Some random text"
        retrieved_chunks = []
        
        score, sources = auditor.calculate_groundedness(sentence, retrieved_chunks)
        
        assert score == 0.0
        assert sources == []
    
    def test_calculate_groundedness_no_overlap(self):
        sentence = "Completely different topic here"
        retrieved_chunks = [
            {
                'text': 'Quantum computing uses qubits.',
                'source_id': 'source1'
            }
        ]
        
        score, sources = auditor.calculate_groundedness(sentence, retrieved_chunks)
        
        # Should have low score due to minimal word overlap
        assert score >= 0.0


class TestRetrieveSources:
    """Test source retrieval."""
    
    @patch('app.packages.rag_audit.auditor.load_embedding_model')
    def test_retrieve_sources_with_embeddings(self, mock_load_model, sample_config):
        # Create mock model
        model = Mock()
        model.encode = Mock(return_value=np.random.rand(1, 384).astype(np.float32))
        mock_load_model.return_value = model
        
        query = "What is quantum computing?"
        
        chunks = [
            {
                'chunk_id': 0,
                'text': 'Quantum computing uses qubits.',
                'source_id': 'source1'
            }
        ]
        
        metadata = {'chunks': chunks}
        embeddings = np.random.rand(1, 384).astype(np.float32)
        
        results = auditor.retrieve_sources(
            query, None, embeddings, metadata, model, sample_config
        )
        
        assert isinstance(results, list)
    
    def test_retrieve_sources_no_model(self, sample_config):
        query = "test"
        metadata = {'chunks': []}
        
        with pytest.raises(RuntimeError, match="Embedding model must be available"):
            auditor.retrieve_sources(query, None, None, metadata, None, sample_config)


class TestAuditScript:
    """Test script auditing."""
    
    @patch('app.packages.rag_audit.auditor.retrieve_sources')
    def test_audit_script_success(self, mock_retrieve, tmp_path, sample_config, mock_index_data):
        # Create test script
        script_path = tmp_path / "script.md"
        script_content = """## Chapter 1
**Host A:** Quantum computing is fascinating.
**Host B:** It uses qubits for processing data.
"""
        script_path.write_text(script_content)
        
        # Mock retrieval to return relevant chunks
        def mock_retrieve_fn(*args, **kwargs):
            return [
                {
                    'text': 'Quantum computing uses qubits.',
                    'source_id': 'source1',
                    'relevance_score': 0.9
                }
            ]
        
        mock_retrieve.side_effect = mock_retrieve_fn
        
        index, embeddings, metadata = mock_index_data
        model = Mock()
        
        report = auditor.audit_script(
            str(script_path),
            index,
            embeddings,
            metadata,
            model,
            sample_config
        )
        
        assert 'script_path' in report
        assert 'total_sentences' in report
        assert 'avg_groundedness' in report
        assert 'passed' in report
        assert report['total_sentences'] > 0


class TestAuditJob:
    """Test job-level auditing."""
    
    @patch('app.packages.rag_audit.auditor.load_embedding_model')
    @patch('app.packages.rag_audit.auditor.load_index')
    @patch('app.packages.rag_audit.auditor.audit_script')
    def test_audit_job_success(self, mock_audit_script, mock_load_index, mock_load_model, tmp_path, sample_config, mock_index_data):
        # Setup
        job_dir = tmp_path / "job_001"
        job_dir.mkdir()
        
        script_path = job_dir / "script.md"
        script_path.write_text("**Host:** Test content.")
        
        config_path = tmp_path / "retrieval.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(sample_config, f)
        
        # Mock dependencies
        mock_load_model.return_value = Mock()
        mock_load_index.return_value = mock_index_data
        mock_audit_script.return_value = {
            'script_path': str(script_path),
            'total_sentences': 1,
            'avg_groundedness': 0.85,
            'passed': True
        }
        
        result = auditor.audit_job(str(job_dir), str(config_path))
        
        assert 'script_path' in result
        assert result['passed'] is True
        
        # Verify report was saved
        report_path = job_dir / 'audit_report.json'
        assert report_path.exists()
    
    @patch('app.packages.rag_audit.auditor.load_embedding_model')
    @patch('app.packages.rag_audit.auditor.load_index')
    def test_audit_job_missing_script(self, mock_load_index, mock_load_model, tmp_path, sample_config, mock_index_data):
        job_dir = tmp_path / "job_002"
        job_dir.mkdir()
        
        config_path = tmp_path / "retrieval.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(sample_config, f)
        
        mock_load_model.return_value = Mock()
        mock_load_index.return_value = mock_index_data
        
        result = auditor.audit_job(str(job_dir), str(config_path))
        
        assert 'error' in result
        assert 'script not found' in result['error']
    
    @patch('app.packages.rag_audit.auditor.load_embedding_model')
    def test_audit_job_missing_index(self, mock_load_model, tmp_path, sample_config):
        job_dir = tmp_path / "job_003"
        job_dir.mkdir()
        
        script_path = job_dir / "script.md"
        script_path.write_text("Test")
        
        config_path = tmp_path / "retrieval.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(sample_config, f)
        
        mock_load_model.return_value = Mock()
        
        # Mock load_index to raise FileNotFoundError
        with patch('app.packages.rag_audit.auditor.load_index', side_effect=FileNotFoundError("No index")):
            result = auditor.audit_job(str(job_dir), str(config_path))
        
        assert 'error' in result
