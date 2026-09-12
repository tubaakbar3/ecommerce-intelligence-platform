-- 05_business_kpis.sql
-- Purpose: Single management-level KPI summary — the numbers that would
-- appear on Page 1 (Executive Overview) of the Power BI dashboard.
-- Run against: database/ecommerce.db (CLEAN layer)
 
WITH completed_items AS (
    SELECT oi.*, o.order_id AS o_order_id, o.order_status, o.order_date, o.customer_id
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'Completed'
),
revenue_calc AS (
    SELECT SUM(quantity * unit_price * (1 - discount)) AS gross_revenue,
           SUM(quantity * cost) AS total_cost
    FROM completed_items
),
returns_calc AS (
    SELECT SUM(refund_amount) AS total_refunds,
           SUM(returned_quantity) AS total_units_returned
    FROM returns
),
units_calc AS (
    SELECT SUM(quantity) AS total_units_sold FROM completed_items
),
order_calc AS (
    SELECT COUNT(DISTINCT o_order_id) AS total_orders FROM completed_items
),
customer_calc AS (
    SELECT COUNT(DISTINCT customer_id) AS purchasing_customers FROM completed_items
),
repeat_calc AS (
    SELECT
        COUNT(*) AS customers_with_orders,
        SUM(CASE WHEN n_orders >= 2 THEN 1 ELSE 0 END) AS repeat_customers
    FROM (
        SELECT customer_id, COUNT(DISTINCT o_order_id) AS n_orders
        FROM completed_items GROUP BY customer_id
    )
),
marketing_calc AS (
    SELECT SUM(spend) AS total_spend, SUM(attributed_revenue) AS total_attributed_revenue
    FROM marketing
)
SELECT
    ROUND(r.gross_revenue, 2) AS gross_revenue,
    ROUND(r.gross_revenue - COALESCE(ret.total_refunds, 0), 2) AS net_revenue,
    ROUND(r.gross_revenue - r.total_cost, 2) AS gross_profit,
    ROUND((r.gross_revenue - r.total_cost) / NULLIF(r.gross_revenue, 0), 4) AS gross_margin_pct,
    o.total_orders,
    ROUND(r.gross_revenue / NULLIF(o.total_orders, 0), 2) AS aov,
    u.total_units_sold,
    c.purchasing_customers,
    ROUND(1.0 * rep.repeat_customers / NULLIF(rep.customers_with_orders, 0), 4) AS repeat_purchase_rate,
    ROUND(1.0 * COALESCE(ret.total_units_returned, 0) / NULLIF(u.total_units_sold, 0), 4) AS return_rate_units,
    ROUND(COALESCE(ret.total_refunds, 0), 2) AS total_refund_amount,
    ROUND(m.total_spend, 2) AS marketing_spend,
    ROUND(m.total_attributed_revenue / NULLIF(m.total_spend, 0), 2) AS blended_roas
FROM revenue_calc r, returns_calc ret, units_calc u, order_calc o,
     customer_calc c, repeat_calc rep, marketing_calc m;
 
-- Notes for dashboard build:
--   * gross_margin_pct and return_rate_units are the two "health check" KPIs
--     that most directly explain the margin-pressure narrative in Stage 9.
--   * blended_roas is a simplified, non-time-lagged ROAS (spend and
--     attributed_revenue are summed over the whole campaign record — a real
--     system would need attribution windows, which is out of scope here
--     and should be stated as a limitation in the report).
 