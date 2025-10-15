
# Knowledge Source Organization Plan (KSO)

This document specifies how we **organize, cleanse, normalize, and score** existing knowledge sources so NotebookLM inputs are faster to assemble and yield higher-quality outputs. It plugs directly into the PRD/SPEC/TASKS and adds concrete schemas, conventions, and operations.

---

## 1) Objectives
- **Reduce friction**: curators can locate the right sources in seconds.
- **Raise quality**: inputs are clean, deduplicated, citation-rich, and language-tagged.
- **Speed up generation**: curated “packs” reduce ingestion time in NotebookLM and downstream pipelines.
- **Enable traceability**: every output maps back to canonical sources with stable IDs and hashes.

---

## 2) Canonical Data Model

### 2.1 Entities
- **Source**: a document/audio/video/web page.
- **Edition**: a specific version of a source (by date/hash).
- **Pack**: a curated bundle of Sources for a single NotebookLM project/episode.
- **Citation**: a reference extracted from a Source (normalized to CSL JSON).

### 2.2 IDs & Fingerprints
- `source_id`: `SRC-{slug}-{nnnn}` (stable, human-readable).
- `edition_id`: `ED-{YYYYMMDD}-{short_hash}`.
- `pack_id`: `PK-{topic_slug}-{YYYYMMDD}`.
- `fingerprints`: SHA256 and *text-level SimHash/MinHash* for dedup detection.

### 2.3 Directory Layout
```
/knowledge
  /catalog/              # CSV/Parquet catalog of all sources (source_catalog.*)
  /sources_raw/          # original uploads (read-only once registered)
  /sources_clean/        # normalized outputs (PDF/A, text, images, subtitles)
  /citations/            # CSL-JSON files per source
  /packs/                # YAML manifests of curated packs
  /cache/                # lookup caches (DOI, Wayback, arXiv)
```

---

## 3) Metadata Schema (minimal, composable)

| Field | Type | Required | Description |
|---|---|---|---|
| source_id | string | ✓ | Stable ID assigned at registration |
| title | string | ✓ | Human title |
| authors | array<string> |  | Standardized “Last, First” |
| published_date | date |  | ISO 8601 |
| doi | string |  | DOI if available |
| url | string |  | Canonical link |
| file_path_raw | string | ✓ | Path in `/sources_raw` |
| file_path_clean | string |  | Path in `/sources_clean` after normalization |
| language | string | ✓ | BCP-47 tag (e.g., en, es-ES) |
| license | string |  | SPDX id or human text |
| topic_tags | array<string> | ✓ | Controlled vocabulary (see Ontology) |
| level | enum |  | beginner | intermediate | advanced |
| status | enum | ✓ | registered | cleaned | validated |
| sha256 | string | ✓ | File hash |
| simhash | string |  | Textual fingerprint |
| minhash | string |  | Textual fingerprint (LSH) |
| notes | string |  | Freeform curation notes |

> **Serialization**: CSV for quick edits; Parquet for speed/scale.

---

## 4) Ontology & Controlled Vocabularies

- **Topics**: hierarchical list (see `ONTOLOGY.yaml`).
- **Document Types**: article, chapter, dataset, lecture, podcast, video, blog, spec, repo, slide deck.
- **Pedagogy Tags**: concept, example, proof, exercise, assessment, case-study, analogy.
- **Quality Flags**: peer-reviewed, primary, secondary, retracted, paywalled, noisy-ocr, translation.

---

## 5) Normalization Pipeline

1. **Register**: copy to `/sources_raw`, compute hashes, detect language, extract rough text.
2. **Clean**:
   - PDFs → PDF/A; text via **GROBID** (scholarly) or **Unstructured** (general).
   - HTML → readability extract; strip boilerplate, banners, cookie text.
   - Audio/Video → subtitles (Whisper), speaker diarization optional.
3. **Enrich**:
   - Resolve DOI/arXiv; pull metadata; store **CSL-JSON** citation file.
   - Extract **figure/table captions**; snapshot key images (300 DPI).
   - Build **chunk boundaries**: sections, headings, tables, captions kept intact.
4. **Deduplicate**:
   - SimHash/MinHash compare within topic; auto-flag near-duplicates.
   - Prefer canonical editions (publisher DOI over preprint when appropriate).
5. **Validate**:
   - Sanity checks: language, encoding, page count, OCR confidence, citation count.
   - Assign **quality score** (see §6).

Output is written to `/sources_clean` and catalog updated.

---

## 6) Quality Scoring (0–100)

**Base (70 pts):**
- Parse integrity (headings/sections present) – 15
- OCR confidence (if OCR) – 10
- Citation extraction rate – 10
- Language detection confidence – 5
- Dedup status (unique best edition) – 10
- License clarity – 10
- Structural richness (tables, figures captured) – 10

**Bonus (30 pts):**
- Peer-reviewed – 10
- Recency (≤ 3 yrs) – 5
- Alignment with ontology topic depth – 5
- Clean captions/alt-text present – 5
- Pack-fit (matches beat-sheet needs) – 5

Thresholds:
- **≥ 85**: Prime
- **70–84**: Acceptable
- **< 70**: Needs attention (auto-excluded from “Prime” packs)

---

## 7) Packs (NotebookLM-ready Bundles)

A **Pack** is a YAML manifest listing clean sources, recommended order, and guidance:
```yaml
pack_id: PK-climate_policy-20251014
title: "Climate Policy – Foundational Pack"
language: en
goals: ["overview", "case studies", "policy mechanisms"]
sources:
  - source_id: SRC-stern_review-0001
    edition_id: ED-20061130-a1b2c3
    role: "overview"
  - source_id: SRC-paris_agreement-0007
    edition_id: ED-20151212-d4e5f6
    role: "treaty"
notebooklm_hints:
  persona: "debate"
  prompts: ["contrast carbon tax vs cap-and-trade", "common misconceptions"]
  exclusions: ["outdated pre-2010 summaries"]
```

Use Packs to drag-and-drop a small, **high-quality** set into NotebookLM.

---

## 8) Operations

### 8.1 Make Targets
- `make curate` → run registration, hashing, language detection, DOI/URL check.
- `make clean` → normalize with GROBID/Unstructured; save CSL-JSON.
- `make dedupe` → compute SimHash/MinHash; mark duplicates.
- `make score` → compute quality scores; update catalog.
- `make pack TOPIC=climate_policy LANG=en` → create Pack YAML with top-scoring sources.

### 8.2 Acceptance Criteria
- Catalog row exists for every file in `/sources_raw` with SHA256.
- 0 un-validated items in target Pack.
- Average Pack quality score ≥ 80.
- Each Pack has ≤ 12 items and ≤ 100 MB total where possible (NotebookLM-friendly).

---

## 9) Governance

- **Immutability**: never overwrite `/sources_raw`; new editions get new `edition_id`.
- **Licenses**: record SPDX or human-readable license; block items with unknown or incompatible licenses from “Prime” Packs.
- **Auditability**: every exported NotebookLM project must store Pack manifest + catalog snapshot hash.

---

## 10) Deliverables

- `source_catalog.csv` (or parquet) updated on every run.
- `ONTOLOGY.yaml` controlled vocabulary.
- `PACKS/*.yaml` curated manifests.
- `citations/*.json` CSL-JSON for each source.
- QC report: counts, quality distribution, duplicate map.

