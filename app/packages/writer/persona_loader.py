"""Utilities for loading and applying persona configurations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml


PERSONA_DIR = Path("configs/personas")


@dataclass(frozen=True)
class PersonaCard:
    id: str
    display_name: str | None
    voice_id: str | None
    fallback_voice_id: str | None
    lexical_favor: tuple[str, ...]
    lexical_avoid: tuple[str, ...]
    tone_traits: tuple[str, ...]
    style_notes: str | None

    def rewrite(self, text: str) -> str:
        return self._replace_terms(text)

    def _replace_terms(self, text: str) -> str:
        if not self.lexical_favor or not self.lexical_avoid:
            return text
        rewritten = text
        for avoid in self.lexical_avoid:
            for favor in self.lexical_favor:
                rewritten = rewritten.replace(avoid, favor)
        return rewritten


def discover_persona_files(directory: Path = PERSONA_DIR) -> Iterable[Path]:
    if directory.exists():
        yield from sorted(directory.glob("*.yaml"))


def load_persona_cards(directory: Path = PERSONA_DIR) -> dict[str, PersonaCard]:
    personas: dict[str, PersonaCard] = {}
    for path in discover_persona_files(directory):
        persona_id = path.stem
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        lexical = data.get("lexical_preferences", {})
        personas[persona_id] = PersonaCard(
            id=persona_id,
            display_name=data.get("name"),
            voice_id=(data.get("voice_config") or {}).get("primary_voice_id"),
            fallback_voice_id=(data.get("voice_config") or {}).get("fallback_voice_id"),
            lexical_favor=tuple(lexical.get("encouraged_words", []) or ()),
            lexical_avoid=tuple(lexical.get("avoid_phrases", []) or ()),
            tone_traits=tuple(data.get("tone_traits", []) or ()),
            style_notes=data.get("style_notes"),
        )
    return personas


__all__ = ["PersonaCard", "load_persona_cards", "discover_persona_files"]