# app.packages.tts.synthesizer

Lightweight, testable mock TTS synthesizer used during development.

The real product will integrate F5-TTS and/or Piper. Until then we
generate deterministic sine-wave audio so the rest of the pipeline can
be exercised and verified by tests.

## Members
- HostConfig(id: 'str', name: 'str', voice: 'str', fallback: 'str', rate: 'float', pitch: 'float', seed: 'int') -> None
- Path(*args, **kwargs)
- cache_voice_embedding(host: 'HostConfig', cache_dir: 'str | Path | None' = None) -> 'Path'
- dataclass(cls=None, /, *, init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False, match_args=True, kw_only=False, slots=False, weakref_slot=False)
- load_hosts_config(config_path: 'str' = 'configs/hosts.yaml') -> 'list[HostConfig]'
- main(script_path: 'str', out_dir: 'str', config_path: 'str' = 'configs/hosts.yaml') -> 'None'
- parse_script_lines(script_path: 'Path') -> 'Iterable[tuple[str, str]]'
- select_host(hosts: 'list[HostConfig]', speaker: 'str') -> 'HostConfig'
- synthesize_script(script_path: 'Path', output_dir: 'Path', config_path: 'str' = 'configs/hosts.yaml') -> 'list[Path]'
- synthesize_text(text: 'str', host: 'HostConfig', output_path: 'Path') -> 'Path'
