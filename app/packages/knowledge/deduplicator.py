"""
Knowledge Deduplicator - Detects duplicate source documents using MinHash
Marks duplicates in catalog
"""
import csv
from pathlib import Path

try:
    from datasketch import MinHash, MinHashLSH
    DATASKETCH_AVAILABLE = True
except ImportError:
    DATASKETCH_AVAILABLE = False
    MinHash = None  # Type hint fallback
    print("⚠ datasketch not installed, deduplication disabled")

CATALOG_PATH = Path("knowledge/catalog/source_catalog.csv")
SOURCES_CLEAN_PATH = Path("knowledge/sources_clean")

SIMILARITY_THRESHOLD = 0.85  # Jaccard similarity threshold

def compute_minhash(text: str, num_perm: int = 128):
    """Compute MinHash signature for text."""
    m = MinHash(num_perm=num_perm)
    # Split into shingles (3-grams of words)
    words = text.lower().split()
    for i in range(len(words) - 2):
        shingle = " ".join(words[i:i+3])
        m.update(shingle.encode('utf-8'))
    return m

def deduplicate():
    """Find and mark duplicate documents."""
    if not DATASKETCH_AVAILABLE:
        print(" datasketch required for deduplication")
        return 1
    
    if not CATALOG_PATH.exists():
        print(" Catalog not found")
        return 1
    
    # Read catalog
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Build LSH index
    lsh = MinHashLSH(threshold=SIMILARITY_THRESHOLD, num_perm=128)
    signatures = {}
    
    print(f"Computing MinHash signatures for {len(rows)} documents...")
    
    for row in rows:
        file_path = Path(row["file_path"])
        # Use cleaned version if available
        clean_path = SOURCES_CLEAN_PATH / f"{file_path.stem}.txt"
        
        if not clean_path.exists():
            continue
        
        with open(clean_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        minhash = compute_minhash(text)
        signatures[row["sha256"]] = minhash
        lsh.insert(row["sha256"], minhash)
    
    # Find duplicates
    duplicates_found = 0
    for row in rows:
        sha256 = row["sha256"]
        if sha256 not in signatures:
            continue
        
        # Query for similar documents
        similar = lsh.query(signatures[sha256])
        
        # Remove self
        similar = [s for s in similar if s != sha256]
        
        if similar:
            row["is_duplicate"] = "true"
            row["duplicate_of"] = similar[0]  # First match
            duplicates_found += 1
            print(f" Duplicate found: {Path(row['file_path']).name}  {similar[0][:8]}")
    
    # Write updated catalog
    with open(CATALOG_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n Marked {duplicates_found} duplicates")
    return 0

def main():
    return deduplicate()

if __name__ == "__main__":
    import sys
    sys.exit(main())
