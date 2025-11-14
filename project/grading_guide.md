# Grading Guide

Use this checklist to validate the submission quickly.

## Setup
- [ ] Repository root is `project/` with the exact structure from the brief.
- [ ] `.gitignore` ignores generated artifacts (`*.csv`, `report.*`, `query_result.*`, `db/*.db`).

## Functionality
- [ ] `python generate_data.py --generate --seed 42` reruns without manual cleanup and produces five CSVs.
- [ ] `python ingest.py --ingest` recreates `db/ecommerce.db` using `db/schema.sql`.
- [ ] `python ingest.py --report` emits both `report.md` and `report.json`.
- [ ] `python run_query.py` reads `queries/join_query.sql` and writes `query_result.*`.

## Data Integrity
- [ ] All foreign keys succeed; ingestion fails fast if a CSV is missing.
- [ ] `submission_meta` contains `student_unique_id`, `generated_timestamp`, row counts JSON, SHA-1 of generator, and `tool_used="Cursor"`.
- [ ] Reports list row counts, validation results, top products, high-value customers, payment anomalies, and cohort stats.

## Determinism
- [ ] Passing the same `--seed` regenerates the identical dataset (confirmed via identical SHA-1 hash in metadata).

## Testing & Documentation
- [ ] `python -m unittest tests/test_integrity.py` passes.
- [ ] `README.md`, `design_notes.md`, `example_run.md`, and `grading_guide.md` look professional and reference the exact commands above.

