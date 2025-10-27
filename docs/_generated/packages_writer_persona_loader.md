# app.packages.writer.persona_loader

Utilities for loading and applying persona configurations.

## Members
- Any(*args, **kwargs)
- Path(*args, **kwargs)
- PersonaCard(id: 'str', display_name: 'str | None', voice_id: 'str | None', fallback_voice_id: 'str | None', lexical_favor: 'tuple[str, ...]', lexical_avoid: 'tuple[str, ...]', tone_traits: 'tuple[str, ...]', style_notes: 'str | None') -> None
- dataclass(cls=None, /, *, init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False, match_args=True, kw_only=False, slots=False, weakref_slot=False)
- discover_persona_files(directory: 'Path' = WindowsPath('configs/personas')) -> 'Iterable[Path]'
- load_persona_cards(directory: 'Path' = WindowsPath('configs/personas')) -> 'dict[str, PersonaCard]'
