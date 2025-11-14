import argparse
import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from utils.helpers import (
    BASE_DIR,
    DATA_FILES,
    configure_logger,
    hash_file_sha1,
    now_utc_iso,
    read_csv,
    write_json,
)


DB_PATH = BASE_DIR / "db" / "ecommerce.db"
SCHEMA_PATH = BASE_DIR / "db" / "schema.sql"
REPORT_MD = BASE_DIR / "report.md"
REPORT_JSON = BASE_DIR / "report.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest CSV files into SQLite.")
    parser.add_argument("--ingest", action="store_true", help="Run ingestion pipeline.")
    parser.add_argument("--report", action="store_true", help="Generate report output.")
    return parser.parse_args()


def load_csv_data() -> Dict[str, List[Dict[str, str]]]:
    data: Dict[str, List[Dict[str, str]]] = {}
    for filename in DATA_FILES:
        path = BASE_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Expected CSV {filename} not found in {BASE_DIR}")
        data[filename] = read_csv(path)
    return data


def reset_database(logger: logging.Logger) -> sqlite3.Connection:
    if DB_PATH.exists():
        logger.info("Removing existing database at %s", DB_PATH)
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema_sql)
    logger.info("Database schema applied.")
    return conn


def insert_data(conn: sqlite3.Connection, data: Dict[str, List[Dict[str, str]]]) -> None:
    conn.executemany(
        """
        INSERT INTO users (
            user_id, first_name, last_name, email, country, signup_date,
            segment, is_active, loyalty_score
        ) VALUES (
            :user_id, :first_name, :last_name, :email, :country, :signup_date,
            :segment, :is_active, :loyalty_score
        )
        """,
        data["users.csv"],
    )

    conn.executemany(
        """
        INSERT INTO products (
            product_id, name, category, price, currency,
            inventory_count, is_active
        ) VALUES (
            :product_id, :name, :category, :price, :currency,
            :inventory_count, :is_active
        )
        """,
        data["products.csv"],
    )

    conn.executemany(
        """
        INSERT INTO orders (
            order_id, user_id, order_date, status, shipping_method,
            discount_amount, total_amount, currency
        ) VALUES (
            :order_id, :user_id, :order_date, :status, :shipping_method,
            :discount_amount, :total_amount, :currency
        )
        """,
        data["orders.csv"],
    )

    conn.executemany(
        """
        INSERT INTO order_items (
            order_item_id, order_id, product_id, quantity, unit_price, line_total
        ) VALUES (
            :order_item_id, :order_id, :product_id, :quantity, :unit_price, :line_total
        )
        """,
        data["order_items.csv"],
    )

    conn.executemany(
        """
        INSERT INTO payments (
            payment_id, order_id, payment_date, amount, status,
            payment_method, transaction_reference
        ) VALUES (
            :payment_id, :order_id, :payment_date, :amount, :status,
            :payment_method, :transaction_reference
        )
        """,
        data["payments.csv"],
    )


def insert_submission_meta(conn: sqlite3.Connection, total_rows: Dict[str, int]) -> None:
    meta = {
        "student_unique_id": "diligent_candidate_v1",
        "generated_timestamp": now_utc_iso(),
        "total_rows_json": json.dumps(total_rows, sort_keys=True),
        "source_code_sha1": hash_file_sha1(BASE_DIR / "data_generation" / "generate_data.py"),
        "tool_used": "Cursor",
    }
    conn.execute(
        """
        INSERT INTO submission_meta (
            student_unique_id, generated_timestamp,
            total_rows_json, source_code_sha1, tool_used
        ) VALUES (
            :student_unique_id, :generated_timestamp,
            :total_rows_json, :source_code_sha1, :tool_used
        )
        """,
        meta,
    )


def fetch_report_data(conn: sqlite3.Connection) -> Dict[str, Any]:
    tables = ["users", "products", "orders", "order_items", "payments", "submission_meta"]
    table_counts = {
        table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in tables
    }

    validations = []
    orders_without_items = conn.execute(
        """
        SELECT COUNT(*) FROM orders o
        LEFT JOIN order_items oi ON oi.order_id = o.order_id
        WHERE oi.order_id IS NULL
        """
    ).fetchone()[0]
    validations.append(
        {
            "check": "Every order should have at least one order_item",
            "status": "pass" if orders_without_items == 0 else "fail",
            "details": orders_without_items,
        }
    )

    payment_mismatch = conn.execute(
        """
        SELECT COUNT(*) FROM orders o
        LEFT JOIN payments p ON p.order_id = o.order_id
        GROUP BY o.order_id
        HAVING ABS(COALESCE(SUM(p.amount), 0) - o.total_amount) > 0.01
        """
    ).fetchall()
    validations.append(
        {
            "check": "Payments roughly match order totals",
            "status": "pass" if not payment_mismatch else "warn",
            "details": len(payment_mismatch),
        }
    )

    top_products = conn.execute(
        """
        SELECT p.product_id, p.name, ROUND(SUM(oi.line_total), 2) AS revenue
        FROM order_items oi
        JOIN products p ON p.product_id = oi.product_id
        GROUP BY p.product_id, p.name
        ORDER BY revenue DESC
        LIMIT 5
        """
    ).fetchall()

    high_value_customers = conn.execute(
        """
        SELECT
            u.user_id,
            u.first_name || ' ' || u.last_name AS customer_name,
            u.segment,
            ROUND(COALESCE(SUM(o.total_amount), 0), 2) AS revenue
        FROM users u
        LEFT JOIN orders o ON o.user_id = u.user_id
        GROUP BY u.user_id
        ORDER BY revenue DESC
        LIMIT 5
        """
    ).fetchall()

    anomaly_rows = conn.execute(
        """
        SELECT o.order_id, o.user_id, o.status, p.status, p.amount
        FROM orders o
        JOIN payments p ON p.order_id = o.order_id
        WHERE p.status != 'succeeded'
        ORDER BY p.amount DESC
        LIMIT 5
        """
    ).fetchall()

    cohort_rows = conn.execute(
        """
        SELECT
            strftime('%Y-%m', u.signup_date) AS cohort_month,
            COUNT(DISTINCT u.user_id) AS customers,
            ROUND(SUM(COALESCE(o.total_amount, 0)), 2) AS cohort_revenue
        FROM users u
        LEFT JOIN orders o ON o.user_id = u.user_id
        GROUP BY cohort_month
        ORDER BY cohort_month
        """
    ).fetchall()

    return {
        "table_row_counts": table_counts,
        "validations": validations,
        "top_products": [
            {"product_id": row[0], "name": row[1], "revenue": row[2]} for row in top_products
        ],
        "high_value_customers": [
            {
                "user_id": row[0],
                "name": row[1],
                "segment": row[2],
                "revenue": row[3],
            }
            for row in high_value_customers
        ],
        "anomalies": [
            {
                "order_id": row[0],
                "user_id": row[1],
                "order_status": row[2],
                "payment_status": row[3],
                "amount": row[4],
            }
            for row in anomaly_rows
        ],
        "cohort_insights": [
            {
                "cohort_month": row[0],
                "customers": row[1],
                "cohort_revenue": row[2],
            }
            for row in cohort_rows
        ],
    }


def write_report(report_data: Dict[str, Any], logger: logging.Logger) -> None:
    logger.info("Writing report outputs.")
    write_json(REPORT_JSON, report_data)

    md_lines = [
        "# E-Commerce Data Quality Report",
        "",
        "## Table Row Counts",
    ]
    for table, count in report_data["table_row_counts"].items():
        md_lines.append(f"- **{table}**: {count} rows")

    md_lines.append("\n## Integrity Checks")
    for check in report_data["validations"]:
        md_lines.append(f"- **{check['check']}**: {check['status']} ({check['details']})")

    md_lines.append("\n## Top Products by Revenue")
    for product in report_data["top_products"]:
        md_lines.append(
            f"- {product['product_id']} {product['name']} — ${product['revenue']}"
        )

    md_lines.append("\n## High-Value Customers")
    for customer in report_data["high_value_customers"]:
        md_lines.append(
            f"- {customer['user_id']} {customer['name']} ({customer['segment']}) — ${customer['revenue']}"
        )

    md_lines.append("\n## Payment Anomalies")
    if report_data["anomalies"]:
        for row in report_data["anomalies"]:
            md_lines.append(
                f"- Order {row['order_id']} ({row['order_status']}) payment {row['payment_status']} amount ${row['amount']}"
            )
    else:
        md_lines.append("- None detected.")

    md_lines.append("\n## Cohort Insights")
    for cohort in report_data["cohort_insights"]:
        md_lines.append(
            f"- {cohort['cohort_month']}: {cohort['customers']} customers, ${cohort['cohort_revenue']} revenue"
        )

    REPORT_MD.write_text("\n".join(md_lines), encoding="utf-8")
    logger.info("Report saved to %s and %s", REPORT_MD.name, REPORT_JSON.name)


def run_ingestion(logger: logging.Logger) -> None:
    data = load_csv_data()
    row_counts = {name: len(rows) for name, rows in data.items()}
    with reset_database(logger) as conn:
        try:
            insert_data(conn, data)
            insert_submission_meta(conn, row_counts)
            conn.commit()
        except Exception:
            conn.rollback()
            logger.exception("Ingestion failed; rolled back transaction.")
            raise
    logger.info("Ingestion completed successfully.")


def main() -> None:
    args = parse_args()
    if not args.ingest and not args.report:
        raise SystemExit("Specify --ingest and/or --report.")

    logger = configure_logger("ingest")

    if args.ingest:
        run_ingestion(logger)

    if args.report:
        if not DB_PATH.exists():
            raise FileNotFoundError("Database not found. Run with --ingest first.")
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            report_data = fetch_report_data(conn)
        write_report(report_data, logger)


if __name__ == "__main__":
    main()

