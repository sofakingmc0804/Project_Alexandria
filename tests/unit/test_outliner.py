"""
Unit tests for packages/planner/outliner.py

Tests chapter generation, duration targeting, and length mode variants.
"""

import json
import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open
from app.packages.planner import outliner


@pytest.fixture
def sample_segments():
    """Create sample segments with varying durations."""
    return [
        {
            'id': 'seg1',
            'start_ms': 0,
            'end_ms': 120000,  # 2 minutes
            'text': 'First segment about quantum computing and its applications in cryptography.'
        },
        {
            'id': 'seg2',
            'start_ms': 120000,
            'end_ms': 240000,  # 2 minutes
            'text': 'Second segment discussing machine learning techniques.'
        },
        {
            'id': 'seg3',
            'start_ms': 240000,
            'end_ms': 360000,  # 2 minutes
            'text': 'Third segment covering distributed systems architecture.'
        },
        {
            'id': 'seg4',
            'start_ms': 360000,
            'end_ms': 480000,  # 2 minutes
            'text': 'Fourth segment about data structures and algorithms.'
        },
        {
            'id': 'seg5',
            'start_ms': 480000,
            'end_ms': 600000,  # 2 minutes
            'text': 'Fifth segment on software engineering best practices.'
        }
    ]


@pytest.fixture
def sample_config():
    """Create sample output menu configuration."""
    return {
        'target_duration_minutes': 60,
        'length_mode': 'full',
        'persona': 'conversational_educator'
    }


class TestEstDur:
    """Test duration estimation helper."""
    
    def test_est_dur_calculates_correctly(self):
        segment = {'start_ms': 0, 'end_ms': 60000}  # 1 minute
        duration = outliner.est_dur(segment)
        assert duration == 1.0
    
    def test_est_dur_with_different_durations(self):
        segment = {'start_ms': 0, 'end_ms': 120000}  # 2 minutes
        duration = outliner.est_dur(segment)
        assert duration == 2.0
    
    def test_est_dur_with_non_zero_start(self):
        segment = {'start_ms': 60000, 'end_ms': 180000}  # 2 minutes
        duration = outliner.est_dur(segment)
        assert duration == 2.0


class TestCreateChapters:
    """Test chapter creation logic."""
    
    def test_create_chapters_full_mode(self, sample_segments):
        chapters, actual_target = outliner.create_chapters(sample_segments, 60, 'full')
        
        # Should use full target (60 minutes)
        assert actual_target == 60.0
        
        # With 10 minutes total and 60 minute target, should create 1 chapter
        assert len(chapters) >= 1
        
        # All chapters should have required fields
        for ch in chapters:
            assert 'chapter_id' in ch
            assert 'title' in ch
            assert 'description' in ch
            assert 'segment_ids' in ch
            assert 'duration_minutes' in ch
            assert 'order' in ch
    
    def test_create_chapters_condensed_mode(self, sample_segments):
        chapters, actual_target = outliner.create_chapters(sample_segments, 60, 'condensed')
        
        # Should use 33% of target (approximately 20 minutes, 19.8 is 60 * 0.33)
        assert actual_target == pytest.approx(19.8)
    
    def test_create_chapters_topic_focus_mode(self, sample_segments):
        chapters, actual_target = outliner.create_chapters(sample_segments, 60, 'topic_focus')
        
        # Should use 17% of target (10.2 minutes)
        assert actual_target == pytest.approx(10.2)
    
    def test_create_chapters_empty_segments(self):
        chapters, actual_target = outliner.create_chapters([], 60, 'full')
        
        assert chapters == []
        assert actual_target == 60.0
    
    def test_create_chapters_segment_ids(self, sample_segments):
        chapters, _ = outliner.create_chapters(sample_segments, 60, 'full')
        
        # Verify all chapter segment IDs are from the input segments
        all_ids = {seg['id'] for seg in sample_segments}
        for ch in chapters:
            for seg_id in ch['segment_ids']:
                assert seg_id in all_ids
    
    def test_create_chapters_duration_calculation(self, sample_segments):
        chapters, _ = outliner.create_chapters(sample_segments, 60, 'full')
        
        # Each chapter's duration should match sum of its segments
        for ch in chapters:
            expected_duration = sum(
                outliner.est_dur(seg) 
                for seg in sample_segments 
                if seg['id'] in ch['segment_ids']
            )
            assert ch['duration_minutes'] == pytest.approx(expected_duration)


class TestValidateOutline:
    """Test outline validation logic."""
    
    def test_validate_outline_within_target(self):
        chapters = [
            {'duration_minutes': 9.0},
            {'duration_minutes': 9.5}
        ]
        result = outliner.validate_outline(chapters, 20.0)
        
        # Total is 18.5, which is within 90-110% of 20.0 (18.0-22.0)
        assert result['passed'] is True
        assert result['total_duration'] == 18.5
        assert result['target_duration'] == 20.0
        assert result['num_chapters'] == 2
    
    def test_validate_outline_below_target(self):
        chapters = [
            {'duration_minutes': 5.0},
            {'duration_minutes': 5.0}
        ]
        result = outliner.validate_outline(chapters, 20.0)
        
        # Total is 10.0, which is below 90% of 20.0
        assert result['passed'] is False
    
    def test_validate_outline_above_target(self):
        chapters = [
            {'duration_minutes': 15.0},
            {'duration_minutes': 15.0}
        ]
        result = outliner.validate_outline(chapters, 20.0)
        
        # Total is 30.0, which is above 110% of 20.0
        assert result['passed'] is False
    
    def test_validate_outline_empty_chapters(self):
        result = outliner.validate_outline([], 20.0)
        
        assert result['passed'] is False
        assert result['total_duration'] == 0
        assert result['num_chapters'] == 0


class TestGenerateOutline:
    """Test end-to-end outline generation."""
    
    def test_generate_outline_success(self, tmp_path, sample_segments, sample_config):
        # Create job directory with segments
        job_dir = tmp_path / "job_001"
        job_dir.mkdir()
        
        segments_data = {
            'job_id': 'job_001',
            'segments': sample_segments
        }
        segments_path = job_dir / "segments.json"
        with open(segments_path, 'w') as f:
            json.dump(segments_data, f, indent=2)
        
        # Mock config loading
        with patch('app.packages.planner.outliner.load_config', return_value=sample_config):
            result = outliner.generate_outline(str(job_dir))
        
        # Verify result structure
        assert result['job_id'] == 'job_001'
        assert result['target_duration_minutes'] == 60
        assert result['actual_target_minutes'] == 60.0
        assert result['length_mode'] == 'full'
        assert 'chapters' in result
        assert 'validation' in result
        
        # Verify outline.yaml was created
        outline_path = job_dir / "outline.yaml"
        assert outline_path.exists()
        
        # Verify outline.yaml content
        with open(outline_path) as f:
            saved_outline = yaml.safe_load(f)
        assert saved_outline['job_id'] == 'job_001'
        assert len(saved_outline['chapters']) == len(result['chapters'])
    
    def test_generate_outline_empty_segments(self, tmp_path, sample_config):
        # Create job directory with no segments
        job_dir = tmp_path / "job_002"
        job_dir.mkdir()
        
        segments_data = {'job_id': 'job_002', 'segments': []}
        segments_path = job_dir / "segments.json"
        with open(segments_path, 'w') as f:
            json.dump(segments_data, f, indent=2)
        
        with patch('app.packages.planner.outliner.load_config', return_value=sample_config):
            result = outliner.generate_outline(str(job_dir))
        
        assert result['chapters'] == []
        assert result['validation']['passed'] is False
        assert result['validation']['num_chapters'] == 0
    
    def test_generate_outline_with_condensed_mode(self, tmp_path, sample_segments):
        # Create job directory
        job_dir = tmp_path / "job_003"
        job_dir.mkdir()
        
        segments_data = {'job_id': 'job_003', 'segments': sample_segments}
        segments_path = job_dir / "segments.json"
        with open(segments_path, 'w') as f:
            json.dump(segments_data, f, indent=2)
        
        # Config with condensed mode
        config = {
            'target_duration_minutes': 60,
            'length_mode': 'condensed'
        }
        
        with patch('app.packages.planner.outliner.load_config', return_value=config):
            result = outliner.generate_outline(str(job_dir))
        
        assert result['length_mode'] == 'condensed'
        assert result['actual_target_minutes'] == pytest.approx(19.8)


class TestLoadConfig:
    """Test configuration loading."""
    
    def test_load_config_reads_yaml(self, tmp_path):
        config_path = tmp_path / "test_config.yaml"
        config_data = {
            'target_duration_minutes': 45,
            'length_mode': 'condensed'
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        result = outliner.load_config(str(config_path))
        
        assert result['target_duration_minutes'] == 45
        assert result['length_mode'] == 'condensed'


class TestLoadSegments:
    """Test segment loading."""
    
    def test_load_segments_reads_json(self, tmp_path, sample_segments):
        job_dir = tmp_path / "job_004"
        job_dir.mkdir()
        
        segments_data = {'segments': sample_segments}
        segments_path = job_dir / "segments.json"
        with open(segments_path, 'w') as f:
            json.dump(segments_data, f, indent=2)
        
        result = outliner.load_segments(str(job_dir))
        
        assert len(result) == 5
        assert result[0]['id'] == 'seg1'
    
    def test_load_segments_missing_segments_key(self, tmp_path):
        job_dir = tmp_path / "job_005"
        job_dir.mkdir()
        
        segments_data = {'other_key': 'value'}
        segments_path = job_dir / "segments.json"
        with open(segments_path, 'w') as f:
            json.dump(segments_data, f, indent=2)
        
        result = outliner.load_segments(str(job_dir))
        
        assert result == []
