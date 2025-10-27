"""Notes generator implemented with the shared pipeline base classes."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from app.packages.base import PipelineContext, PipelineStep


class NotesGeneratorStep(PipelineStep[Path, str, Path]):
    """Pipeline step that converts a script into show notes markdown."""

    def process(self, context: PipelineContext, input_data: Path) -> str:
        lines = input_data.read_text(encoding="utf-8").splitlines()
        return "\n".join(_render_notes(lines)) + "\n"

    def after_process(self, context: PipelineContext, processed: str) -> Path:
        output_path = Path(context.params["output_path"]).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(processed, encoding="utf-8")
        return output_path


def _render_notes(lines: Iterable[str]) -> Iterable[str]:
    yield "# Show Notes"
    chapter_index = 1
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if line.startswith("##"):
            yield ""
            yield f"## Chapter {chapter_index}"
            chapter_index += 1
        elif not line.startswith("#"):
            yield f"- {line}"


def generate_notes(script_path: str | Path, notes_path: str | Path) -> Path:
    step = NotesGeneratorStep()
    script = Path(script_path).resolve()
    output = step.run(
        job_id=f"notes_{script.stem}",
        input_data=script,
        params={"output_path": Path(notes_path)},
    )
    print(f"Show notes saved to {output}")
    return output


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python notes_generator.py <script.md> <notes.md>")
        sys.exit(1)
    generate_notes(sys.argv[1], sys.argv[2])
