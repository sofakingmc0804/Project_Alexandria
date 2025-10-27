"""
Unit tests for packages/planner/selector.py

Tests segment selection per chapter with duplicate avoidance.
"""

import json
import pytest
from pathlib import Path
from app.packages.planner import selector


@pytest.fixture
def sample_outline():
    """Create sample outline with chapters."""
    return {
        'job_id': 'job_001',
        'chapters': [
            {
                'chapter_id': 'ch01',
                'title': 'Chapter 1',
                'segment_ids': ['seg1', 'seg2', 'seg3']
            },
            {
                'chapter_id': 'ch02',
                'title': 'Chapter 2',
                'segment_ids': ['seg4', 'seg5', 'seg6']
            }
        ]
    }


@pytest.fixture
def sample_segments():
    """Create sample segments."""
    return [
        {'id': 'seg1', 'text': 'First segment', 'start_ms': 0, 'end_ms': 10000},
        {'id': 'seg2', 'text': 'Second segment', 'start_ms': 10000, 'end_ms': 20000},
        {'id': 'seg3', 'text': 'Third segment', 'start_ms': 20000, 'end_ms': 30000},
        {'id': 'seg4', 'text': 'Fourth segment', 'start_ms': 30000, 'end_ms': 40000},
        {'id': 'seg5', 'text': 'Fifth segment', 'start_ms': 40000, 'end_ms': 50000},
        {'id': 'seg6', 'text': 'Sixth segment', 'start_ms': 50000, 'end_ms': 60000}
    ]


@pytest.fixture
def sample_graph():
    """Create sample graph with duplicates."""
    return {
        'nodes': [],
        'edges': [],
        'duplicates': [
            {
                'segment1_id': 'seg2',
                'segment2_id': 'seg5',  # seg5 is marked as duplicate
                'similarity': 0.95
            }
        ]
    }


class TestLoadOutline:
    """Test outline loading."""
    
    def test_load_outline_reads_yaml(self, tmp_path, sample_outline):
        import yaml
        
        job_dir = tmp_path / "job_001"
        job_dir.mkdir()
        
        outline_path = job_dir / "outline.yaml"
        with open(outline_path, 'w') as f:
            yaml.dump(sample_outline, f)
        
        result = selector.load_outline(str(job_dir))
        
        assert result['job_id'] == 'job_001'
        assert len(result['chapters']) == 2
        assert result['chapters'][0]['chapter_id'] == 'ch01'


class TestLoadSegments:
    """Test segment loading."""
    
    def test_load_segments_reads_json(self, tmp_path, sample_segments):
        job_dir = tmp_path / "job_001"
        job_dir.mkdir()
        
        segments_data = {'segments': sample_segments}
        segments_path = job_dir / "segments.json"
        with open(segments_path, 'w') as f:
            json.dump(segments_data, f, indent=2)
        
        result = selector.load_segments(str(job_dir))
        
        assert len(result) == 6
        assert result[0]['id'] == 'seg1'


class TestLoadGraph:
    """Test graph loading."""
    
    def test_load_graph_reads_json(self, tmp_path, sample_graph):
        job_dir = tmp_path / "job_001"
        job_dir.mkdir()
        
        graph_path = job_dir / "graph.json"
        with open(graph_path, 'w') as f:
            json.dump(sample_graph, f, indent=2)
        
        result = selector.load_graph(str(job_dir))
        
        assert 'duplicates' in result
        assert len(result['duplicates']) == 1
        assert result['duplicates'][0]['segment2_id'] == 'seg5'


class TestSelectSegments:
    """Test segment selection logic."""
    
    def test_select_segments_success(self, tmp_path, sample_outline, sample_segments, sample_graph):
        import yaml
        
        # Create job directory with all required files
        job_dir = tmp_path / "job_001"
        job_dir.mkdir()
        
        # Save outline
        outline_path = job_dir / "outline.yaml"
        with open(outline_path, 'w') as f:
            yaml.dump(sample_outline, f)
        
        # Save segments
        segments_data = {'segments': sample_segments}
        segments_path = job_dir / "segments.json"
        with open(segments_path, 'w') as f:
            json.dump(segments_data, f, indent=2)
        
        # Save graph
        graph_path = job_dir / "graph.json"
        with open(graph_path, 'w') as f:
            json.dump(sample_graph, f, indent=2)
        
        result = selector.select_segments(str(job_dir))
        
        # Verify result structure
        assert result['job_id'] == 'job_001'
        assert 'selection' in result
        assert len(result['selection']) == 2  # Two chapters
        assert result['num_duplicates_skipped'] == 1  # seg5 is duplicate
        
        # Verify selection.json was created
        selection_path = job_dir / "selection.json"
        assert selection_path.exists()
        
        # Verify selection.json content
        with open(selection_path) as f:
            saved_selection = json.load(f)
        assert saved_selection['job_id'] == 'job_001'
    
    def test_select_segments_skips_duplicates(self, tmp_path, sample_outline, sample_segments, sample_graph):
        import yaml
        
        job_dir = tmp_path / "job_002"
        job_dir.mkdir()
        
        outline_path = job_dir / "outline.yaml"
        with open(outline_path, 'w') as f:
            yaml.dump(sample_outline, f)
        
        segments_data = {'segments': sample_segments}
        segments_path = job_dir / "segments.json"
        with open(segments_path, 'w') as f:
            json.dump(segments_data, f, indent=2)
        
        graph_path = job_dir / "graph.json"
        with open(graph_path, 'w') as f:
            json.dump(sample_graph, f, indent=2)
        
        result = selector.select_segments(str(job_dir))
        
        # seg5 should be skipped as duplicate
        all_selected = []
        for ch in result['selection']:
            for seg in ch['segments']:
                all_selected.append(seg['id'])
        
        assert 'seg5' not in all_selected
        assert 'seg2' in all_selected  # Original (not duplicate) should be included
    
    def test_select_segments_avoids_reuse(self, tmp_path, sample_segments):
        import yaml
        
        # Create outline where same segment appears in multiple chapters
        outline = {
            'job_id': 'job_003',
            'chapters': [
                {
                    'chapter_id': 'ch01',
                    'title': 'Chapter 1',
                    'segment_ids': ['seg1', 'seg2']
                },
                {
                    'chapter_id': 'ch02',
                    'title': 'Chapter 2',
                    'segment_ids': ['seg2', 'seg3']  # seg2 appears again
                }
            ]
        }
        
        job_dir = tmp_path / "job_003"
        job_dir.mkdir()
        
        outline_path = job_dir / "outline.yaml"
        with open(outline_path, 'w') as f:
            yaml.dump(outline, f)
        
        segments_data = {'segments': sample_segments}
        segments_path = job_dir / "segments.json"
        with open(segments_path, 'w') as f:
            json.dump(segments_data, f, indent=2)
        
        # Graph with no duplicates
        graph = {'duplicates': []}
        graph_path = job_dir / "graph.json"
        with open(graph_path, 'w') as f:
            json.dump(graph, f, indent=2)
        
        result = selector.select_segments(str(job_dir))
        
        # Count how many times seg2 appears in selection
        seg2_count = 0
        for ch in result['selection']:
            for seg in ch['segments']:
                if seg['id'] == 'seg2':
                    seg2_count += 1
        
        # seg2 should only appear once (in first chapter)
        assert seg2_count == 1
    
    def test_select_segments_handles_missing_segment(self, tmp_path, sample_segments):
        import yaml
        
        # Create outline with non-existent segment ID
        outline = {
            'job_id': 'job_004',
            'chapters': [
                {
                    'chapter_id': 'ch01',
                    'title': 'Chapter 1',
                    'segment_ids': ['seg1', 'seg_missing', 'seg2']
                }
            ]
        }
        
        job_dir = tmp_path / "job_004"
        job_dir.mkdir()
        
        outline_path = job_dir / "outline.yaml"
        with open(outline_path, 'w') as f:
            yaml.dump(outline, f)
        
        segments_data = {'segments': sample_segments}
        segments_path = job_dir / "segments.json"
        with open(segments_path, 'w') as f:
            json.dump(segments_data, f, indent=2)
        
        graph = {'duplicates': []}
        graph_path = job_dir / "graph.json"
        with open(graph_path, 'w') as f:
            json.dump(graph, f, indent=2)
        
        result = selector.select_segments(str(job_dir))
        
        # Should only select seg1 and seg2 (skip missing)
        selected_ids = [seg['id'] for ch in result['selection'] for seg in ch['segments']]
        assert 'seg1' in selected_ids
        assert 'seg2' in selected_ids
        assert 'seg_missing' not in selected_ids
    
    def test_select_segments_empty_chapters(self, tmp_path, sample_segments):
        import yaml
        
        # Create outline with no chapters
        outline = {
            'job_id': 'job_005',
            'chapters': []
        }
        
        job_dir = tmp_path / "job_005"
        job_dir.mkdir()
        
        outline_path = job_dir / "outline.yaml"
        with open(outline_path, 'w') as f:
            yaml.dump(outline, f)
        
        segments_data = {'segments': sample_segments}
        segments_path = job_dir / "segments.json"
        with open(segments_path, 'w') as f:
            json.dump(segments_data, f, indent=2)
        
        graph = {'duplicates': []}
        graph_path = job_dir / "graph.json"
        with open(graph_path, 'w') as f:
            json.dump(graph, f, indent=2)
        
        result = selector.select_segments(str(job_dir))
        
        assert result['selection'] == []
        assert result['num_selected'] == 0
    
    def test_select_segments_preserves_chapter_structure(self, tmp_path, sample_outline, sample_segments, sample_graph):
        import yaml
        
        job_dir = tmp_path / "job_006"
        job_dir.mkdir()
        
        outline_path = job_dir / "outline.yaml"
        with open(outline_path, 'w') as f:
            yaml.dump(sample_outline, f)
        
        segments_data = {'segments': sample_segments}
        segments_path = job_dir / "segments.json"
        with open(segments_path, 'w') as f:
            json.dump(segments_data, f, indent=2)
        
        graph_path = job_dir / "graph.json"
        with open(graph_path, 'w') as f:
            json.dump(sample_graph, f, indent=2)
        
        result = selector.select_segments(str(job_dir))
        
        # Verify chapter structure is preserved
        for i, ch in enumerate(result['selection']):
            assert ch['chapter_id'] == sample_outline['chapters'][i]['chapter_id']
            assert ch['title'] == sample_outline['chapters'][i]['title']
            assert 'segments' in ch
