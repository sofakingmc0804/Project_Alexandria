#!/usr/bin/env python3
"""
Translation module using NLLB-200 (No Language Left Behind).

Translates script.md files to target languages while preserving:
- Markdown structure (chapter headings, speaker tags)
- Speaker names
- Formatting
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping

import yaml


# NLLB-200 language code mapping (subset of most common languages)
NLLB_LANG_CODES = {
    'en': 'eng_Latn',  # English
    'es': 'spa_Latn',  # Spanish
    'fr': 'fra_Latn',  # French
    'de': 'deu_Latn',  # German
    'zh': 'zho_Hans',  # Chinese (Simplified)
    'ja': 'jpn_Jpan',  # Japanese
    'ko': 'kor_Hang',  # Korean
    'pt': 'por_Latn',  # Portuguese
    'ru': 'rus_Cyrl',  # Russian
    'ar': 'arb_Arab',  # Arabic
    'hi': 'hin_Deva',  # Hindi
    'it': 'ita_Latn',  # Italian
    'nl': 'nld_Latn',  # Dutch
    'pl': 'pol_Latn',  # Polish
    'tr': 'tur_Latn',  # Turkish
    'vi': 'vie_Latn',  # Vietnamese
    'th': 'tha_Thai',  # Thai
    'id': 'ind_Latn',  # Indonesian
    'sv': 'swe_Latn',  # Swedish
    'no': 'nob_Latn',  # Norwegian
    'da': 'dan_Latn',  # Danish
    'fi': 'fin_Latn',  # Finnish
}


def load_translation_model(model_name: str = "facebook/nllb-200-distilled-600M"):
    """
    Load NLLB-200 translation model.
    
    Args:
        model_name: HuggingFace model identifier
        
    Returns:
        Tuple of (model, tokenizer) or (None, None) if unavailable
    """
    try:
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        
        print(f"Loading translation model: {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        print("✓ Translation model loaded")
        return model, tokenizer
    except ImportError:
        print("⚠ transformers library not available, translation disabled")
        return None, None
    except Exception as e:
        print(f"⚠ Failed to load translation model: {e}")
        return None, None


def get_nllb_code(lang_code: str) -> str:
    """
    Convert ISO 639-1 code to NLLB-200 language code.
    
    Args:
        lang_code: Two-letter ISO code (e.g., 'es')
        
    Returns:
        NLLB language code (e.g., 'spa_Latn')
    """
    return NLLB_LANG_CODES.get(lang_code.lower(), 'eng_Latn')


def translate_text(
    text: str,
    source_lang: str,
    target_lang: str,
    model: Any,
    tokenizer: Any,
    max_length: int = 512
) -> str:
    """
    Translate text using NLLB-200 model.
    
    Args:
        text: Text to translate
        source_lang: Source language ISO code
        target_lang: Target language ISO code
        model: NLLB model
        tokenizer: NLLB tokenizer
        max_length: Maximum sequence length
        
    Returns:
        Translated text or original if translation fails
    """
    if model is None or tokenizer is None:
        return text
    
    if not text or not text.strip():
        return text
    
    try:
        # Get NLLB language codes
        src_code = get_nllb_code(source_lang)
        tgt_code = get_nllb_code(target_lang)
        
        # Set source language for tokenizer
        tokenizer.src_lang = src_code
        
        # Tokenize input
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
        
        # Generate translation with target language forced
        translated_tokens = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.lang_code_to_id[tgt_code],
            max_length=max_length
        )
        
        # Decode translation
        translated = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
        return translated
        
    except Exception as e:
        print(f"⚠ Translation failed for text segment: {e}")
        return text


def parse_script_line(line: str) -> tuple[str, str, str]:
    """
    Parse a script line into components: prefix, speaker, content.
    
    Args:
        line: Script line (e.g., "**Alex:** Welcome to the show.")
        
    Returns:
        Tuple of (prefix, speaker_name, content)
        - prefix: Everything before content (e.g., "**Alex:** ")
        - speaker_name: Speaker name (e.g., "Alex")
        - content: Text to translate (e.g., "Welcome to the show.")
    """
    # Match pattern: **SpeakerName:** content
    # Note: Speaker name is between ** and :**
    speaker_pattern = r'^\*\*([^*:]+):\*\*\s*(.*)$'
    match = re.match(speaker_pattern, line)
    
    if match:
        speaker = match.group(1)  # "Alex"
        content = match.group(2)  # "Welcome..."
        prefix = f"**{speaker}:** "
        return prefix, speaker, content
    
    return "", "", line


def translate_script(
    script_path: str | Path,
    target_lang: str,
    source_lang: str = "en",
    output_path: str | Path | None = None,
    model: Any = None,
    tokenizer: Any = None
) -> Mapping[str, Any]:
    """
    Translate a script.md file to target language.
    
    Preserves:
    - Chapter headings structure (## Chapter N)
    - Speaker tags (**Name:**)
    - Blank lines and paragraph breaks
    
    Args:
        script_path: Path to script.md
        target_lang: Target language ISO code
        source_lang: Source language ISO code
        output_path: Optional output path (default: script_[lang].md)
        model: Pre-loaded translation model (optional)
        tokenizer: Pre-loaded tokenizer (optional)
        
    Returns:
        Dict with job_id, source_script, translated_script, target_language
    """
    script_path = Path(script_path)
    
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    # Load model if not provided
    load_model = model is None or tokenizer is None
    if load_model:
        model, tokenizer = load_translation_model()
    
    # Read source script
    source_text = script_path.read_text(encoding="utf-8")
    lines = source_text.split('\n')
    
    translated_lines: list[str] = []
    
    print(f"Translating script from {source_lang} to {target_lang}...")
    
    for i, line in enumerate(lines):
        # Skip empty lines
        if not line.strip():
            translated_lines.append(line)
            continue
        
        # Check if it's a chapter heading
        if line.startswith('##'):
            # Extract chapter title
            heading_match = re.match(r'^(##\s+)(.+)$', line)
            if heading_match:
                prefix = heading_match.group(1)
                title = heading_match.group(2)
                
                # Translate chapter title
                translated_title = translate_text(title, source_lang, target_lang, model, tokenizer)
                translated_lines.append(f"{prefix}{translated_title}")
            else:
                translated_lines.append(line)
            continue
        
        # Check if it's a speaker line
        speaker_prefix, speaker_name, content = parse_script_line(line)
        
        if speaker_prefix and content:
            # Translate content only, preserve speaker name
            translated_content = translate_text(content, source_lang, target_lang, model, tokenizer)
            translated_lines.append(f"{speaker_prefix}{translated_content}")
        else:
            # Regular text line (shouldn't happen in well-formed scripts, but handle gracefully)
            translated = translate_text(line, source_lang, target_lang, model, tokenizer)
            translated_lines.append(translated)
        
        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"  Translated {i + 1}/{len(lines)} lines...")
    
    # Join translated lines
    translated_script = '\n'.join(translated_lines)
    
    # Determine output path
    if output_path is None:
        output_path = script_path.parent / f"script_{target_lang}.md"
    else:
        output_path = Path(output_path)
    
    # Write translated script
    output_path.write_text(translated_script, encoding="utf-8")
    
    print(f"✓ Translation complete: {output_path}")
    
    return {
        "job_id": script_path.parent.name,
        "source_script": str(script_path),
        "translated_script": str(output_path),
        "source_language": source_lang,
        "target_language": target_lang,
        "line_count": len(lines)
    }


def translate_job(
    job_dir: str | Path,
    target_languages: list[str],
    source_lang: str = "en"
) -> list[Mapping[str, Any]]:
    """
    Translate script.md in a job directory to multiple target languages.
    
    Args:
        job_dir: Job directory containing script.md
        target_languages: List of target language codes
        source_lang: Source language code
        
    Returns:
        List of translation result dicts
    """
    job_path = Path(job_dir)
    script_path = job_path / "script.md"
    
    if not script_path.exists():
        raise FileNotFoundError(f"No script.md found in {job_path}")
    
    # Load model once for all translations
    model, tokenizer = load_translation_model()
    
    results = []
    
    for target_lang in target_languages:
        if target_lang.lower() == source_lang.lower():
            print(f"Skipping {target_lang} (same as source)")
            continue
        
        try:
            result = translate_script(
                script_path,
                target_lang,
                source_lang,
                model=model,
                tokenizer=tokenizer
            )
            results.append(result)
        except Exception as e:
            print(f"✗ Failed to translate to {target_lang}: {e}")
            results.append({
                "job_id": job_path.name,
                "target_language": target_lang,
                "error": str(e)
            })
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python translator.py <script.md> <target_lang> [source_lang]")
        print("Example: python translator.py job_001/script.md es en")
        sys.exit(1)
    
    script = sys.argv[1]
    target = sys.argv[2]
    source = sys.argv[3] if len(sys.argv) > 3 else "en"
    
    translate_script(script, target, source)
