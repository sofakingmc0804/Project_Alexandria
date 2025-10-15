"""
Knowledge Normalizer - Extracts text from source documents
Uses GROBID for PDFs, Unstructured for docs, outputs to sources_clean/
"""
import argparse
import csv
from pathlib import Path
from typing import Optional

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print(" PyPDF2 not installed, PDF extraction limited")

CATALOG_PATH = Path("knowledge/catalog/source_catalog.csv")
SOURCES_RAW_PATH = Path("knowledge/sources_raw")
SOURCES_CLEAN_PATH = Path("knowledge/sources_clean")

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from PDF using PyPDF2 (fallback when GROBID unavailable)."""
    if not PDF_AVAILABLE:
        return ""
    
    try:
        reader = PdfReader(pdf_path)
        text = []
        for page in reader.pages:
            text.append(page.extract_text())
        return "\n\n".join(text)
    except Exception as e:
        print(f" PDF extraction failed: {e}")
        return ""

def extract_text_from_txt(txt_path: Path) -> str:
    """Extract text from plain text file."""
    try:
        with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print(f" Text extraction failed: {e}")
        return ""

def normalize_file(raw_path: Path) -> Optional[Path]:
    """
    Extract text from source file and save to sources_clean/.
    Returns path to cleaned file or None if failed.
    """
    if not raw_path.exists():
        print(f" File not found: {raw_path}")
        return None
    
    # Determine extraction method
    suffix = raw_path.suffix.lower()
    
    if suffix == ".pdf":
        text = extract_text_from_pdf(raw_path)
    elif suffix in [".txt", ".md"]:
        text = extract_text_from_txt(raw_path)
    else:
        print(f" Unsupported file type: {suffix}")
        return None
    
    if not text.strip():
        print(f" No text extracted from {raw_path.name}")
        return None
    
    # Write to sources_clean
    SOURCES_CLEAN_PATH.mkdir(parents=True, exist_ok=True)
    clean_path = SOURCES_CLEAN_PATH / f"{raw_path.stem}.txt"
    
    with open(clean_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f" Normalized: {raw_path.name}  {clean_path.name}")
    print(f"  Extracted {len(text):,} characters")
    
    return clean_path

def normalize_all():
    """Normalize all files in catalog with status='raw'."""
    if not CATALOG_PATH.exists():
        print(" Catalog not found")
        return 1
    
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    normalized_count = 0
    for row in rows:
        if row["status"] == "raw":
            raw_path = Path(row["file_path"])
            clean_path = normalize_file(raw_path)
            if clean_path:
                normalized_count += 1
                # TODO: Update catalog status to 'cleaned'
    
    print(f"\n Normalized {normalized_count} files")
    return 0

def main():
    parser = argparse.ArgumentParser(description="Normalize source documents")
    parser.add_argument("--file", help="Specific file to normalize")
    
    args = parser.parse_args()
    
    if args.file:
        result = normalize_file(Path(args.file))
        return 0 if result else 1
    else:
        return normalize_all()

if __name__ == "__main__":
    import sys
    sys.exit(main())
