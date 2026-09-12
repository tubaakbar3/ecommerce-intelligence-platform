-- 03_customer_analysis.sql
-- Purpose: Customer-level KPIs — value, retention, and segmentation.
-- Run against: database/ecommerce.db (CLEAN layer)
 
-- 1. CUSTOMER COUNTS: total, new customers per month
-- Why: distinguishes growth from acquisition vs. growth from existing base.
SELECT
    strftime('%Y-%m', signup_date) AS signup_month,
    COUNT(*) AS new_customers
FROM customers
GROUP BY signup_month
ORDER BY signup_month;
 
-- 2. REPEAT PURCHASE RATE
-- Formula: customers with 2+ completed orders / total customers with >=1 completed order
-- Why: the single clearest signal of customer loyalty/retention health.
WITH order_counts AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS n_orders
    FROM orders
    WHERE order_status = 'Completed'
    GROUP BY customer_id
)
SELECT
    COUNT(*) AS customers_with_orders,
    SUM(CASE WHEN n_orders >= 2 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(1.0 * SUM(CASE WHEN n_orders >= 2 THEN 1 ELSE 0 END) / COUNT(*), 4) AS repeat_purchase_rate
FROM order_counts;
 
-- 3. AVERAGE ORDERS PER CUSTOMER & AVERAGE CUSTOMER SPEND
-- Why: baseline for evaluating whether retention initiatives are working.
WITH cust_rev AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT o.order_id) AS n_orders,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS total_spend
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY o.customer_id
)
SELECT
    ROUND(AVG(n_orders), 2) AS avg_orders_per_customer,
    ROUND(AVG(total_spend), 2) AS avg_customer_spend
FROM cust_rev;
 
-- 4. SIMPLIFIED (OBSERVED) CUSTOMER LIFETIME VALUE
-- Methodology: historical/observed CLV = total realized revenue per
-- customer to date. This is NOT a predictive CLV (no churn probability
-- or forecast model) — it's an honest "value so far" metric, appropriate
-- for a portfolio project without a validated survival/regression model.
-- Assumption: only 'Completed' orders count toward realized value.
WITH cust_rev AS (
    SELECT
        o.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS observed_clv,
        COUNT(DISTINCT o.order_id) AS n_orders,
        MIN(o.order_date) AS first_order,
        MAX(o.order_date) AS last_order
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY o.customer_id
)
SELECT
    customer_id, ROUND(observed_clv, 2) AS observed_clv, n_orders, first_order, last_order
FROM cust_rev
ORDER BY observed_clv DESC
LIMIT 100;
 
-- 5. CUSTOMER SEGMENTATION BY VALUE (simple quartile-based tiering)
-- Why: gives management a fast way to identify the "vital few" customers
-- driving disproportionate revenue (classic 80/20 check).
WITH cust_rev AS (
    SELECT
        o.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS total_spend
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY o.customer_id
),
ranked AS (
    SELECT customer_id, total_spend,
           NTILE(4) OVER (ORDER BY total_spend DESC) AS value_quartile
    FROM cust_rev
)
SELECT
    value_quartile,
    COUNT(*) AS customers,
    ROUND(SUM(total_spend), 2) AS quartile_revenue,
    ROUND(100.0 * SUM(total_spend) / (SELECT SUM(total_spend) FROM cust_rev), 2) AS pct_of_total_revenue
FROM ranked
GROUP BY value_quartile
ORDER BY value_quartile;
 
-- 6. CUSTOMER SEGMENT (Budget/Mainstream/Premium) PERFORMANCE
-- Why: connects declared customer_segment to actual realized spend —
-- validates whether the segment labels reflect real purchasing behavior.
SELECT
    c.customer_segment,
    COUNT(DISTINCT c.customer_id) AS customers,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed'
GROUP BY c.customer_segment
ORDER BY revenue DESC;
 