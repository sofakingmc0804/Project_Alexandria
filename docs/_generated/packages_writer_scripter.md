# app.packages.writer.scripter

## Members
- Any(*args, **kwargs)
- Path(*args, **kwargs)
- PersonaCard(id: 'str', display_name: 'str | None', voice_id: 'str | None', fallback_voice_id: 'str | None', lexical_favor: 'tuple[str, ...]', lexical_avoid: 'tuple[str, ...]', tone_traits: 'tuple[str, ...]', style_notes: 'str | None') -> None
- choose_persona(personas: 'Mapping[str, PersonaCard]', persona_id: 'str') -> 'PersonaCard | None'
- generate_script(job_dir: 'str | Path') -> 'Mapping[str, Any]'
- load_hosts(config_path: 'Path' = WindowsPath('configs/hosts.yaml')) -> 'Mapping[str, Any]'
- load_persona_cards(directory: 'Path' = WindowsPath('configs/personas')) -> 'dict[str, PersonaCard]'
- load_selection(job_dir: 'Path') -> 'Mapping[str, Any]'
- rewrite_with_persona(text: 'str', persona: 'PersonaCard | None', host_name: 'str') -> 'str'
