"""Unit tests for the notes generator module."""

from pathlib import Path

from app.packages.exporters import notes_generator


def test_generate_notes_creates_markdown(tmp_path):
    script = tmp_path / "script.md"
    script.write_text(
        """# Title
## Chapter One
Key insight

## Chapter Two
Another insight
""",
        encoding="utf-8",
    )

    notes_path = tmp_path / "notes.md"
    notes_generator.generate_notes(script, notes_path)

    output = notes_path.read_text(encoding="utf-8").splitlines()
    assert output[0] == "# Show Notes"
    assert "## Chapter 1" in output
    assert "- Key insight" in output
    assert "## Chapter 2" in output
    assert "- Another insight" in output


def test_generate_notes_ignores_empty_lines(tmp_path):
    script = tmp_path / "script.md"
    script.write_text("\n# Heading\n\nPoint one\n\n", encoding="utf-8")

    notes_path = tmp_path / "notes.md"
    notes_generator.generate_notes(script, notes_path)

    content = notes_path.read_text(encoding="utf-8")
    assert "Point one" in content
    assert "Heading" not in content