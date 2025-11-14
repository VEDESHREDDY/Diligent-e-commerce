# Example Run (Seed 42)

All commands executed from `project/`.

## 1. Generate Data
```
python generate_data.py --generate --seed 42
2025-11-14 15:07:59 | INFO | data_generation | Generating datasets in ...\project
2025-11-14 15:07:59 | INFO | data_generation | Wrote users.csv (95 rows)
2025-11-14 15:08:00 | INFO | data_generation | Wrote payments.csv (233 rows)
2025-11-14 15:08:00 | INFO | data_generation | Generation complete. Total rows: 1173
```

## 2. Ingest
```
python ingest.py --ingest
2025-11-14 15:08:11 | INFO | ingest | Database schema applied.
2025-11-14 15:08:11 | INFO | ingest | Ingestion completed successfully.
```

## 3. Reporting
```
python ingest.py --report
2025-11-14 15:08:20 | INFO | ingest | Writing report outputs.
2025-11-14 15:08:20 | INFO | ingest | Report saved to report.md and report.json
```

## 4. Analytics Query
```
python run_query.py
2025-11-14 15:08:29 | INFO | run_query | Query complete. Rows: 21. Outputs: query_result.csv, query_result.json
```

## 5. Sample Outputs
- `report.md` highlights table counts (e.g., `order_items: 580`) and top revenue products.
- `query_result.csv` shows cohorts such as `2023-01` with aggregated revenue and payment success ratios.

