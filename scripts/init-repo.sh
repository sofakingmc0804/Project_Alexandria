#!/bin/bash
set -euo pipefail

# Project Alexandria - Repository Initialization Script
# Creates the directory structure per SPEC.md section 3

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Initializing Project Alexandria repository structure..."

# Create main app structure
mkdir -p app/apps/{api,worker,ui}
mkdir -p app/packages/{ingest,asr,segment,embed,graph,planner,writer,continuity,rag_audit,tts,mastering,exporters,eval}

# Create config directories
mkdir -p configs/{hosts,personas,mix_profiles}

# Create data directories
mkdir -p {inputs,sources,dist,tmp}

# Create subdirectories for tmp
mkdir -p tmp/{cache,assets,intermediate}

# Create dist subdirectories for organized outputs
mkdir -p dist/{episodes,stems,promos,notes,rss}

# Create sources subdirectories for organized source materials
mkdir -p sources/{pdfs,docs,html,audio,video}

# Create metadata directory
mkdir -p .metadata/{catalogs,indexes,duplicates}

# Copy default config templates if they don't exist
if [ ! -f configs/hosts.yaml ]; then
  cat > configs/hosts.yaml <<'EOF'
hosts:
  - id: host_a
    voice: f5:en_male_01
    rate: 1.0
    pitch: 0.0
    seed: 42
  - id: host_b
    voice: f5:en_female_02
    rate: 0.98
    pitch: -0.1
language: en
target_duration_minutes: 60
personas:
  style: "inquisitive, friendly, concise"
EOF
fi

if [ ! -f configs/mastering.yaml ]; then
  cat > configs/mastering.yaml <<'EOF'
lufs_target: -16
de_ess: true
limiter: true
crossfade_ms: 50
EOF
fi

if [ ! -f configs/retrieval.yaml ]; then
  cat > configs/retrieval.yaml <<'EOF'
embed_model: "bge-large-en"
db: "faiss"
top_k: 6
rerank: "bge-reranker-large"
EOF
fi

# Create README placeholders for key directories
cat > inputs/README.md <<'EOF'
# Inputs Directory
Drop NotebookLM audio/video files here for processing.
EOF

cat > sources/README.md <<'EOF'
# Sources Directory
Place source documents (PDFs, DOCX, HTML) here for RAG retrieval.
EOF

cat > dist/README.md <<'EOF'
# Distribution Directory
Final outputs (episodes, stems, promos) are exported here.
EOF

# Create .gitignore entries for data directories
if ! grep -q "/tmp/\*" .gitignore 2>/dev/null; then
  cat >> .gitignore <<'EOF'

# Data directories
/tmp/*
!/tmp/.gitkeep
/inputs/*
!/inputs/README.md
/sources/*
!/sources/README.md
/dist/*
!/dist/README.md
.metadata/catalogs/*
.metadata/indexes/*
.metadata/duplicates/*
EOF
fi

# Create .gitkeep files to preserve empty directories
find app inputs sources dist tmp .metadata -type d -exec touch {}/.gitkeep \;

echo "✓ Directory structure created"
echo "✓ Default configuration files generated"
echo "✓ Repository initialization complete"
echo ""
echo "Next steps:"
echo "  1. Review and customize configs/*.yaml files"
echo "  2. Run organize-files.sh to process existing source materials"
echo "  3. Drop NotebookLM outputs into inputs/ directory"
