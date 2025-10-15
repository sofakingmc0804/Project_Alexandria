#!/bin/bash
set -euo pipefail

# Project Alexandria - File Organization Script
# Scans Downloads/Documents for relevant files and organizes them into sources/

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Scanning for files to organize..."

# Define source paths (adjust for WSL/Windows paths)
DOWNLOADS_PATH="/mnt/c/Users/Couch/Downloads"
DOCUMENTS_PATH="/mnt/c/Users/Couch/Documents"

# Counters
PDF_COUNT=0
DOCX_COUNT=0
HTML_COUNT=0
AUDIO_COUNT=0
VIDEO_COUNT=0
SKIPPED_COUNT=0

# Function to copy file with metadata tracking
organize_file() {
  local src="$1"
  local category="$2"
  local filename=$(basename "$src")
  local dest="sources/$category/$filename"

  # Skip if already exists
  if [ -f "$dest" ]; then
    echo "  ⊘ Skipping (already exists): $filename"
    ((SKIPPED_COUNT++))
    return
  fi

  # Copy file
  cp "$src" "$dest"

  # Create metadata entry
  local hash=$(sha256sum "$dest" | cut -d' ' -f1)
  local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  cat >> .metadata/catalogs/ingested_files.jsonl <<EOF
{"filename": "$filename", "category": "$category", "sha256": "$hash", "ingested_at": "$timestamp", "source_path": "$src"}
EOF

  echo "  ✓ Organized: $filename → sources/$category/"
}

# Scan Downloads directory
if [ -d "$DOWNLOADS_PATH" ]; then
  echo ""
  echo "Scanning Downloads directory..."

  # PDFs
  while IFS= read -r -d '' file; do
    organize_file "$file" "pdfs"
    ((PDF_COUNT++))
  done < <(find "$DOWNLOADS_PATH" -maxdepth 2 -type f -iname "*.pdf" -print0 2>/dev/null || true)

  # DOCX files
  while IFS= read -r -d '' file; do
    organize_file "$file" "docs"
    ((DOCX_COUNT++))
  done < <(find "$DOWNLOADS_PATH" -maxdepth 2 -type f \( -iname "*.docx" -o -iname "*.doc" -o -iname "*.odt" \) -print0 2>/dev/null || true)

  # HTML files
  while IFS= read -r -d '' file; do
    organize_file "$file" "html"
    ((HTML_COUNT++))
  done < <(find "$DOWNLOADS_PATH" -maxdepth 2 -type f \( -iname "*.html" -o -iname "*.htm" \) -print0 2>/dev/null || true)

  # Audio files (MP3, WAV, M4A, OGG, OPUS)
  while IFS= read -r -d '' file; do
    organize_file "$file" "audio"
    ((AUDIO_COUNT++))
  done < <(find "$DOWNLOADS_PATH" -maxdepth 2 -type f \( -iname "*.mp3" -o -iname "*.wav" -o -iname "*.m4a" -o -iname "*.ogg" -o -iname "*.opus" \) -print0 2>/dev/null || true)

  # Video files (MP4, WEBM, MKV, MOV)
  while IFS= read -r -d '' file; do
    organize_file "$file" "video"
    ((VIDEO_COUNT++))
  done < <(find "$DOWNLOADS_PATH" -maxdepth 2 -type f \( -iname "*.mp4" -o -iname "*.webm" -o -iname "*.mkv" -o -iname "*.mov" \) -print0 2>/dev/null || true)
fi

# Scan Documents directory
if [ -d "$DOCUMENTS_PATH" ]; then
  echo ""
  echo "Scanning Documents directory..."

  # PDFs
  while IFS= read -r -d '' file; do
    organize_file "$file" "pdfs"
    ((PDF_COUNT++))
  done < <(find "$DOCUMENTS_PATH" -maxdepth 2 -type f -iname "*.pdf" -print0 2>/dev/null || true)

  # DOCX files
  while IFS= read -r -d '' file; do
    organize_file "$file" "docs"
    ((DOCX_COUNT++))
  done < <(find "$DOCUMENTS_PATH" -maxdepth 2 -type f \( -iname "*.docx" -o -iname "*.doc" -o -iname "*.odt" \) -print0 2>/dev/null || true)

  # HTML files
  while IFS= read -r -d '' file; do
    organize_file "$file" "html"
    ((HTML_COUNT++))
  done < <(find "$DOCUMENTS_PATH" -maxdepth 2 -type f \( -iname "*.html" -o -iname "*.htm" \) -print0 2>/dev/null || true)
fi

echo ""
echo "═══════════════════════════════════════"
echo "File Organization Summary"
echo "═══════════════════════════════════════"
echo "  PDFs:        $PDF_COUNT"
echo "  Documents:   $DOCX_COUNT"
echo "  HTML:        $HTML_COUNT"
echo "  Audio:       $AUDIO_COUNT"
echo "  Video:       $VIDEO_COUNT"
echo "  Skipped:     $SKIPPED_COUNT"
echo "═══════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Review organized files in sources/ subdirectories"
echo "  2. Check .metadata/catalogs/ingested_files.jsonl for tracking"
echo "  3. Drop NotebookLM outputs into inputs/ to begin processing"
