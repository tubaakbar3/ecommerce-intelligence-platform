# Data Dictionary — Verona E-Commerce Intelligence Platform

All tables below reflect the **cleaned/processed** schema (`data/processed/`, and the constrained tables in `database/ecommerce.db`). Raw versions (`data/raw/`, `raw_*` tables) contain intentional imperfections described in each table's notes — see `data/processed/cleaning_log.txt` for the full audit trail.
## customers

| Column | Type | Nullable | Key | Description | Example |
|---|---|---|---|---|---|
| customer_id | TEXT | No | PK | Unique customer identifier | CUST100001 |
| signup_date | DATE | No | | Date the customer created an account | 2023-04-12 |
| gender | TEXT | No | | Self-reported gender (normalized to Female/Male/Other-Undisclosed/Unknown) | Female |
| age | INTEGER | No (imputed) | | Customer age in years; missing/invalid values imputed with segment median | 34 |
| city | TEXT | No (imputed as "Unknown") | | City of residence | Austin |
| country | TEXT | No | | Country (USA or Canada) | USA |
| acquisition_channel | TEXT | No | | How the customer was originally acquired | Paid Search |
| customer_segment | TEXT | No | | Declared value segment: Budget / Mainstream / Premium | Mainstream |

**Business meaning:** One row = one unique customer. Used as the customer dimension for all customer-level KPIs (repeat rate, CLV, RFM, cohorts).
## products

| Column | Type | Nullable | Key | Description | Example |
|---|---|---|---|---|---|
| product_id | TEXT | No | PK | Unique product identifier | PROD1001 |
| product_name | TEXT | No | | Product display name | Portable Smart Home 131 |
| category | TEXT | No | | One of 6 top-level categories | Electronics |
| subcategory | TEXT | No | | Category subdivision | Smart Home |
| brand | TEXT | No | | Brand name (Verona house brands + partner brands) | Novalux |
| supplier | TEXT | No | | Supplier code | Supplier_014 |
| cost | REAL | No (imputed) | | Unit cost to Verona; missing/invalid values imputed from category-average margin | 45.30 |
| selling_price | REAL | No | | List selling price (pre-discount) | 79.99 |
| launch_date | DATE | No | | Date product was first listed | 2023-06-01 |

**Business meaning:** Product dimension. `selling_price` and `cost` drive all revenue/margin calculations at the line-item level.
## orders

| Column | Type | Nullable | Key | Description | Example |
|---|---|---|---|---|---|
| order_id | TEXT | No | PK | Unique order identifier | ORD500001 |
| customer_id | TEXT | No | FK -> customers | Customer who placed the order | CUST100001 |
| order_date | DATETIME | No | | Date/time order was placed | 2023-11-24 14:32:00 |
| order_status | TEXT | No | | Completed / Cancelled / Refunded | Completed |
| sales_channel | TEXT | No | | Website / Marketplace / Mobile App | Website |
| shipping_cost | REAL | No (imputed as 0) | | Shipping fee charged; missing treated as waived | 0.00 |
| discount | REAL | No | | Order-level discount rate applied [0,1] | 0.15 |

**Business meaning:** Order header (fact table grain: 1 row per order). Only `order_status = 'Completed'` orders count toward realized revenue in analysis.

## order_items

| Column | Type | Nullable | Key | Description | Example |
|---|---|---|---|---|---|
| order_item_id | TEXT | No | PK | Unique line-item identifier | ITEM0000001 |
| order_id | TEXT | No | FK -> orders | Parent order | ORD500001 |
| product_id | TEXT | No | FK -> products | Product purchased | PROD1001 |
| quantity | INTEGER | No | | Units purchased (invalid/negative values removed in cleaning) | 2 |
| unit_price | REAL | No (imputed) | | Price per unit at time of sale | 79.99 |
| discount | REAL | No | | Line-level discount rate [0,1] | 0.10 |
| cost | REAL | No | | Unit cost at time of sale | 45.30 |

**Business meaning:** True grain of the sales fact table — 1 row per product per order. Revenue = `quantity * unit_price * (1 - discount)`.
## payments

| Column | Type | Nullable | Key | Description | Example |
|---|---|---|---|---|---|
| payment_id | TEXT | No | PK | Unique payment identifier | PAY700001 |
| order_id | TEXT | No | FK -> orders | Associated order | ORD500001 |
| payment_date | DATETIME | No | | When payment was processed | 2023-11-24 15:10:00 |
| payment_method | TEXT | No (imputed as "Unknown") | | Credit Card / Debit Card / PayPal / BNPL / Gift Card | Credit Card |
| payment_status | TEXT | No | | Success / Failed / Refunded | Success |
| payment_amount | REAL | No | | Amount charged (revenue + shipping) | 143.98 |

**Business meaning:** Confirms financial settlement of an order; used for payment-method mix analysis and reconciliation checks against order_items revenue.
## returns

| Column | Type | Nullable | Key | Description | Example |
|---|---|---|---|---|---|
| return_id | TEXT | No | PK | Unique return identifier | RET900001 |
| order_id | TEXT | No | FK -> orders | Order the return relates to | ORD500001 |
| product_id | TEXT | No | FK -> products | Product returned | PROD1001 |
| return_date | DATE | No | | Date of return | 2023-12-05 |
| return_reason | TEXT | No (imputed as "Not Specified") | | Reason given by customer | Defective/Damaged |
| returned_quantity | INTEGER | No | | Units returned | 1 |
| refund_amount | REAL | No | | Amount refunded | 79.99 |

**Business meaning:** Drives return-rate KPIs and profitability erosion analysis. Return rate is calculated **units-based** (see KPI definitions) rather than order-based, to avoid overstating impact from partial-order returns.
## marketing

| Column | Type | Nullable | Key | Description | Example |
|---|---|---|---|---|---|
| campaign_id | TEXT | No | PK | Unique campaign identifier | CAMP0001 |
| campaign_date | DATE | No | | Campaign start/reporting date | 2023-11-15 |
| channel | TEXT | No | | Paid Search / Social Media / Email / Affiliate / Display | Paid Search |
| campaign_name | TEXT | No | | Descriptive campaign name | Paid_Search_Nov2023_1 |
| impressions | INTEGER | No | | Ad impressions served | 245000 |
| clicks | INTEGER | No | | Ad clicks | 8200 |
| spend | REAL | No (imputed) | | Campaign spend in USD; missing values imputed from channel average CPC | 4100.00 |
| conversions | INTEGER | No | | Attributed conversions | 210 |
| attributed_revenue | REAL | No | | Revenue attributed to the campaign | 15750.00 |

**Business meaning:** Campaign-level marketing fact table. **Not foreign-keyed** to orders/customers — real-world marketing attribution is channel/date-level, not a clean join. This is intentional and should be explained as a known limitation, not a bug.
## website_events

| Column | Type | Nullable | Key | Description | Example |
|---|---|---|---|---|---|
| event_id | TEXT | No | PK | Unique event identifier | EVT00000001 |
| customer_id | TEXT | Yes (guest sessions) | FK -> customers | Customer if logged in; null for anonymous/guest sessions | CUST100001 |
| session_id | TEXT | No | | Session identifier (multiple events share a session) | a1b2c3d4e5f6 |
| event_timestamp | DATETIME | No | | When the event occurred | 2023-11-24 14:28:00 |
| device | TEXT | No (imputed as "Unknown") | | Mobile / Desktop / Tablet | Mobile |
| traffic_source | TEXT | No | | Paid Search / Organic Search / Social Media / Email / Direct / Referral | Organic Search |
| event_type | TEXT | No | | Funnel stage: site_visit / product_view / add_to_cart / checkout_start / purchase | product_view |
| product_id | TEXT | Yes | FK -> products | Product involved (null for site_visit stage) | PROD1001 |

**Business meaning:** Clickstream fact table driving funnel/conversion analysis. `customer_id IS NULL` is a **valid, expected state** (guest browsing) — not a data quality issue, and must not be dropped during cleaning.
## Derived tables (from `src/feature_engineering.py`)

### rfm_segments.csv
| Column | Description |
|---|---|
| customer_id | Customer identifier |
| recency_days | Days since last completed order (as of snapshot date = day after last order in dataset) |
| frequency | Count of distinct completed orders |
| monetary | Total realized revenue |
| R_score / F_score / M_score | Quintile scores 1-5 (5 = best) |
| RFM_score | Concatenated 3-digit score |
| segment | Champions / Loyal Customers / Potential Loyalists / New Customers / At Risk / Lost Customers / Others |

### cohort_retention.csv
Pivoted table: rows = acquisition cohort month (customer signup month), columns = period number (months since signup), values = % of that cohort still purchasing in that period.
