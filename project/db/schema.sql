PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS submission_meta;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    country TEXT NOT NULL,
    signup_date TEXT NOT NULL,
    segment TEXT NOT NULL,
    is_active TEXT NOT NULL CHECK (is_active IN ('true', 'false')),
    loyalty_score INTEGER NOT NULL
);

CREATE TABLE products (
    product_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    currency TEXT NOT NULL,
    inventory_count INTEGER NOT NULL,
    is_active TEXT NOT NULL CHECK (is_active IN ('true', 'false'))
);

CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    order_date TEXT NOT NULL,
    status TEXT NOT NULL,
    shipping_method TEXT NOT NULL,
    discount_amount REAL NOT NULL DEFAULT 0,
    total_amount REAL NOT NULL,
    currency TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE order_items (
    order_item_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    line_total REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE payments (
    payment_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    payment_date TEXT NOT NULL,
    amount REAL NOT NULL,
    status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    transaction_reference TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

CREATE TABLE submission_meta (
    student_unique_id TEXT NOT NULL,
    generated_timestamp TEXT NOT NULL,
    total_rows_json TEXT NOT NULL,
    source_code_sha1 TEXT NOT NULL,
    tool_used TEXT NOT NULL DEFAULT 'Cursor'
);

