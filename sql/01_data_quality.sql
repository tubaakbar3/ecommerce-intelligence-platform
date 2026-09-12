-- ============================================================
-- 01_data_quality.sql
-- Purpose: Demonstrate data quality auditing against the RAW layer
--          (raw_* tables, loaded unmodified from data/raw/*.csv).
--          These are the checks that justified every cleaning rule
--          applied in src/data_cleaning.py.
-- Run against: database/ecommerce.db
-- ============================================================

-- ---------------------------------------------------------
-- 1. NULL CHECKS
-- Why: missing values in key business fields distort every downstream
-- metric (e.g. missing shipping_cost understates order cost; missing
-- age blocks demographic segmentation).
-- ---------------------------------------------------------
SELECT 'raw_customers.age' AS field, COUNT(*) AS null_count
FROM raw_customers WHERE age IS NULL
UNION ALL
SELECT 'raw_customers.city', COUNT(*) FROM raw_customers WHERE city IS NULL
UNION ALL
SELECT 'raw_products.cost', COUNT(*) FROM raw_products WHERE cost IS NULL
UNION ALL
SELECT 'raw_orders.shipping_cost', COUNT(*) FROM raw_orders WHERE shipping_cost IS NULL
UNION ALL
SELECT 'raw_order_items.unit_price', COUNT(*) FROM raw_order_items WHERE unit_price IS NULL
UNION ALL
SELECT 'raw_payments.payment_method', COUNT(*) FROM raw_payments WHERE payment_method IS NULL
UNION ALL
SELECT 'raw_returns.return_reason', COUNT(*) FROM raw_returns WHERE return_reason IS NULL
UNION ALL
SELECT 'raw_marketing.spend', COUNT(*) FROM raw_marketing WHERE spend IS NULL
UNION ALL
SELECT 'raw_website_events.device', COUNT(*) FROM raw_website_events WHERE device IS NULL;


-- ---------------------------------------------------------
-- 2. DUPLICATE RECORD CHECKS
-- Why: duplicate customers/orders directly inflate revenue and customer
-- counts. Must be resolved before any KPI is trustworthy.
-- ---------------------------------------------------------
SELECT customer_id, COUNT(*) AS occurrences
FROM raw_customers
GROUP BY customer_id
HAVING COUNT(*) > 1
ORDER BY occurrences DESC;

SELECT order_id, COUNT(*) AS occurrences
FROM raw_orders
GROUP BY order_id
HAVING COUNT(*) > 1
ORDER BY occurrences DESC;


-- ---------------------------------------------------------
-- 3. INVALID VALUE CHECKS
-- Why: impossible values (negative quantity, cost > price, out-of-range
-- age) indicate data entry or system errors that would silently corrupt
-- revenue/margin calculations if left unchecked.
-- ---------------------------------------------------------
-- Impossible ages
SELECT customer_id, age FROM raw_customers
WHERE age IS NOT NULL AND (age < 13 OR age > 100);

-- Products where cost exceeds selling price (implies negative margin)
SELECT product_id, cost, selling_price
FROM raw_products
WHERE cost > selling_price;

-- Order items with non-positive quantity
SELECT order_item_id, order_id, quantity
FROM raw_order_items
WHERE quantity <= 0;

-- Orders/order_items with discount outside a sane [0,1] range
SELECT order_id, discount FROM raw_orders WHERE discount < 0 OR discount > 1;


-- ---------------------------------------------------------
-- 4. INCONSISTENT CATEGORY / FORMATTING CHECKS
-- Why: inconsistent casing/labels (e.g. "electronics" vs "Electronics")
-- silently fragments GROUP BY results and undercounts category totals.
-- ---------------------------------------------------------
SELECT DISTINCT category FROM raw_products ORDER BY category;
SELECT DISTINCT gender FROM raw_customers ORDER BY gender;
SELECT DISTINCT order_status FROM raw_orders ORDER BY order_status;
SELECT DISTINCT TRIM(country) AS country_trimmed, country AS country_raw
FROM raw_customers
WHERE country != TRIM(country) OR country != UPPER(country) AND country != LOWER(country);


-- ---------------------------------------------------------
-- 5. REFERENTIAL INTEGRITY CHECKS
-- Why: orphaned foreign keys (an order pointing to a customer that
-- doesn't exist) break every join-based analysis downstream.
-- ---------------------------------------------------------
-- Orders referencing a customer_id not present in customers
SELECT o.order_id, o.customer_id
FROM raw_orders o
LEFT JOIN raw_customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- Order items referencing a product_id not present in products
SELECT oi.order_item_id, oi.product_id
FROM raw_order_items oi
LEFT JOIN raw_products p ON oi.product_id = p.product_id
WHERE p.product_id IS NULL;

-- Order items referencing an order_id not present in orders
SELECT oi.order_item_id, oi.order_id
FROM raw_order_items oi
LEFT JOIN raw_orders o ON oi.order_id = o.order_id
WHERE o.order_id IS NULL;


-- ---------------------------------------------------------
-- 6. OUTLIER DETECTION (order value)
-- Why: extreme order values can be legitimate bulk orders OR data errors
-- (e.g. a misplaced decimal). Flag for manual review rather than
-- auto-deleting — this is a judgment call, not a hard rule.
-- ---------------------------------------------------------
WITH order_value AS (
    SELECT oi.order_id, SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
    FROM raw_order_items oi
    WHERE oi.quantity > 0 AND oi.unit_price IS NOT NULL
    GROUP BY oi.order_id
),
stats AS (
    SELECT AVG(revenue) AS mean_rev,
           -- approximate stddev
           SQRT(AVG(revenue*revenue) - AVG(revenue)*AVG(revenue)) AS std_rev
    FROM order_value
)
SELECT ov.order_id, ov.revenue
FROM order_value ov, stats s
WHERE ov.revenue > s.mean_rev + 3 * s.std_rev
ORDER BY ov.revenue DESC
LIMIT 50;
