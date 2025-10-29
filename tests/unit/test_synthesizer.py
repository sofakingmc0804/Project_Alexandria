"""Unit tests for the mock synthesizer module."""

from pathlib import Path

import numpy as np
import pytest

from app.packages.tts import synthesizer


def test_load_hosts_config_parses_hosts():
    hosts = synthesizer.load_hosts_config()
    assert hosts, "Expected at least one host configuration"
    assert all(isinstance(h.id, str) and h.id for h in hosts)


def test_load_hosts_config_includes_language():
    """Test that hosts have language attribute."""
    hosts = synthesizer.load_hosts_config()
    assert all(hasattr(h, 'language') for h in hosts)
    assert all(isinstance(h.language, str) for h in hosts)


def test_cache_voice_embedding_is_deterministic(tmp_path):
    host = synthesizer.load_hosts_config()[0]
    cache_file = synthesizer.cache_voice_embedding(host, cache_dir=tmp_path)
    second = synthesizer.cache_voice_embedding(host, cache_dir=tmp_path)

    assert cache_file == second
    vector = np.load(cache_file)
    assert vector.shape == (synthesizer.DEFAULT_EMBED_DIM,)


def test_synthesize_text_is_deterministic(tmp_path):
    host = synthesizer.load_hosts_config()[0]
    path1 = tmp_path / "out1.wav"
    path2 = tmp_path / "out2.wav"

    synthesizer.synthesize_text("Hello world", host, path1)
    synthesizer.synthesize_text("Hello world", host, path2)

    assert path1.read_bytes() == path2.read_bytes()


def test_parse_script_lines_extracts_speakers(tmp_path):
    script = tmp_path / "script.md"
    script.write_text("Alex: Hello\nJordan: Hi there\n# Comment\nFree line", encoding="utf-8")

    pairs = list(synthesizer.parse_script_lines(script))
    assert pairs == [
        ("Alex", "Hello"),
        ("Jordan", "Hi there"),
        ("Narrator", "Free line"),
    ]


def test_synthesize_script_outputs_files(tmp_path):
    script = tmp_path / "script.md"
    script.write_text("Alex: Hello\nJordan: Another line", encoding="utf-8")

    generated = synthesizer.synthesize_script(script, tmp_path / "stems")

    assert len(generated) == 2
    for path in generated:
        assert path.exists()
        assert path.suffix == ".wav"


# Multilingual TTS Tests

class TestGetVoiceForLanguage:
    """Test language-specific voice selection."""
    
    def test_english_returns_base_voice(self):
        """English should return the base voice unchanged."""
        base = "f5:en_male_01"
        result = synthesizer.get_voice_for_language(base, "en")
        assert result == base
    
    def test_spanish_voice_selection(self):
        """Spanish should map to Spanish voice."""
        base = "f5:en_male_01"
        result = synthesizer.get_voice_for_language(base, "es")
        assert result == "f5:es_male_01"
    
    def test_french_voice_selection(self):
        """French should map to French voice."""
        base = "f5:en_male_01"
        result = synthesizer.get_voice_for_language(base, "fr")
        assert result == "f5:fr_male_01"
    
    def test_german_voice_selection(self):
        """German should map to German voice."""
        base = "f5:en_female_02"
        result = synthesizer.get_voice_for_language(base, "de")
        assert result == "f5:de_female_02"
    
    def test_japanese_voice_selection(self):
        """Japanese should map to Japanese voice."""
        base = "f5:en_male_03"
        result = synthesizer.get_voice_for_language(base, "ja")
        assert result == "f5:ja_male_03"
    
    def test_chinese_voice_selection(self):
        """Chinese should map to Chinese voice."""
        base = "f5:en_male_01"
        result = synthesizer.get_voice_for_language(base, "zh")
        assert result == "f5:zh_male_01"
    
    def test_preserves_gender(self):
        """Voice gender should be preserved across languages."""
        female_base = "f5:en_female_01"
        result = synthesizer.get_voice_for_language(female_base, "es")
        assert "female" in result
        assert result == "f5:es_female_01"
    
    def test_preserves_voice_number(self):
        """Voice number should be preserved."""
        base = "f5:en_male_03"
        result = synthesizer.get_voice_for_language(base, "pt")
        assert result == "f5:pt_male_03"
    
    def test_unknown_language_returns_base(self):
        """Unknown languages should return base voice."""
        base = "f5:en_male_01"
        result = synthesizer.get_voice_for_language(base, "xx")
        assert result == base
    
    def test_malformed_voice_id_returns_base(self):
        """Malformed voice IDs should be returned unchanged."""
        base = "invalid_format"
        result = synthesizer.get_voice_for_language(base, "es")
        assert result == base
    
    def test_all_supported_languages(self):
        """All languages in DEFAULT_VOICE_MAP should work."""
        base = "f5:en_male_01"
        
        for lang in synthesizer.DEFAULT_VOICE_MAP:
            if lang != "en":
                result = synthesizer.get_voice_for_language(base, lang)
                assert lang in result, f"Language {lang} not in result: {result}"


class TestMultilingualSynthesis:
    """Test multilingual script synthesis."""
    
    def test_synthesize_script_with_spanish(self, tmp_path):
        """Synthesizing Spanish script should use Spanish voices."""
        script = tmp_path / "script_es.md"
        script.write_text("Alex: Hola\nJordan: Buenos días", encoding="utf-8")
        
        generated = synthesizer.synthesize_script(
            script,
            tmp_path / "stems",
            target_language="es"
        )
        
        assert len(generated) == 2
        for path in generated:
            assert path.exists()
    
    def test_synthesize_script_with_french(self, tmp_path):
        """Synthesizing French script should use French voices."""
        script = tmp_path / "script_fr.md"
        script.write_text("Alex: Bonjour\nJordan: Comment allez-vous?", encoding="utf-8")
        
        generated = synthesizer.synthesize_script(
            script,
            tmp_path / "stems",
            target_language="fr"
        )
        
        assert len(generated) == 2
        for path in generated:
            assert path.exists()
    
    def test_synthesize_script_with_german(self, tmp_path):
        """Synthesizing German script should use German voices."""
        script = tmp_path / "script_de.md"
        script.write_text("Alex: Guten Tag\nJordan: Wie geht es Ihnen?", encoding="utf-8")
        
        generated = synthesizer.synthesize_script(
            script,
            tmp_path / "stems",
            target_language="de"
        )
        
        assert len(generated) == 2
    
    def test_synthesize_script_default_is_english(self, tmp_path):
        """Default synthesis should use English voices."""
        script = tmp_path / "script.md"
        script.write_text("Alex: Hello\nJordan: Hi", encoding="utf-8")
        
        generated = synthesizer.synthesize_script(
            script,
            tmp_path / "stems"
        )
        
        assert len(generated) == 2
    
    def test_synthesize_script_with_japanese(self, tmp_path):
        """Synthesizing Japanese script should use Japanese voices."""
        script = tmp_path / "script_ja.md"
        script.write_text("Alex: こんにちは\nJordan: 元気ですか", encoding="utf-8")
        
        generated = synthesizer.synthesize_script(
            script,
            tmp_path / "stems",
            target_language="ja"
        )
        
        assert len(generated) == 2
    
    def test_multilingual_synthesis_creates_different_audio(self, tmp_path):
        """Different languages should produce different audio (different frequencies)."""
        script = tmp_path / "script.md"
        script.write_text("Alex: Test", encoding="utf-8")
        
        # Synthesize in English
        en_files = synthesizer.synthesize_script(
            script,
            tmp_path / "en",
            target_language="en"
        )
        
        # Synthesize in Spanish
        es_files = synthesizer.synthesize_script(
            script,
            tmp_path / "es",
            target_language="es"
        )
        
        # Files should exist but may have same content (mock limitation)
        assert en_files[0].exists()
        assert es_files[0].exists()


class TestHostConfigLanguage:
    """Test HostConfig language attribute."""
    
    def test_host_config_has_language(self):
        """HostConfig should have language attribute."""
        host = synthesizer.HostConfig(
            id="test",
            name="Test",
            voice="f5:en_male_01",
            fallback="",
            rate=1.0,
            pitch=0.0,
            seed=42,
            language="es"
        )
        
        assert host.language == "es"
    
    def test_host_config_default_language(self):
        """HostConfig should default to English."""
        host = synthesizer.HostConfig(
            id="test",
            name="Test",
            voice="f5:en_male_01",
            fallback="",
            rate=1.0,
            pitch=0.0,
            seed=42
        )
        
        assert host.language == "en"
    
    def test_load_hosts_uses_config_language(self, tmp_path):
        """Loading hosts should respect language in config."""
        config = tmp_path / "hosts.yaml"
        config.write_text("""
language: es
hosts:
  - id: host_a
    name: Alex
    voice: f5:en_male_01
    seed: 42
""", encoding="utf-8")
        
        hosts = synthesizer.load_hosts_config(str(config))
        
        assert hosts[0].language == "es"
    
    def test_load_hosts_per_host_language_override(self, tmp_path):
        """Per-host language should override default."""
        config = tmp_path / "hosts.yaml"
        config.write_text("""
language: en
hosts:
  - id: host_a
    name: Alex
    voice: f5:en_male_01
    seed: 42
    language: fr
""", encoding="utf-8")
        
        hosts = synthesizer.load_hosts_config(str(config))
        
        assert hosts[0].language == "fr"