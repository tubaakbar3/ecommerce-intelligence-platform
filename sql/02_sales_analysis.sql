 --02_sales_analysis.sql
-- Purpose: Core revenue and sales KPIs for management reporting.
-- Run against: database/ecommerce.db (CLEAN layer)
 
-- Revenue formula used throughout:
--   line_revenue = quantity * unit_price * (1 - discount)
-- Only order_status = 'Completed' counts toward realized revenue;
-- Cancelled orders are excluded, Refunded orders are handled via
-- the returns table (net revenue = gross revenue - refunds).
 
-- 1. TOTAL REVENUE, GROSS PROFIT, MARGIN
-- Why management needs it: the single top-line health check.
SELECT
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS total_revenue,
    ROUND(SUM(oi.quantity * oi.cost), 2) AS total_cost,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) - SUM(oi.quantity * oi.cost), 2) AS gross_profit,
    ROUND(
        (SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) - SUM(oi.quantity * oi.cost))
        / NULLIF(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 0), 4
    ) AS gross_margin_pct
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed';
 
-- 2. ORDERS, UNITS SOLD, AOV
-- Why: AOV tells management whether growth is from more customers
-- or bigger baskets — very different strategic responses.
SELECT
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity) AS total_units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) / COUNT(DISTINCT o.order_id), 2) AS aov
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed';
 
-- 3. REVENUE BY MONTH + MONTH-OVER-MONTH GROWTH
-- Why: reveals seasonality and whether current performance is trending
-- up or down — the first question every management meeting asks.
WITH monthly AS (
    SELECT
        strftime('%Y-%m', o.order_date) AS year_month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY year_month
)
SELECT
    year_month,
    ROUND(revenue, 2) AS revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY year_month))
        / NULLIF(LAG(revenue) OVER (ORDER BY year_month), 0) * 100, 2
    ) AS mom_growth_pct
FROM monthly
ORDER BY year_month;
 
-- 4. REVENUE BY CATEGORY
-- Why: tells merchandising which categories to invest marketing/inventory in.
SELECT
    p.category,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) - SUM(oi.quantity * oi.cost), 2) AS gross_profit,
    ROUND(
        (SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) - SUM(oi.quantity * oi.cost))
        / NULLIF(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 0), 4
    ) AS gross_margin_pct
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_status = 'Completed'
GROUP BY p.category
ORDER BY revenue DESC;
 
-- 5. REVENUE BY SALES CHANNEL
-- Why: informs channel investment decisions (e.g. is Marketplace worth
-- its commission fees relative to the direct Website channel?).
SELECT
    o.sales_channel,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) / COUNT(DISTINCT o.order_id), 2) AS aov
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY o.sales_channel
ORDER BY revenue DESC;
 
-- 6. REVENUE BY GEOGRAPHY (country)
-- Why: identifies where to focus geographic expansion or logistics investment.
SELECT
    c.country,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'Completed'
GROUP BY c.country
ORDER BY revenue DESC;