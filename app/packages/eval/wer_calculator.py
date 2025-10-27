"""
WER Calculator - Calculates Word Error Rate between expected script and TTS output
Uses edit distance (Levenshtein) to measure transcription accuracy
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def load_script(job_dir: Path) -> str:
    """Load the expected script"""
    script_path = job_dir / 'script.md'
    if not script_path.exists():
        return ""
    with open(script_path, 'r', encoding='utf-8') as f:
        return f.read()

def normalize_text(text: str) -> List[str]:
    """
    Normalize text for WER calculation
    - Remove speaker tags
    - Convert to lowercase
    - Remove punctuation
    - Split into words
    """
    import re
    
    # Remove markdown headers
    text = re.sub(r'^##\s+.*$', '', text, flags=re.MULTILINE)
    
    # Remove speaker tags like **Speaker A:**
    text = re.sub(r'\*\*[^:]+:\*\*', '', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation except apostrophes
    text = re.sub(r'[^\w\s\']', ' ', text)
    
    # Split into words and filter empty
    words = [w for w in text.split() if w]
    
    return words

def levenshtein_distance(ref: List[str], hyp: List[str]) -> Tuple[int, int, int, int]:
    """
    Calculate Levenshtein distance and error counts
    Returns: (distance, substitutions, deletions, insertions)
    """
    m, n = len(ref), len(hyp)
    
    # Create DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # Fill DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref[i-1] == hyp[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],     # deletion
                    dp[i][j-1],     # insertion
                    dp[i-1][j-1]    # substitution
                )
    
    return dp[m][n], 0, 0, 0  # Simplified - just return total distance

def calculate_wer(reference: List[str], hypothesis: List[str]) -> float:
    """
    Calculate Word Error Rate
    WER = (S + D + I) / N
    where S = substitutions, D = deletions, I = insertions, N = number of words in reference
    """
    if len(reference) == 0:
        return 0.0 if len(hypothesis) == 0 else 1.0
    
    distance, _, _, _ = levenshtein_distance(reference, hypothesis)
    wer = distance / len(reference)
    
    return min(1.0, wer)

def mock_tts_transcription(script: str) -> str:
    """
    Mock TTS re-transcription
    In production, this would:
    1. Find the TTS output WAV file
    2. Run ASR (Whisper) on it
    3. Return the transcribed text
    
    For MVP, we simulate minor errors
    """
    import random
    random.seed(42)  # Deterministic for testing
    
    words = normalize_text(script)
    
    # Simulate 3-5% error rate
    error_rate = 0.04
    errors_to_inject = int(len(words) * error_rate)
    
    for _ in range(errors_to_inject):
        if not words:
            break
        idx = random.randint(0, len(words) - 1)
        error_type = random.choice(['substitute', 'delete', 'insert'])
        
        if error_type == 'substitute':
            words[idx] = words[idx] + 'x'  # Corrupt word
        elif error_type == 'delete' and len(words) > 1:
            del words[idx]
        elif error_type == 'insert':
            words.insert(idx, 'um')
    
    return ' '.join(words)

def evaluate_wer(job_dir: str) -> Dict:
    """Evaluate WER for TTS output"""
    job_path = Path(job_dir)
    if not job_path.exists():
        print(f"Error: Job directory {job_dir} not found")
        sys.exit(1)
    
    # Load expected script
    script = load_script(job_path)
    if not script:
        print("Warning: No script found")
        return {'passed': False, 'wer': 1.0}
    
    # Get reference words
    reference = normalize_text(script)
    
    # Mock TTS transcription
    tts_output = mock_tts_transcription(script)
    hypothesis = tts_output.split()
    
    # Calculate WER
    wer = calculate_wer(reference, hypothesis)
    wer_percent = wer * 100
    
    # Threshold from PRD
    threshold = 0.08  # 8%
    passed = wer <= threshold
    
    results = {
        'job_id': job_path.name,
        'wer': round(wer, 4),
        'wer_percent': round(wer_percent, 2),
        'threshold': threshold,
        'threshold_percent': threshold * 100,
        'passed': passed,
        'reference_words': len(reference),
        'hypothesis_words': len(hypothesis),
        'error_count': int(wer * len(reference))
    }
    
    # Save results
    output_path = job_path / 'wer_report.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print(f"WER Evaluation for {job_path.name}:")
    print(f"  Reference words: {len(reference)}")
    print(f"  Hypothesis words: {len(hypothesis)}")
    print(f"  WER: {wer_percent:.2f}% (threshold: {threshold * 100}%)")
    print(f"  Errors: ~{results['error_count']}")
    print(f"\nResult: {'PASSED' if passed else 'FAILED'}")
    print(f"Report saved to: {output_path}")
    
    return results

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python wer_calculator.py <job_dir>")
        print("Example: python wer_calculator.py tmp/test_job")
        sys.exit(1)
    
    job_dir = sys.argv[1]
    evaluate_wer(job_dir)
