import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from utils.helpers import BASE_DIR, configure_logger, write_csv


UserRow = Dict[str, str]
ProductRow = Dict[str, str]
OrderRow = Dict[str, str]
OrderItemRow = Dict[str, str]
PaymentRow = Dict[str, str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate deterministic synthetic e-commerce CSV datasets."
    )
    parser.add_argument("--generate", action="store_true", help="Generate datasets.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(BASE_DIR),
        help="Directory where CSV files will be written.",
    )
    return parser.parse_args()


def create_id(prefix: str, idx: int) -> str:
    return f"{prefix}-{idx:05d}"


def generate_users(rng: random.Random, count: int = 95) -> List[UserRow]:
    first_names = [
        "Ava",
        "Ethan",
        "Maya",
        "Noah",
        "Liam",
        "Zara",
        "Leo",
        "Isla",
        "Aria",
        "Mila",
    ]
    last_names = [
        "Reed",
        "Patel",
        "Nguyen",
        "Garcia",
        "Chen",
        "Walker",
        "Singh",
        "Kim",
        "Silva",
        "Lopez",
    ]
    countries = ["US", "CA", "DE", "IN", "GB", "AU", "BR", "NL", "FR"]
    segments = ["consumer", "business", "vip"]
    base_date = datetime(2023, 1, 1)
    users: List[UserRow] = []
    for idx in range(1, count + 1):
        first = rng.choice(first_names)
        last = rng.choice(last_names)
        signup_date = base_date + timedelta(days=rng.randint(0, 640))
        users.append(
            {
                "user_id": create_id("USR", idx),
                "first_name": first,
                "last_name": last,
                "email": f"{first.lower()}.{last.lower()}{idx}@example.com",
                "country": rng.choice(countries),
                "signup_date": signup_date.strftime("%Y-%m-%d"),
                "segment": rng.choices(
                    segments, weights=[0.7, 0.2, 0.1], k=1
                )[0],
                "is_active": "true" if rng.random() > 0.1 else "false",
                "loyalty_score": str(rng.randint(100, 980)),
            }
        )
    return users


def generate_products(rng: random.Random, count: int = 32) -> List[ProductRow]:
    categories = {
        "Electronics": ["Smart Speaker", "Noise-canceling Headphones", "Drone Mini"],
        "Home": ["Air Purifier", "Smart Thermostat", "Espresso Maker"],
        "Outdoors": ["Trail Backpack", "Compact Tent", "Thermal Bottle"],
        "Apparel": ["Performance Hoodie", "Trail Shoes", "Travel Jacket"],
        "Beauty": ["Serum Duo", "Hydration Kit", "Vegan Cleanser"],
    }
    currency = "USD"
    products: List[ProductRow] = []
    idx = 1
    for category, names in categories.items():
        for name in names:
            price = round(rng.uniform(25, 480), 2)
            products.append(
                {
                    "product_id": create_id("PRD", idx),
                    "name": name,
                    "category": category,
                    "price": f"{price:.2f}",
                    "currency": currency,
                    "inventory_count": str(rng.randint(20, 500)),
                    "is_active": "true" if rng.random() > 0.05 else "false",
                }
            )
            idx += 1
    # Add additional variants until count reached
    while len(products) < count:
        base = rng.choice(products)
        price = max(12.0, float(base["price"]) * rng.uniform(0.8, 1.25))
        products.append(
            {
                "product_id": create_id("PRD", len(products) + 1),
                "name": f"{base['name']} {rng.choice(['Plus', 'Mini', 'XL'])}",
                "category": base["category"],
                "price": f"{price:.2f}",
                "currency": currency,
                "inventory_count": str(rng.randint(15, 420)),
                "is_active": "true",
            }
        )
    return products[:count]


def generate_orders(
    rng: random.Random,
    users: List[UserRow],
    products: List[ProductRow],
) -> Tuple[List[OrderRow], List[OrderItemRow], List[PaymentRow]]:
    orders: List[OrderRow] = []
    order_items: List[OrderItemRow] = []
    payments: List[PaymentRow] = []

    order_statuses = ["processing", "completed", "cancelled"]
    shipping_methods = ["standard", "express", "priority"]
    payment_methods = ["card", "ach", "paypal", "wallet"]
    payment_statuses = ["succeeded", "failed", "refunded"]

    base_order_date = datetime(2023, 6, 1)
    order_idx = 1
    order_item_idx = 1
    payment_idx = 1
    for user in users:
        order_count = rng.randint(0, 5 if user["segment"] != "vip" else 7)
        for _ in range(order_count):
            order_date = base_order_date + timedelta(days=rng.randint(0, 450))
            order_id = create_id("ORD", order_idx)
            status = rng.choices(order_statuses, weights=[0.2, 0.7, 0.1], k=1)[0]
            discount = round(rng.uniform(0, 45), 2)
            orders.append(
                {
                    "order_id": order_id,
                    "user_id": user["user_id"],
                    "order_date": order_date.strftime("%Y-%m-%d"),
                    "status": status,
                    "shipping_method": rng.choice(shipping_methods),
                    "discount_amount": f"{discount:.2f}",
                    "currency": "USD",
                    "total_amount": "0.00",  # placeholder updated after items
                }
            )
            item_count = rng.randint(1, 4)
            order_total = 0.0
            for _ in range(item_count):
                product = rng.choice(products)
                quantity = rng.randint(1, 3)
                unit_price = float(product["price"])
                line_total = unit_price * quantity
                order_items.append(
                    {
                        "order_item_id": create_id("ITM", order_item_idx),
                        "order_id": order_id,
                        "product_id": product["product_id"],
                        "quantity": str(quantity),
                        "unit_price": f"{unit_price:.2f}",
                        "line_total": f"{line_total:.2f}",
                    }
                )
                order_total += line_total
                order_item_idx += 1
            order_total = max(0.0, order_total - discount)
            orders[-1]["total_amount"] = f"{order_total:.2f}"

            payment_status = (
                "succeeded"
                if status != "cancelled" and rng.random() > 0.08
                else rng.choice(payment_statuses)
            )
            payment_amount = order_total if payment_status == "succeeded" else order_total * rng.uniform(0.1, 0.9)
            payment_date = order_date + timedelta(days=rng.randint(0, 5))
            payments.append(
                {
                    "payment_id": create_id("PAY", payment_idx),
                    "order_id": order_id,
                    "payment_date": payment_date.strftime("%Y-%m-%d"),
                    "amount": f"{payment_amount:.2f}",
                    "status": payment_status,
                    "payment_method": rng.choice(payment_methods),
                    "transaction_reference": f"TXN{rng.randint(100000, 999999)}",
                }
            )
            payment_idx += 1
            order_idx += 1
    return orders, order_items, payments


def build_datasets(rng: random.Random) -> Dict[str, Tuple[List[str], Iterable[Dict[str, str]]]]:
    users = generate_users(rng)
    products = generate_products(rng)
    orders, order_items, payments = generate_orders(rng, users, products)

    datasets: Dict[str, Tuple[List[str], Iterable[Dict[str, str]]]] = {
        "users.csv": (
            [
                "user_id",
                "first_name",
                "last_name",
                "email",
                "country",
                "signup_date",
                "segment",
                "is_active",
                "loyalty_score",
            ],
            users,
        ),
        "products.csv": (
            [
                "product_id",
                "name",
                "category",
                "price",
                "currency",
                "inventory_count",
                "is_active",
            ],
            products,
        ),
        "orders.csv": (
            [
                "order_id",
                "user_id",
                "order_date",
                "status",
                "shipping_method",
                "discount_amount",
                "total_amount",
                "currency",
            ],
            orders,
        ),
        "order_items.csv": (
            [
                "order_item_id",
                "order_id",
                "product_id",
                "quantity",
                "unit_price",
                "line_total",
            ],
            order_items,
        ),
        "payments.csv": (
            [
                "payment_id",
                "order_id",
                "payment_date",
                "amount",
                "status",
                "payment_method",
                "transaction_reference",
            ],
            payments,
        ),
    }
    return datasets


def main() -> None:
    args = parse_args()
    logger = configure_logger("data_generation")

    if not args.generate:
        logger.error("Use --generate to produce datasets.")
        raise SystemExit(1)

    rng = random.Random(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Generating datasets in %s", output_dir)

    datasets = build_datasets(rng)
    total_rows = 0
    for filename, (header, rows) in datasets.items():
        path = output_dir / filename
        write_csv(path, header, rows)
        row_count = sum(1 for _ in csv.DictReader(path.open("r", encoding="utf-8")))
        total_rows += row_count
        logger.info("Wrote %s (%s rows)", filename, row_count)

    logger.info("Generation complete. Total rows: %s", total_rows)


if __name__ == "__main__":
    main()

