-- Verona Home & Lifestyle Co. — E-Commerce Intelligence Platform
-- Database Schema (SQLite)
-- Design notes:
--   * customers, products = dimension tables
--   * orders, order_items, payments, returns, marketing, website_events = fact tables
--   * order_items is the true grain of sales (1 row = 1 product line in 1 order)
--   * marketing is intentionally NOT foreign-keyed to orders/customers —
--     real-world attribution is channel/date-level, not a clean join.
--     We connect it analytically via channel + date, not via FK.

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS website_events;
DROP TABLE IF EXISTS marketing;
DROP TABLE IF EXISTS returns;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- DIMENSION: customers
CREATE TABLE customers (
    customer_id         TEXT PRIMARY KEY,
    signup_date          DATE NOT NULL,
    gender                TEXT,
    age                    INTEGER,
    city                   TEXT,
    country                TEXT,
    acquisition_channel     TEXT,
    customer_segment       TEXT
);
-- DIMENSION: products
CREATE TABLE products (
    product_id      TEXT PRIMARY KEY,
    product_name    TEXT NOT NULL,
    category         TEXT,
    subcategory      TEXT,
    brand              TEXT,
    supplier           TEXT,
    cost                 REAL,
    selling_price       REAL,
    launch_date         DATE
);
-- FACT: orders (order header)
CREATE TABLE orders (
    order_id        TEXT PRIMARY KEY,
    customer_id     TEXT NOT NULL,
    order_date      DATETIME NOT NULL,
    order_status    TEXT,
    sales_channel   TEXT,
    shipping_cost   REAL,
    discount        REAL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
-- FACT: order_items (grain of the sales fact table)
CREATE TABLE order_items (
    order_item_id   TEXT PRIMARY KEY,
    order_id        TEXT NOT NULL,
    product_id      TEXT NOT NULL,
    quantity        INTEGER,
    unit_price      REAL,
    discount        REAL,
    cost            REAL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
-- FACT: payments
CREATE TABLE payments (
    payment_id      TEXT PRIMARY KEY,
    order_id        TEXT NOT NULL,
    payment_date    DATETIME,
    payment_method  TEXT,
    payment_status  TEXT,
    payment_amount  REAL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
-- FACT: returns
CREATE TABLE returns (
    return_id           TEXT PRIMARY KEY,
    order_id             TEXT NOT NULL,
    product_id           TEXT NOT NULL,
    return_date          DATE,
    return_reason        TEXT,
    returned_quantity    INTEGER,
    refund_amount        REAL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
-- FACT: marketing (campaign-level, channel/date grain)
CREATE TABLE marketing (
    campaign_id         TEXT PRIMARY KEY,
    campaign_date        DATE,
    channel               TEXT,
    campaign_name         TEXT,
    impressions           INTEGER,
    clicks                INTEGER,
    spend                 REAL,
    conversions           INTEGER,
    attributed_revenue    REAL
);
-- FACT: website_events (clickstream / funnel)
CREATE TABLE website_events (
    event_id         TEXT PRIMARY KEY,
    customer_id      TEXT,
    session_id       TEXT,
    event_timestamp  DATETIME,
    device            TEXT,
    traffic_source    TEXT,
    event_type        TEXT,
    product_id        TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
-- Indexes for common analytical joins/filters
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_items_order ON order_items(order_id);
CREATE INDEX idx_items_product ON order_items(product_id);
CREATE INDEX idx_payments_order ON payments(order_id);
CREATE INDEX idx_returns_order ON returns(order_id);
CREATE INDEX idx_returns_product ON returns(product_id);
CREATE INDEX idx_events_customer ON website_events(customer_id);
CREATE INDEX idx_events_session ON website_events(session_id);
CREATE INDEX idx_marketing_date ON marketing(campaign_date);
