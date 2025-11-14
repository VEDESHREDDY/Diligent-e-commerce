import argparse
import csv
import sqlite3
from pathlib import Path

from utils.helpers import BASE_DIR, configure_logger, write_json


DB_PATH = BASE_DIR / "db" / "ecommerce.db"
QUERY_PATH = BASE_DIR / "queries" / "join_query.sql"
CSV_OUTPUT = BASE_DIR / "query_result.csv"
JSON_OUTPUT = BASE_DIR / "query_result.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run cohort CLV query.")
    parser.add_argument("--query", type=str, default=str(QUERY_PATH), help="SQL file.")
    return parser.parse_args()


def run_query(sql_path: Path):
    logger = configure_logger("run_query")
    if not DB_PATH.exists():
        raise FileNotFoundError("Database not found. Run ingestion first.")
    sql = sql_path.read_text(encoding="utf-8")
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql).fetchall()

    fieldnames = rows[0].keys() if rows else []
    CSV_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))

    write_json(JSON_OUTPUT, [dict(row) for row in rows])
    logger.info(
        "Query complete. Rows: %s. Outputs: %s, %s",
        len(rows),
        CSV_OUTPUT.name,
        JSON_OUTPUT.name,
    )


def main() -> None:
    args = parse_args()
    run_query(Path(args.query))


if __name__ == "__main__":
    main()

