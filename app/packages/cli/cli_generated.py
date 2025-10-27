"""Typer-based CLI entry points for Phase 5 modules."""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from typing import Optional

from app.packages.worker import Phase5OrchestrationError, run_full_pipeline
from app.packages.base import generate_markdown_docs, generate_stub_files


app = typer.Typer(help="Alexandria pipeline CLI")


@app.command()
def batch_synth(
    script_path: Path = typer.Argument(..., exists=True, help="Input script.md"),
    stems_dir: Path = typer.Argument(..., help="Directory to write stems"),
    config_path: Path = typer.Option(
        Path("configs/hosts.yaml"),
        "--config",
        help="Host configuration YAML",
    ),
) -> None:
    """Generate deterministic audio stems for each speaker."""

    from app.packages.tts import batch_synth as batch

    stems_dir.mkdir(parents=True, exist_ok=True)
    batch.synthesize_batch(str(script_path), str(stems_dir), str(config_path))
    typer.echo(f"✓ Stems generated in {stems_dir}")


@app.command()
def mix(
    stems_dir: Path = typer.Argument(..., exists=True, help="Input stems directory"),
    output_mix: Path = typer.Argument(..., help="Output WAV file path"),
) -> None:
    """Mix stems into a mastered WAV file."""

    from app.packages.mastering import mixer

    output_mix.parent.mkdir(parents=True, exist_ok=True)
    mixer.mix_stems(str(stems_dir), str(output_mix))
    typer.echo(f"✓ Mix created: {output_mix}")


@app.command()
def export_audio(
    mix_path: Path = typer.Argument(..., exists=True, help="Input mix WAV"),
    export_dir: Path = typer.Argument(..., help="Directory for exported assets"),
) -> None:
    """Export MP3/Opus derivatives and chapter metadata."""

    from app.packages.exporters import audio_exporter

    export_dir.mkdir(parents=True, exist_ok=True)
    audio_exporter.export_audio(str(mix_path), str(export_dir))
    typer.echo(f"✓ Audio exported to {export_dir}")


@app.command()
def notes(
    script_path: Path = typer.Argument(..., exists=True, help="Input script"),
    notes_path: Path = typer.Argument(..., help="Output notes markdown"),
) -> None:
    """Generate show notes markdown from the script."""

    from app.packages.exporters import notes_generator

    notes_path.parent.mkdir(parents=True, exist_ok=True)
    notes_generator.generate_notes(str(script_path), str(notes_path))
    typer.echo(f"✓ Notes written to {notes_path}")


@app.command(name="generate-docs")
def generate_docs(
    output_dir: Path = typer.Option(Path("docs/_generated"), "--output-dir", help="Directory for generated Markdown documentation"),
    packages: str = typer.Option("packages", "--packages", help="Comma-separated package roots relative to app/"),
) -> None:
    """Generate Markdown documentation for the selected packages."""
    roots = [segment.strip() for segment in packages.split(',') if segment.strip()] or ['packages']
    generated = generate_markdown_docs(output_dir, roots)
    typer.echo(f"Generated {len(generated)} Markdown files in {output_dir}")


@app.command(name="generate-stubs")
def generate_stubs_cli(
    output_dir: Path = typer.Option(Path("stubs"), "--output-dir", help="Directory for generated stub files"),
    packages: str = typer.Option("packages", "--packages", help="Comma-separated package roots relative to app/"),
) -> None:
    """Generate .pyi stub files for the selected packages."""
    roots = [segment.strip() for segment in packages.split(',') if segment.strip()] or ['packages']
    generated = generate_stub_files(output_dir, roots)
    typer.echo(f"Generated {len(generated)} stub files in {output_dir}")



@app.command(name="pipeline")
def run_pipeline(
    script_path: Path = typer.Argument(..., exists=True, help="Input script markdown"),
    work_dir: Path = typer.Option(Path("tmp/phase5"), "--work-dir", help="Directory for intermediate stems/mix"),
    export_dir: Path = typer.Option(Path("dist/export/phase5"), "--export-dir", help="Directory for exported deliverables"),
    config_path: Path = typer.Option(Path("configs/hosts.yaml"), "--config", help="Host configuration YAML"),
    notes_filename: Optional[str] = typer.Option("notes.md", "--notes-name", help="Filename for generated notes within export directory"),
) -> None:
    """Execute the full Phase 5 pipeline using the async orchestrator."""

    work_dir.mkdir(parents=True, exist_ok=True)
    export_dir.mkdir(parents=True, exist_ok=True)

    stems_dir = work_dir / "stems"
    mix_path = work_dir / "mix.wav"
    notes_path = export_dir / (notes_filename or "notes.md")

    try:
        artifacts = asyncio.run(
            run_full_pipeline(
                script_path=script_path,
                stems_dir=stems_dir,
                mix_path=mix_path,
                export_dir=export_dir,
                notes_path=notes_path,
                config_path=config_path,
            )
        )
    except Phase5OrchestrationError as exc:
        typer.echo(f"✗ Pipeline failed: {exc}")
        raise typer.Exit(code=1) from exc

    typer.echo("✓ Phase 5 pipeline completed")
    typer.echo(f"  Stems directory: {artifacts.stems[0].parent if artifacts.stems else stems_dir}")
    typer.echo(f"  Mix file: {artifacts.mix_path}")
    typer.echo(f"  Export directory: {artifacts.export_dir}")
    typer.echo(f"  Notes file: {artifacts.notes_path}")
    if artifacts.summary:
        typer.echo("  Summary metrics:")
        for key, value in sorted(artifacts.summary.items()):
            typer.echo(f"    {key}: {value:.2f}")


def main() -> None:
    """Entry point for python -m app.packages.cli.cli_generated."""

    app()


if __name__ == "__main__":
    main()
