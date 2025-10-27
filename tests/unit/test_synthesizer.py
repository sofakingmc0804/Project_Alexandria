"""Unit tests for the mock synthesizer module."""

from pathlib import Path

import numpy as np

from app.packages.tts import synthesizer


def test_load_hosts_config_parses_hosts():
    hosts = synthesizer.load_hosts_config()
    assert hosts, "Expected at least one host configuration"
    assert all(isinstance(h.id, str) and h.id for h in hosts)


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