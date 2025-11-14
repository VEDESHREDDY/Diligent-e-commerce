# Diligent Synthetic Commerce Stack

This repository contains a deterministic synthetic data factory, SQLite ingestion pipeline, analytics query, and reporting layer designed for the Diligent assessment. It relies solely on the Python standard library and produces reviewer-friendly artifacts automatically.

## Quickstart

```bash
python -m venv .venv
.venv\Scripts\activate          
pip install --upgrade pip
```

All commands are run from the `project/` directory:

```bash
python generate_data.py --generate --seed 42
python ingest.py --ingest
python ingest.py --report
python run_query.py
# optional: python -m http.server --directory frontend 8000
```

## Expected Outputs

Command | Purpose | Key Artifacts
---|---|---
`python generate_data.py --generate --seed 42` | Creates deterministic CSVs | `users.csv`, `products.csv`, `orders.csv`, `order_items.csv`, `payments.csv`
`python ingest.py --ingest` | Builds SQLite DB from schema + CSV | `db/ecommerce.db`
`python ingest.py --report` | Summarizes integrity + trends | `report.md`, `report.json`
`python run_query.py` | Runs cohort CLV query | `query_result.csv`, `query_result.json`

## Repository Map

- `data_generation/generate_data.py` – deterministic CSV builder with optional seed override.
- `db/schema.sql` – normalized schema with integrity constraints.
- `db/ingest.py` – ingestion + metadata + reporting workflow.
- `queries/join_query.sql` & `queries/run_query.py` – cohort CLV analytics.
- `utils/helpers.py` – logging, hashing, and filesystem helpers.
- `tests/test_integrity.py` – minimal deterministic unit checks.
- Documentation: `design_notes.md`, `example_run.md`, `grading_guide.md`, `report.*`.
- `frontend/index.html` – ultra-light dashboard that hydrates from `report.json` and `query_result.json`.

## Testing

```bash
python -m unittest tests/test_integrity.py
```

## Lightweight Frontend

After running the CLI workflow (generate → ingest → report → query), spin up a static server:

```bash
python serve_frontend.py
```

You’ll see a message like:

```
🔌 Server running at http://localhost:8000/frontend/
```

The script automatically serves the repository root, redirects `/` to `/frontend/`, and keeps `report.json` + `query_result.json` accessible. Ensure those files exist (run ingest/report/query first), then open the printed URL.

## Design Highlights

- **Deterministic randomness** with `--seed` to guarantee reproducibility.
- **Atomic ingestion**: schema recreation + single transaction commit/rollback.
- **Submission metadata**: hashes, row counts, and tool attribution captured in `submission_meta`.
- **Reviewer empathy**: generated `report.*` and `query_result.*` save analysis time, while `grading_guide.md` accelerates evaluation.

Refer to `design_notes.md` for deeper architecture decisions.

