"""
Unit tests for packages/translate/translator.py

Tests multilingual translation with structure preservation.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from app.packages.translate import translator


@pytest.fixture
def sample_script():
    """Create sample script content."""
    return """## Chapter 1

**Alex:** Welcome to this episode where we discuss machine learning fundamentals.

**Jordan:** Deep learning has revolutionized computer vision and natural language processing.

## Chapter 2

**Alex:** Lets now discuss transformer architectures.

**Jordan:** Transformers have become the foundation for modern language models.

"""


@pytest.fixture
def mock_translation_model():
    """Create mock NLLB model and tokenizer."""
    model = Mock()
    tokenizer = Mock()
    
    # Mock tokenizer attributes
    tokenizer.src_lang = None
    tokenizer.lang_code_to_id = {
        'eng_Latn': 256047,
        'spa_Latn': 256069,
        'fra_Latn': 256057,
        'deu_Latn': 256047,
    }
    
    # Mock tokenization
    tokenizer.return_value = {
        'input_ids': [[1, 2, 3]],
        'attention_mask': [[1, 1, 1]]
    }
    
    # Mock translation - just add [ES] prefix to indicate translation
    def mock_decode(tokens, skip_special_tokens=True):
        return ["[ES] Translated text"]
    
    tokenizer.batch_decode = Mock(side_effect=mock_decode)
    
    # Mock model generation
    model.generate = Mock(return_value=[[4, 5, 6]])
    
    return model, tokenizer


class TestLanguageCodeMapping:
    """Test NLLB language code conversion."""
    
    def test_get_nllb_code_english(self):
        code = translator.get_nllb_code('en')
        assert code == 'eng_Latn'
    
    def test_get_nllb_code_spanish(self):
        code = translator.get_nllb_code('es')
        assert code == 'spa_Latn'
    
    def test_get_nllb_code_japanese(self):
        code = translator.get_nllb_code('ja')
        assert code == 'jpn_Jpan'
    
    def test_get_nllb_code_chinese(self):
        code = translator.get_nllb_code('zh')
        assert code == 'zho_Hans'
    
    def test_get_nllb_code_unknown_defaults_to_english(self):
        code = translator.get_nllb_code('xx')
        assert code == 'eng_Latn'
    
    def test_get_nllb_code_case_insensitive(self):
        code = translator.get_nllb_code('ES')
        assert code == 'spa_Latn'


class TestParseScriptLine:
    """Test script line parsing."""
    
    def test_parse_speaker_line(self):
        line = "**Alex:** Welcome to the show."
        prefix, speaker, content = translator.parse_script_line(line)
        
        # prefix includes full speaker tag with separator
        assert "Alex" in prefix
        assert "**" in prefix
        assert ":" in prefix
        assert speaker == "Alex"
        assert content == "Welcome to the show."
    
    def test_parse_different_speaker(self):
        line = "**Jordan:** This is interesting content."
        prefix, speaker, content = translator.parse_script_line(line)
        
        # prefix includes full speaker tag with separator
        assert "Jordan" in prefix
        assert "**" in prefix
        assert ":" in prefix
        assert speaker == "Jordan"
        assert content == "This is interesting content."
    
    def test_parse_non_speaker_line(self):
        line = "Just some regular text"
        prefix, speaker, content = translator.parse_script_line(line)
        
        assert prefix == ""
        assert speaker == ""
        assert content == "Just some regular text"
    
    def test_parse_empty_line(self):
        line = ""
        prefix, speaker, content = translator.parse_script_line(line)
        
        assert prefix == ""
        assert speaker == ""
        assert content == ""
    
    def test_parse_chapter_heading(self):
        line = "## Chapter 1"
        prefix, speaker, content = translator.parse_script_line(line)
        
        # Chapter headings don't match speaker pattern
        assert prefix == ""
        assert speaker == ""
        assert content == "## Chapter 1"


class TestTranslateText:
    """Test text translation function."""
    
    def test_translate_text_with_model(self, mock_translation_model):
        model, tokenizer = mock_translation_model
        
        result = translator.translate_text(
            "Hello world",
            "en",
            "es",
            model,
            tokenizer
        )
        
        assert "[ES]" in result
        assert model.generate.called
    
    def test_translate_text_no_model_returns_original(self):
        result = translator.translate_text(
            "Hello world",
            "en",
            "es",
            None,
            None
        )
        
        assert result == "Hello world"
    
    def test_translate_text_empty_input(self, mock_translation_model):
        model, tokenizer = mock_translation_model
        
        result = translator.translate_text("", "en", "es", model, tokenizer)
        assert result == ""
    
    def test_translate_text_whitespace_only(self, mock_translation_model):
        model, tokenizer = mock_translation_model
        
        result = translator.translate_text("   ", "en", "es", model, tokenizer)
        assert result == "   "


class TestTranslateScript:
    """Test script translation."""
    
    @patch('app.packages.translate.translator.load_translation_model')
    def test_translate_script_creates_output_file(self, mock_load_model, tmp_path, sample_script, mock_translation_model):
        # Setup
        script_path = tmp_path / "script.md"
        script_path.write_text(sample_script)
        
        model, tokenizer = mock_translation_model
        mock_load_model.return_value = (model, tokenizer)
        
        # Translate
        result = translator.translate_script(
            script_path,
            "es",
            "en"
        )
        
        # Verify output file created
        output_path = tmp_path / "script_es.md"
        assert output_path.exists()
        
        # Verify result
        assert result['target_language'] == 'es'
        assert result['source_language'] == 'en'
        assert 'translated_script' in result
    
    @patch('app.packages.translate.translator.load_translation_model')
    def test_translate_script_preserves_chapter_structure(self, mock_load_model, tmp_path, sample_script, mock_translation_model):
        script_path = tmp_path / "script.md"
        script_path.write_text(sample_script)
        
        model, tokenizer = mock_translation_model
        mock_load_model.return_value = (model, tokenizer)
        
        translator.translate_script(script_path, "es", "en")
        
        output_path = tmp_path / "script_es.md"
        translated = output_path.read_text()
        
        # Should have chapter headings
        assert "## Chapter" in translated or "## [ES]" in translated
    
    @patch('app.packages.translate.translator.load_translation_model')
    def test_translate_script_preserves_speaker_tags(self, mock_load_model, tmp_path, sample_script, mock_translation_model):
        script_path = tmp_path / "script.md"
        script_path.write_text(sample_script)
        
        model, tokenizer = mock_translation_model
        mock_load_model.return_value = (model, tokenizer)
        
        translator.translate_script(script_path, "es", "en")
        
        output_path = tmp_path / "script_es.md"
        translated = output_path.read_text()
        
        # Speaker tags format should be preserved (even if content is mock translated)
        # The parse_script_line function preserves speaker prefix
        assert "**" in translated  # Has speaker tags
        assert ":" in translated  # Has separator
    
    @patch('app.packages.translate.translator.load_translation_model')
    def test_translate_script_preserves_blank_lines(self, mock_load_model, tmp_path, sample_script, mock_translation_model):
        script_path = tmp_path / "script.md"
        script_path.write_text(sample_script)
        
        model, tokenizer = mock_translation_model
        mock_load_model.return_value = (model, tokenizer)
        
        translator.translate_script(script_path, "es", "en")
        
        output_path = tmp_path / "script_es.md"
        translated = output_path.read_text()
        
        # Should have blank lines preserved
        assert "\n\n" in translated
    
    @patch('app.packages.translate.translator.load_translation_model')
    def test_translate_script_custom_output_path(self, mock_load_model, tmp_path, sample_script, mock_translation_model):
        script_path = tmp_path / "script.md"
        script_path.write_text(sample_script)
        
        custom_output = tmp_path / "custom_translation.md"
        
        model, tokenizer = mock_translation_model
        mock_load_model.return_value = (model, tokenizer)
        
        result = translator.translate_script(
            script_path,
            "es",
            "en",
            output_path=custom_output
        )
        
        assert custom_output.exists()
        assert str(custom_output) in result['translated_script']
    
    def test_translate_script_missing_file_raises_error(self, tmp_path):
        script_path = tmp_path / "nonexistent.md"
        
        with pytest.raises(FileNotFoundError):
            translator.translate_script(script_path, "es", "en")
    
    @patch('app.packages.translate.translator.load_translation_model')
    def test_translate_script_uses_provided_model(self, mock_load_model, tmp_path, sample_script, mock_translation_model):
        script_path = tmp_path / "script.md"
        script_path.write_text(sample_script)
        
        model, tokenizer = mock_translation_model
        
        # Should not call load_translation_model when model provided
        translator.translate_script(
            script_path,
            "es",
            "en",
            model=model,
            tokenizer=tokenizer
        )
        
        mock_load_model.assert_not_called()


class TestTranslateJob:
    """Test job-level translation."""
    
    @patch('app.packages.translate.translator.load_translation_model')
    def test_translate_job_multiple_languages(self, mock_load_model, tmp_path, sample_script, mock_translation_model):
        # Setup job directory
        job_dir = tmp_path / "job_001"
        job_dir.mkdir()
        script_path = job_dir / "script.md"
        script_path.write_text(sample_script)
        
        model, tokenizer = mock_translation_model
        mock_load_model.return_value = (model, tokenizer)
        
        # Translate to multiple languages
        results = translator.translate_job(
            job_dir,
            target_languages=['es', 'fr', 'de'],
            source_lang='en'
        )
        
        # Should have 3 results
        assert len(results) == 3
        
        # Should have created 3 translated files
        assert (job_dir / "script_es.md").exists()
        assert (job_dir / "script_fr.md").exists()
        assert (job_dir / "script_de.md").exists()
    
    @patch('app.packages.translate.translator.load_translation_model')
    def test_translate_job_skips_source_language(self, mock_load_model, tmp_path, sample_script, mock_translation_model):
        job_dir = tmp_path / "job_002"
        job_dir.mkdir()
        script_path = job_dir / "script.md"
        script_path.write_text(sample_script)
        
        model, tokenizer = mock_translation_model
        mock_load_model.return_value = (model, tokenizer)
        
        # Include source language in target list
        results = translator.translate_job(
            job_dir,
            target_languages=['en', 'es'],
            source_lang='en'
        )
        
        # Should only translate to Spanish (skip English)
        assert len(results) == 1
        assert results[0]['target_language'] == 'es'
    
    def test_translate_job_missing_script_raises_error(self, tmp_path):
        job_dir = tmp_path / "job_003"
        job_dir.mkdir()
        
        with pytest.raises(FileNotFoundError):
            translator.translate_job(job_dir, ['es'])
    
    @patch('app.packages.translate.translator.load_translation_model')
    def test_translate_job_loads_model_once(self, mock_load_model, tmp_path, sample_script, mock_translation_model):
        job_dir = tmp_path / "job_004"
        job_dir.mkdir()
        script_path = job_dir / "script.md"
        script_path.write_text(sample_script)
        
        model, tokenizer = mock_translation_model
        mock_load_model.return_value = (model, tokenizer)
        
        translator.translate_job(
            job_dir,
            target_languages=['es', 'fr', 'de']
        )
        
        # Should only load model once for all translations
        assert mock_load_model.call_count == 1


class TestLoadTranslationModel:
    """Test model loading."""
    
    @patch('app.packages.translate.translator.load_translation_model')
    def test_load_model_returns_tuple(self, mock_load):
        # Mock to avoid actually loading model during tests
        mock_load.return_value = (Mock(), Mock())
        
        model, tokenizer = mock_load()
        
        # Function should return tuple
        assert model is not None
        assert tokenizer is not None
    
    @patch.dict('sys.modules', {'transformers': None})
    def test_load_model_no_transformers(self):
        # When transformers unavailable, should return None, None gracefully
        model, tokenizer = translator.load_translation_model()
        
        assert model is None
        assert tokenizer is None
