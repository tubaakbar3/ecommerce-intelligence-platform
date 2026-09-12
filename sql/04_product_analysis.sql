-- 04_product_analysis.sql
-- Purpose: Product & category performance, profitability, returns.
-- Run against: database/ecommerce.db (CLEAN layer)
 
-- 1. PRODUCT REVENUE, PROFIT, MARGIN, UNITS SOLD
-- Why: base table for identifying revenue leaders vs. profit leaders
-- (they are not always the same products).
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) - SUM(oi.quantity * oi.cost), 2) AS profit,
    ROUND(
        (SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) - SUM(oi.quantity * oi.cost))
        / NULLIF(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 0), 4
    ) AS margin_pct
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_status = 'Completed'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY revenue DESC;
 
-- 2. TOP 20 PRODUCTS BY REVENUE
SELECT p.product_name, p.category,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_status = 'Completed'
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 20;
 
-- 3. BOTTOM 20 PRODUCTS BY REVENUE (among products with at least 1 sale)
-- Why: candidates for review/discontinuation, pending margin/strategic checks.
SELECT p.product_name, p.category,
       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_status = 'Completed'
GROUP BY p.product_id
ORDER BY revenue ASC
LIMIT 20;
 
-- 4. CATEGORY PERFORMANCE SUMMARY
SELECT
    p.category,
    COUNT(DISTINCT p.product_id) AS n_products,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 2) AS revenue,
    ROUND(
        (SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) - SUM(oi.quantity * oi.cost))
        / NULLIF(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 0), 4
    ) AS margin_pct
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_status = 'Completed'
GROUP BY p.category
ORDER BY revenue DESC;
 
-- 5. PRODUCT RETURN RATE (units-based — see KPI definitions for rationale)
-- Formula: units_returned / units_sold, per product.
SELECT
    p.product_id,
    p.product_name,
    p.category,
    COALESCE(SUM(oi.quantity), 0) AS units_sold,
    COALESCE(r.units_returned, 0) AS units_returned,
    ROUND(1.0 * COALESCE(r.units_returned, 0) / NULLIF(SUM(oi.quantity), 0), 4) AS return_rate_units
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN (
    SELECT product_id, SUM(returned_quantity) AS units_returned
    FROM returns
    GROUP BY product_id
) r ON r.product_id = p.product_id
WHERE o.order_status = 'Completed'
GROUP BY p.product_id, p.product_name, p.category, r.units_returned
HAVING units_sold >= 10   -- exclude low-volume products from noisy return-rate ranking
ORDER BY return_rate_units DESC
LIMIT 30;
 
-- 6. PRODUCT OPPORTUNITY MATRIX (Revenue vs. Margin quadrants)
-- Why: gives merchandising a simple 2x2 view for promote/fix/monitor/cut decisions.
WITH product_stats AS (
    SELECT
        p.product_id, p.product_name, p.category,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue,
        (SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) - SUM(oi.quantity * oi.cost))
            / NULLIF(SUM(oi.quantity * oi.unit_price * (1 - oi.discount)), 0) AS margin_pct
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.order_status = 'Completed'
    GROUP BY p.product_id, p.product_name, p.category
),
medians AS (
    SELECT
        (SELECT AVG(revenue) FROM (
            SELECT revenue FROM product_stats ORDER BY revenue
            LIMIT 2 - (SELECT COUNT(*) FROM product_stats) % 2
            OFFSET (SELECT (COUNT(*) - 1) / 2 FROM product_stats)
        )) AS median_revenue,
        (SELECT AVG(margin_pct) FROM product_stats) AS avg_margin
)
SELECT
    ps.product_id, ps.product_name, ps.category,
    ROUND(ps.revenue, 2) AS revenue,
    ROUND(ps.margin_pct, 4) AS margin_pct,
    CASE
        WHEN ps.revenue >= m.median_revenue AND ps.margin_pct >= m.avg_margin THEN 'High Revenue + High Margin (Promote)'
        WHEN ps.revenue >= m.median_revenue AND ps.margin_pct <  m.avg_margin THEN 'High Revenue + Low Margin (Fix Pricing/Cost)'
        WHEN ps.revenue <  m.median_revenue AND ps.margin_pct >= m.avg_margin THEN 'Low Revenue + High Margin (Grow Awareness)'
        ELSE 'Low Revenue + Low Margin (Review/Discontinue)'
    END AS opportunity_quadrant
FROM product_stats ps, medians m
ORDER BY ps.revenue DESC;
 