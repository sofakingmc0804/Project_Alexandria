#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import yaml

from app.packages.writer.persona_loader import PersonaCard, load_persona_cards


def load_selection(job_dir: Path) -> Mapping[str, Any]:
    return json.loads((job_dir / "selection.json").read_text(encoding="utf-8"))


def load_hosts(config_path: Path = Path("configs/hosts.yaml")) -> Mapping[str, Any]:
    return yaml.safe_load(config_path.read_text(encoding="utf-8-sig"))


def load_output_menu(config_path: Path = Path("configs/output_menu.yaml")) -> Mapping[str, Any]:
    """Load output menu configuration to get persona preference"""
    return yaml.safe_load(config_path.read_text(encoding="utf-8-sig"))


def choose_persona(personas: Mapping[str, PersonaCard], persona_id: str) -> PersonaCard | None:
    return personas.get(persona_id)


def rewrite_with_persona(text: str, persona: PersonaCard | None, host_name: str) -> str:
    rewritten = text if persona is None else persona.rewrite(text)
    return f"**{host_name}:** {rewritten}"


def generate_script(job_dir: str | Path) -> Mapping[str, Any]:
    job_path = Path(job_dir)
    selection = load_selection(job_path)
    hosts_cfg = load_hosts()
    hosts = hosts_cfg.get("hosts", [])

    # Load persona from output_menu.yaml (preferred) or fallback to hosts.yaml
    output_menu = load_output_menu()
    persona_id = output_menu.get("persona", hosts_cfg.get("persona_id", "conversational_educator"))

    persona_cards = load_persona_cards()
    persona = choose_persona(persona_cards, persona_id)

    if persona:
        print(f"Using persona: {persona.display_name or persona_id}")
    else:
        print(f"Warning: Persona '{persona_id}' not found, using default")

    script_lines: list[str] = []
    host_idx = 0

    for chapter in selection.get("selection", []):
        script_lines.append(f"## {chapter['title']}\n")
        for segment in chapter.get("segments", []):
            host = hosts[host_idx % len(hosts)] if hosts else {"name": "Speaker"}
            rewritten = rewrite_with_persona(segment["text"], persona, host["name"])
            script_lines.append(rewritten + "\n")
            host_idx += 1
        script_lines.append("\n")

    script = "\n".join(script_lines)
    output_path = job_path / "script.md"
    output_path.write_text(script, encoding="utf-8")
    print(f" Generated script with {len(selection.get('selection', []))} chapters")
    return {"job_id": job_path.name, "script_path": str(output_path)}


if __name__ == "__main__":
    import sys

    generate_script(sys.argv[1] if len(sys.argv) > 1 else "tests/fixtures/phase2_test")
