# app.packages.cli.cli_generated

Typer-based CLI entry points for Phase 5 modules.

## Members
- Path(*args, **kwargs)
- Phase5OrchestrationError()
- batch_synth(script_path: 'Path' = <typer.models.ArgumentInfo object at 0x000001C6BB9A3770>, stems_dir: 'Path' = <typer.models.ArgumentInfo object at 0x000001C6ACA50E10>, config_path: 'Path' = <typer.models.OptionInfo object at 0x000001C6ACA50CD0>) -> 'None'
- export_audio(mix_path: 'Path' = <typer.models.ArgumentInfo object at 0x000001C6BB9B7250>, export_dir: 'Path' = <typer.models.ArgumentInfo object at 0x000001C6BB9B7390>) -> 'None'
- generate_docs(output_dir: 'Path' = <typer.models.OptionInfo object at 0x000001C6BB9B7890>, packages: 'str' = <typer.models.OptionInfo object at 0x000001C6BB9B79D0>) -> 'None'
- generate_markdown_docs(output_dir: 'Path', package_roots: 'Sequence[str]') -> 'list[Path]'
- generate_stub_files(output_dir: 'Path', package_roots: 'Sequence[str]') -> 'list[Path]'
- generate_stubs_cli(output_dir: 'Path' = <typer.models.OptionInfo object at 0x000001C6BB9B7B10>, packages: 'str' = <typer.models.OptionInfo object at 0x000001C6BB9B7C50>) -> 'None'
- main() -> 'None'
- mix(stems_dir: 'Path' = <typer.models.ArgumentInfo object at 0x000001C6BB9B6D50>, output_mix: 'Path' = <typer.models.ArgumentInfo object at 0x000001C6BB9B6FD0>) -> 'None'
- notes(script_path: 'Path' = <typer.models.ArgumentInfo object at 0x000001C6BB9B7610>, notes_path: 'Path' = <typer.models.ArgumentInfo object at 0x000001C6BB9B7750>) -> 'None'
- run_full_pipeline(script_path: 'Path', stems_dir: 'Path', mix_path: 'Path', export_dir: 'Path', notes_path: 'Path', *, config_path: 'Path' = WindowsPath('configs/hosts.yaml'), segments: 'Optional[Sequence[Segment | dict]]' = None, chapters: 'Optional[Sequence[Chapter | dict]]' = None, existing_qc_report: 'Optional[QCReport | dict]' = None) -> 'Phase5Artifacts'
- run_pipeline(script_path: 'Path' = <typer.models.ArgumentInfo object at 0x000001C6BB9B7D90>, work_dir: 'Path' = <typer.models.OptionInfo object at 0x000001C6BB9B7ED0>, export_dir: 'Path' = <typer.models.OptionInfo object at 0x000001C6BBAA0050>, config_path: 'Path' = <typer.models.OptionInfo object at 0x000001C6BBAA0190>, notes_filename: 'Optional[str]' = <typer.models.OptionInfo object at 0x000001C6BBAA02D0>) -> 'None'
