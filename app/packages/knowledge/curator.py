"""
Knowledge Curator - Manages source document ingestion
Copies files to sources_raw/, computes SHA256, detects language, updates catalog
"""
import argparse
import csv
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from langdetect import detect
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("⚠ langdetect not installed, defaulting to 'en' for all files")

CATALOG_PATH = Path("knowledge/catalog/source_catalog.csv")
SOURCES_RAW_PATH = Path("knowledge/sources_raw")

def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def detect_language_from_file(file_path: Path) -> str:
    """Detect language from text content."""
    if not LANGDETECT_AVAILABLE:
        return "en"
    
    try:
        # For text files, read and detect
        if file_path.suffix.lower() in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                sample = f.read(1000)  # First 1000 chars
                return detect(sample)
        # For PDFs/docs, will need extraction (handled in normalizer.py)
        # For now, default to 'en'
        return "en"
    except Exception:
        return "en"

def add_to_catalog(
    file_path: Path,
    sha256: str,
    file_size: int,
    language: str,
    topic: str,
    status: str = "raw"
) -> None:
    """Append entry to catalog CSV."""
    # Check if catalog needs header
    needs_header = not CATALOG_PATH.exists() or CATALOG_PATH.stat().st_size == 0
    
    with open(CATALOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Write header if needed
        if needs_header:
            writer.writerow([
                "file_path", "sha256", "file_size_bytes", "language",
                "topic", "quality_score", "is_duplicate", "duplicate_of",
                "date_added", "last_processed", "status", "processing_notes"
            ])
        
        # Write entry
        writer.writerow([
            str(file_path),
            sha256,
            file_size,
            language,
            topic,
            "",  # quality_score (filled by scorer.py)
            "false",  # is_duplicate (filled by deduplicator.py)
            "",  # duplicate_of
            datetime.now().isoformat(),  # Fixed deprecated utcnow
            "",  # last_processed
            status,
            ""  # processing_notes
        ])

def curate_file(source_path: Path, topic: str) -> bool:
    """
    Curate a single source file.
    Returns True if successful.
    """
    if not source_path.exists():
        print(f" File not found: {source_path}")
        return False
    
    # Compute hash
    sha256 = compute_sha256(source_path)
    file_size = source_path.stat().st_size
    
    # Detect language
    language = detect_language_from_file(source_path)
    
    # Copy to sources_raw with hash prefix
    dest_name = f"{sha256[:8]}_{source_path.name}"
    dest_path = SOURCES_RAW_PATH / dest_name
    
    if dest_path.exists():
        print(f" File already curated: {dest_name}")
        return True
    
    # Copy file
    SOURCES_RAW_PATH.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, dest_path)
    
    # Add to catalog
    add_to_catalog(
        file_path=dest_path,
        sha256=sha256,
        file_size=file_size,
        language=language,
        topic=topic
    )
    
    print(f" Curated: {source_path.name}  {dest_name}")
    print(f"  SHA256: {sha256}")
    print(f"  Size: {file_size:,} bytes")
    print(f"  Language: {language}")
    print(f"  Topic: {topic}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Curate source documents")
    parser.add_argument("files", nargs="+", help="Files to curate")
    parser.add_argument("--topic", required=True, help="Topic category")
    
    args = parser.parse_args()
    
    success_count = 0
    for file_str in args.files:
        file_path = Path(file_str)
        if curate_file(file_path, args.topic):
            success_count += 1
    
    print(f"\n Curated {success_count}/{len(args.files)} files")
    return 0 if success_count == len(args.files) else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
