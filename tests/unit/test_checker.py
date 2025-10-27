"""
Unit tests for packages/continuity/checker.py

Tests continuity verification and quality checks.
"""

import json
import pytest
from pathlib import Path
from app.packages.continuity import checker


class TestLoadScript:
    """Test script loading."""
    
    def test_load_script_reads_markdown(self, tmp_path):
        job_dir = tmp_path / "job_001"
        job_dir.mkdir()
        
        script_content = """## Chapter 1
**Host:** Welcome to the show.

## Chapter 2
**Host:** Let's dive into the topic."""
        
        script_path = job_dir / "script.md"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        result = checker.load_script(str(job_dir))
        
        assert "Chapter 1" in result
        assert "Welcome to the show" in result
        assert "Chapter 2" in result
    
    def test_load_script_missing_file(self, tmp_path):
        job_dir = tmp_path / "job_002"
        job_dir.mkdir()
        
        # No script.md file
        result = checker.load_script(str(job_dir))
        
        assert result == ""
    
    def test_load_script_empty_file(self, tmp_path):
        job_dir = tmp_path / "job_003"
        job_dir.mkdir()
        
        script_path = job_dir / "script.md"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write("")
        
        result = checker.load_script(str(job_dir))
        
        assert result == ""


class TestCheckContinuity:
    """Test continuity checking logic."""
    
    def test_check_continuity_success(self, tmp_path):
        job_dir = tmp_path / "job_001"
        job_dir.mkdir()
        
        script_content = """## Chapter 1
**Host A:** Welcome to the show about quantum computing.
**Host B:** Thanks for having me! Let's explore this fascinating topic.

## Chapter 2
**Host A:** Now, let's discuss the practical applications.
**Host B:** Absolutely, there are many exciting developments."""
        
        script_path = job_dir / "script.md"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        result = checker.check_continuity(str(job_dir))
        
        # Verify result structure
        assert result['job_id'] == 'job_001'
        assert result['passed'] is True
        assert result['blockers'] == []
        assert 'warnings' in result
        assert 'issues' in result
        assert 'entities_extracted' in result
        assert 'contradictions_found' in result
        
        # Verify report file was created
        report_path = job_dir / "continuity_report.json"
        assert report_path.exists()
        
        # Verify report content
        with open(report_path) as f:
            saved_report = json.load(f)
        assert saved_report['job_id'] == 'job_001'
        assert saved_report['passed'] is True
    
    def test_check_continuity_no_script(self, tmp_path):
        job_dir = tmp_path / "job_002"
        job_dir.mkdir()
        
        # No script.md file
        result = checker.check_continuity(str(job_dir))
        
        assert result['passed'] is False
        assert 'No script found' in result['blockers']
        assert len(result['blockers']) == 1
    
    def test_check_continuity_short_script(self, tmp_path):
        job_dir = tmp_path / "job_003"
        job_dir.mkdir()
        
        script_content = "Short script."
        
        script_path = job_dir / "script.md"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        result = checker.check_continuity(str(job_dir))
        
        # Should pass but have warnings
        assert result['passed'] is True  # No blockers
        assert len(result['warnings']) > 0
        assert 'Script seems very short' in result['warnings']
    
    def test_check_continuity_report_fields(self, tmp_path):
        job_dir = tmp_path / "job_004"
        job_dir.mkdir()
        
        script_content = "A" * 150  # Long enough to pass length check
        
        script_path = job_dir / "script.md"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        result = checker.check_continuity(str(job_dir))
        
        # Verify all required fields are present
        assert 'job_id' in result
        assert 'passed' in result
        assert 'blockers' in result
        assert 'warnings' in result
        assert 'issues' in result
        assert 'entities_extracted' in result
        assert 'contradictions_found' in result
        
        # Verify field types
        assert isinstance(result['passed'], bool)
        assert isinstance(result['blockers'], list)
        assert isinstance(result['warnings'], list)
        assert isinstance(result['issues'], list)
        assert isinstance(result['entities_extracted'], int)
        assert isinstance(result['contradictions_found'], int)
    
    def test_check_continuity_creates_report_file(self, tmp_path):
        job_dir = tmp_path / "job_005"
        job_dir.mkdir()
        
        script_content = "Valid script content for testing."
        
        script_path = job_dir / "script.md"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        checker.check_continuity(str(job_dir))
        
        report_path = job_dir / "continuity_report.json"
        assert report_path.exists()
        
        # Verify JSON is valid
        with open(report_path) as f:
            report = json.load(f)
        assert 'job_id' in report
    
    def test_check_continuity_empty_script(self, tmp_path):
        job_dir = tmp_path / "job_006"
        job_dir.mkdir()
        
        script_path = job_dir / "script.md"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write("")
        
        result = checker.check_continuity(str(job_dir))
        
        # Empty script (empty string) triggers "No script found" blocker
        assert result['passed'] is False
        assert 'No script found' in result['blockers']
        assert len(result['warnings']) > 0  # Also has short script warning
    
    def test_check_continuity_minimal_valid_script(self, tmp_path):
        job_dir = tmp_path / "job_007"
        job_dir.mkdir()
        
        # Create minimal script that passes all checks
        script_content = "A" * 200  # Long enough to avoid short script warning
        
        script_path = job_dir / "script.md"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        result = checker.check_continuity(str(job_dir))
        
        assert result['passed'] is True
        assert len(result['blockers']) == 0
    
    def test_check_continuity_preserves_job_id(self, tmp_path):
        job_dir = tmp_path / "custom_job_123"
        job_dir.mkdir()
        
        script_content = "Script content."
        
        script_path = job_dir / "script.md"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        result = checker.check_continuity(str(job_dir))
        
        # Job ID should match directory name
        assert result['job_id'] == 'custom_job_123'


class TestReportStructure:
    """Test continuity report structure and content."""
    
    def test_report_has_standard_fields(self, tmp_path):
        job_dir = tmp_path / "job_008"
        job_dir.mkdir()
        
        script_content = "Test script with enough content to pass basic checks." * 5
        
        script_path = job_dir / "script.md"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        result = checker.check_continuity(str(job_dir))
        
        # Verify standard report fields
        required_fields = [
            'job_id',
            'passed',
            'blockers',
            'warnings',
            'issues',
            'entities_extracted',
            'contradictions_found'
        ]
        
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
    
    def test_report_blockers_prevent_passing(self, tmp_path):
        job_dir = tmp_path / "job_009"
        job_dir.mkdir()
        
        # Don't create script.md - should create blocker
        result = checker.check_continuity(str(job_dir))
        
        # If there are blockers, passed should be False
        if len(result['blockers']) > 0:
            assert result['passed'] is False
    
    def test_report_saved_to_file(self, tmp_path):
        job_dir = tmp_path / "job_010"
        job_dir.mkdir()
        
        script_content = "Script content for file save test."
        
        script_path = job_dir / "script.md"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        checker.check_continuity(str(job_dir))
        
        report_path = job_dir / "continuity_report.json"
        assert report_path.exists()
        
        # Verify file contains valid JSON with correct structure
        with open(report_path) as f:
            report = json.load(f)
        
        assert 'passed' in report
        assert 'blockers' in report
        assert 'warnings' in report
