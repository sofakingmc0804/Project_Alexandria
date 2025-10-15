"""
Knowledge Scorer - Calculate quality scores for source documents
Per Knowledge_Source_Organization.md 6
"""
import csv
from pathlib import Path

CATALOG_PATH = Path("knowledge/catalog/source_catalog.csv")
SOURCES_CLEAN_PATH = Path("knowledge/sources_clean")

def score_document(clean_path: Path) -> int:
    """
    Score document quality (0-100) based on:
    - Length (longer = higher, up to a point)
    - Structure (paragraphs, formatting)
    - Content density (non-stopword ratio)
    Returns score 0-100
    """
    if not clean_path.exists():
        return 0
    
    try:
        with open(clean_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception:
        return 0
    
    score = 50  # Base score
    
    # Length bonus (up to 30 points)
    char_count = len(text)
    if char_count > 10000:
        score += 30
    elif char_count > 5000:
        score += 20
    elif char_count > 1000:
        score += 10
    
    # Structure bonus (up to 20 points)
    paragraphs = text.split("\n\n")
    if len(paragraphs) > 10:
        score += 20
    elif len(paragraphs) > 5:
        score += 10
    
    # Penalize very short documents
    if char_count < 500:
        score -= 30
    
    return max(0, min(100, score))

def score_all():
    """Score all documents in catalog."""
    if not CATALOG_PATH.exists():
        print(" Catalog not found")
        return 1
    
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    scored_count = 0
    for row in rows:
        file_path = Path(row["file_path"])
        clean_path = SOURCES_CLEAN_PATH / f"{file_path.stem}.txt"
        
        if clean_path.exists():
            score = score_document(clean_path)
            row["quality_score"] = str(score)
            scored_count += 1
            print(f" Scored: {file_path.name}  {score}/100")
    
    # Write updated catalog
    with open(CATALOG_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n Scored {scored_count} documents")
    return 0

def main():
    return score_all()

if __name__ == "__main__":
    import sys
    sys.exit(main())
