
# CURATION_CHECKLIST.md

Use this checklist when adding or updating sources.

## Registration
- [ ] Copy to `/sources_raw`; do **not** overwrite existing files.
- [ ] Compute SHA256; populate `source_catalog.csv` with a new row.
- [ ] Assign `source_id`; detect language (BCP-47).

## Normalization
- [ ] Run GROBID (PDFs) or Unstructured (others).
- [ ] Convert to PDF/A where applicable.
- [ ] Extract clean text, headings, captions, tables.
- [ ] Generate CSL-JSON citation file.
- [ ] Save cleaned artifact to `/sources_clean`.

## Enrichment & Dedup
- [ ] Resolve DOI/arXiv; fetch enriched metadata.
- [ ] Compute SimHash/MinHash and dedupe within topic.
- [ ] Mark canonical edition and archive alternates.

## Scoring & Pack Prep
- [ ] Score quality; confirm thresholds.
- [ ] Tag topics with `ONTOLOGY.yaml` terms.
- [ ] Create/update Pack YAML with ≤ 12 items.
- [ ] Re-run QC report; no blocked items.

## Finalize
- [ ] Commit catalog & manifests.
- [ ] Export Pack manifest hash for audit trail.
