#!/usr/bin/env python3
"""Persona Discovery CLI - List available personas"""
import yaml
from pathlib import Path

PERSONA_DIR = Path('configs/personas')

def list_personas():
    personas = {}
    for f in sorted(PERSONA_DIR.glob('*.yaml')):
        with open(f, 'r', encoding='utf-8-sig') as file:
            data = yaml.safe_load(file)
        if data:
            personas[f.stem] = data

    print()
    print("="*75)
    print(f"ALEXANDRIA PERSONA LIBRARY - {len(personas)} Personas Available")
    print("="*75)
    print()

    for pid, data in personas.items():
        name = data.get('name', 'N/A')
        desc = data.get('description', '')
        traits = data.get('tone_traits', [])
        trait_str = ', '.join(traits[:3])
        wpm = data.get('pacing', {}).get('target_wpm', '?')
        print(f"  {pid:30} {trait_str:40} {wpm} wpm")

    print()
    print("="*75)
    print("Usage: Set 'persona: <id>' in configs/output_menu.yaml")
    print("="*75)
    print()

if __name__ == '__main__':
    list_personas()
