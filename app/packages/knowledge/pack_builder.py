"""
Knowledge Pack Builder - Assembles knowledge packs for RAG
Filters by TOPIC+LANG, selects 12 items 100MB, writes YAML
"""
import argparse
import csv
from pathlib import Path
import yaml

CATALOG_PATH = Path("knowledge/catalog/source_catalog.csv")
SOURCES_CLEAN_PATH = Path("knowledge/sources_clean")
PACKS_PATH = Path("knowledge/packs")

MAX_ITEMS = 12
MAX_SIZE_MB = 100

def build_pack(topic: str, lang: str) -> int:
    """Build knowledge pack for topic and language."""
    if not CATALOG_PATH.exists():
        print(" Catalog not found")
        return 1
    
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Filter by topic and language
    candidates = [
        row for row in rows
        if row["topic"] == topic and row["language"] == lang and row["is_duplicate"] == "false"
    ]
    
    if not candidates:
        print(f" No sources found for topic={topic}, lang={lang}")
        return 1
    
    # Sort by quality score (descending)
    candidates.sort(key=lambda r: int(r.get("quality_score") or 0), reverse=True)
    
    # Select top items within constraints
    selected = []
    total_size = 0
    
    for row in candidates:
        if len(selected) >= MAX_ITEMS:
            break
        
        file_size = int(row["file_size_bytes"])
        if total_size + file_size > MAX_SIZE_MB * 1024 * 1024:
            continue
        
        selected.append(row)
        total_size += file_size
    
    if not selected:
        print(f" No sources fit within constraints")
        return 1
    
    # Build pack manifest
    pack = {
        "name": f"{topic}_{lang}_pack",
        "topic": topic,
        "language": lang,
        "created": Path().cwd().name,  # Placeholder
        "sources": [
            {
                "file_path": row["file_path"],
                "sha256": row["sha256"],
                "quality_score": int(row.get("quality_score") or 0)
            }
            for row in selected
        ],
        "total_sources": len(selected),
        "total_size_mb": round(total_size / (1024 * 1024), 2)
    }
    
    # Write pack YAML
    PACKS_PATH.mkdir(parents=True, exist_ok=True)
    pack_path = PACKS_PATH / f"{topic}_{lang}.yaml"
    
    with open(pack_path, "w", encoding="utf-8") as f:
        yaml.dump(pack, f, default_flow_style=False)
    
    print(f" Created pack: {pack_path.name}")
    print(f"  Sources: {len(selected)}")
    print(f"  Total size: {pack['total_size_mb']} MB")
    
    return 0

def main():
    parser = argparse.ArgumentParser(description="Build knowledge pack")
    parser.add_argument("--topic", required=True, help="Topic category")
    parser.add_argument("--lang", required=True, help="Language code")
    
    args = parser.parse_args()
    return build_pack(args.topic, args.lang)

if __name__ == "__main__":
    import sys
    sys.exit(main())
