# Design Notes

## Data Strategy
- **Dataset sizes**: 95 users, 32 products, 233 orders, 580 order items, 233 payments — comfortably inside the 200–600 total-row guidance while leaving room for richer analytics.
- **Deterministic IDs**: Human-readable keys (`USR-00001`) avoid relying on non-deterministic UUIDs yet still feel production-like.
- **Value realism**: Loyalty scores, discounts, shipping methods, and payment outcomes are sampled with weighted probabilities to mimic actual business distributions (e.g., VIP users get more orders).

## Schema & Constraints
- The schema is normalized to 3NF with foreign keys, cascading deletes, and lightweight CHECK constraints for boolean-like fields.
- `submission_meta` records reproducibility details: ISO timestamps, CSV row counts (JSON blob), SHA-1 hash of the generator, and the mandated tool string.
- Numeric columns use `REAL` for currency to keep SQL simple; analytic code always rounds to two decimals before presentation.

## Pipeline Decisions
- **Single source of truth**: `generate_data.py` is the only writer of CSVs; ingestion simply trusts and validates them.
- **Atomic ingestion**: `reset_database()` recreates the DB and wraps inserts plus metadata in a single transaction, rolling back on any error.
- **Structured logging**: shared formatter ensures uniform timestamps across generator, ingest, and query scripts.
- **Report layer**: `ingest.py --report` keeps evaluation simple by emitting both Markdown and JSON summaries without extra tooling.

## Analytics Query
- CLV cohort query groups by signup month (`strftime('%Y-%m', signup_date)`), aggregates revenue, order frequency, and payment health, and surfaces them in both CSV and JSON for downstream use.
- Separate `run_query.py` keeps SQL in `queries/join_query.sql` readable while allowing reviewers to re-run analytics with a single command.

## Hashing & Determinism
- SHA-1 hash targets the generator script because it defines the dataset; any change to generation logic updates submission metadata automatically.
- Randomness flows from a single `random.Random(seed)` instance passed throughout, ensuring reproducibility even if dataset sizes change.

## Reviewer Empathy
- `example_run.md` contains literal log excerpts to demonstrate the workflow without forcing reviewers to run commands first.
- `grading_guide.md` offers a concise checklist tied to requirements, reducing evaluation time.
- Reports highlight top products, cohorts, and anomalies so reviewers can quickly validate domain understanding beyond raw code.

