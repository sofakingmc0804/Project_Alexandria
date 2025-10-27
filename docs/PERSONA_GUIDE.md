# Persona Creation Guide

## Overview

Alexandria supports **unlimited personas** through a config-driven approach. Simply drop a new `.yaml` file in `configs/personas/` and it becomes immediately available.

## Current Library

Run `python scripts/list_personas.py` to see all available personas.

As of now: **10 personas** covering educational, professional, storytelling, motivational, and analytical styles.

## Creating Custom Personas

### Minimum Viable Persona

```yaml
id: my_persona
name: "My Persona Name"
description: "One-line description"

voice_config:
  primary_voice_id: "f5:en_male_01"
  fallback_voice_id: "piper:en_US-lessac-medium"
  rate: 1.0
  pitch: 0.0
  seed: 42

tone_traits:
  - trait1
  - trait2

lexical_preferences:
  encouraged_words:
    - "phrase to favor"
  avoid_phrases:
    - "phrase to avoid"

pacing:
  target_wpm: 150
  pause_after_key_points_ms: 800
  sentence_break_ms: 400

style_notes: |
  Free-form description of how this persona behaves.
```

### Field Reference

| Field | Type | Purpose | Example Values |
|-------|------|---------|----------------|
| `id` | string | Unique identifier | `academic`, `storyteller` |
| `name` | string | Display name | "Academic Presenter" |
| `description` | string | One-line summary | "Rigorous, evidence-based..." |
| `voice_config.primary_voice_id` | string | TTS voice reference | `f5:en_male_01` |
| `voice_config.rate` | float | Speech rate multiplier | 0.8-1.2 (1.0 = normal) |
| `voice_config.pitch` | float | Pitch adjustment | -0.3 to 0.3 |
| `voice_config.seed` | int | Deterministic seed | Any integer |
| `tone_traits` | list | Descriptive traits | analytical, friendly, etc. |
| `lexical_preferences.encouraged_words` | list | Phrases to favor | "let's explore" |
| `lexical_preferences.avoid_phrases` | list | Phrases to avoid | "obviously" |
| `pacing.target_wpm` | int | Words per minute | 120-180 typical |
| `pacing.pause_after_key_points_ms` | int | Pause duration | 500-1500 ms |
| `style_notes` | string | Free-form guidance | Anything goes |

### Voice Rate Guidelines

- **0.85-0.92**: Slow, contemplative (philosopher, storyteller)
- **0.93-1.02**: Normal conversational pace
- **1.03-1.10**: Energetic, enthusiastic

### WPM Guidelines

- **120-135**: Slow, reflective
- **140-155**: Moderate, clear
- **160-180**: Fast, energetic

## Advanced Patterns

### Multi-Trait Personas

Combine traits for nuanced personalities:

```yaml
tone_traits:
  - analytical      # For structure
  - empathetic      # For connection
  - motivational    # For action
```

### Lexical Transformation

The persona loader applies simple string replacement:

```yaml
lexical_preferences:
  encouraged_words:
    - "let me explain"
  avoid_phrases:
    - "obviously"  # Gets replaced with favored phrase
```

**Current limitation**: Basic string replacement. Future: LLM-based style transfer.

### Context-Aware Personas

Create specialized personas for different content types:

- `science_explainer.yaml` - For STEM topics
- `history_narrator.yaml` - For historical content
- `business_analyst.yaml` - For market analysis

## Persona Categories

Organize by use case:

### Educational
- `conversational_educator` - Friendly teacher
- `academic` - Scholarly presenter
- `technical_expert` - Deep technical dives

### Professional
- `investigative_journalist` - Hard-hitting reporting
- `mentor` - Career guidance
- `coach` - Motivational speaking

### Creative
- `storyteller` - Narrative content
- `enthusiast` - Passionate advocacy
- `philosopher` - Reflective discourse

### Casual
- `casual` - Relaxed conversation
- (Create more as needed!)

## Selection Workflow

1. **List available**: `python scripts/list_personas.py`
2. **Choose persona**: Edit `configs/output_menu.yaml`
3. **Set ID**: `persona: technical_expert`
4. **Run pipeline**: Scripter automatically loads and applies

## Testing Personas

```bash
# Test with different personas
python -c "
import yaml
cfg = yaml.safe_load(open('configs/output_menu.yaml', 'r', encoding='utf-8-sig'))
cfg['persona'] = 'storyteller'  # Change this
with open('configs/output_menu.yaml', 'w') as f:
    yaml.dump(cfg, f)
"

# Run script generation
python -c "import sys; sys.path.insert(0, '.'); from app.packages.writer.scripter import generate_script; generate_script('tests/fixtures/phase2_test')"
```

## Extending the System

### Add New Fields

The `PersonaCard` dataclass can be extended:

```python
# In persona_loader.py
@dataclass(frozen=True)
class PersonaCard:
    # ... existing fields ...
    humor_level: str | None = None  # Add new field
    formality: str | None = None
```

### Custom Rewrite Logic

Override `rewrite()` method for advanced transformations:

```python
def rewrite(self, text: str) -> str:
    # Custom logic here
    if self.humor_level == "high":
        text = self.add_humor(text)
    return self._replace_terms(text)
```

### LLM-Based Style Transfer (Future)

Replace simple string matching with LLM prompts:

```python
def rewrite(self, text: str) -> str:
    prompt = f"Rewrite in {self.display_name} style: {text}"
    return llm.generate(prompt, traits=self.tone_traits)
```

## Best Practices

1. **Start with examples**: Copy an existing persona and modify
2. **Test incrementally**: Change one field at a time
3. **Use descriptive IDs**: `investigative_journalist` > `persona_7`
4. **Document style notes**: Help future you understand intent
5. **Version control**: Git track your personas
6. **Share discoveries**: Great personas are reusable

## No Limits!

The system has **zero hardcoded limits**. You can have:

- 10 personas ✅
- 50 personas ✅
- 500 personas ✅
- Domain-specific collections (medical, legal, technical)
- Language-specific variants (formal_es, casual_fr)
- Brand-specific voices (company_ceo, support_agent)

**The only limit is disk space and your imagination.**

## Future Enhancements

- [ ] Web UI for persona creation
- [ ] A/B testing framework
- [ ] Voice cloning integration
- [ ] Audience-adaptive selection
- [ ] Multi-speaker dialogues
- [ ] Persona blending/interpolation
- [ ] Analytics on persona performance
