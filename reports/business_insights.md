# Verona Home & Lifestyle Co.
## E-Commerce Business Intelligence Report

**Prepared by:** Data Analytics Team
**Reporting Period:** January 2023 – December 2025
**Data Source:** Verona internal transactional database (synthetic portfolio dataset, seed=42, fully reproducible)

## Executive Summary

This report analyzes three years of Verona's e-commerce performance across revenue, customers, products, marketing, and website behavior. Total realized revenue over the period was **$3.96M** across **21,244 completed orders** from **~5,400 purchasing customers**, at a blended gross margin of **35.1%**. The analysis identifies where growth is concentrated, where margin is being eroded, and specific, evidence-based actions for each business function.

## Business Problem

Verona's leadership lacked a unified view of performance — reporting was manual and siloed by team. This project builds the analytics foundation to answer: *why are sales changing, who are the best customers, which products perform, what's hurting profitability, and where should management act?*

## Dataset Description

Synthetic but behaviorally realistic data across 8 relational tables (customers, products, orders, order_items, payments, returns, marketing, website_events), generated with a fixed random seed for full reproducibility. Raw data includes intentional imperfections (missing values, duplicates, invalid entries, inconsistent formatting) — see `docs/data_dictionary.md` and `data/processed/cleaning_log.txt` for the full cleaning methodology.

**This is a portfolio dataset, not real company data.** All figures below are internally consistent with the generated dataset and demonstrate analytical methodology, not real Verona performance (Verona itself is fictional).
## KPI Definitions

See `docs/data_dictionary.md` for full definitions. Two are worth restating here because they involved judgment calls:
- **Return rate** is calculated on a **units basis** (units returned / units sold), not per-order, because a single returned item in a multi-item order would otherwise overstate the order-based rate.
- **CLV** here is an **observed/historical CLV** (total realized revenue per customer to date) — not a predictive model. This is stated explicitly to avoid overselling the estimate.
## Revenue Findings

1. **Revenue was essentially flat across the three-year period** ($1.32M in 2023, $1.34M in 2024, $1.30M in 2025) rather than growing. **Evidence:** yearly revenue sums show <2% variation year over year. **Impact:** the business is not compounding growth despite rising marketing spend (see Marketing Findings). **Recommendation:** shift the growth conversation from "spend more" to "convert and retain better" — the data below shows the real leverage points are retention and channel mix, not raw acquisition volume.

2. **The Website channel is the clear revenue leader**, generating $2.18M (55% of total revenue) across 11,699 orders, compared to Marketplace ($1.20M) and Mobile App ($0.57M). **Evidence:** channel revenue breakdown. **Impact:** Website is both the highest-volume and (typically) lowest-cost-of-sale channel since it avoids marketplace commission fees. **Recommendation:** prioritize Website conversion-rate optimization over expanding Marketplace presence.

3. **Electronics is the top-revenue category ($1.17M) but has the weakest margin among major categories (24.8%)**, well below Beauty (55.9%) and Accessories (44.0%). **Evidence:** category revenue/margin breakdown. **Impact:** Verona is generating the most top-line revenue from its least profitable category. **Recommendation:** don't cut Electronics — it drives traffic and basket size — but evaluate supplier costs and reduce blanket discounting on this category specifically.

4. **Revenue shows strong, consistent seasonality**, with November (Black Friday/Cyber Monday period) as the clear peak month every year, and a January post-holiday dip. **Evidence:** monthly revenue trend (see `sql/02_sales_analysis.sql`, query 3). **Impact:** inventory and staffing planning should anchor to this known pattern rather than treating each peak as a surprise. **Recommendation:** lock in supplier/inventory commitments for Q4 earlier in the year to avoid rush costs.

5. **Average discount rate crept up slightly year over year (3.8% → 4.2%) while gross margin stayed roughly flat (35.3% → 35.0%)**, meaning discounting grew without a proportional revenue payoff. **Evidence:** yearly discount-vs-margin trend. **Impact:** promotional spend is not clearly buying incremental growth — revenue was flat despite more discounting. **Recommendation:** audit which specific campaigns/categories are driving the discount increase before increasing promotional budgets further.
## Customer Findings

1. **67.6% of purchasing customers are repeat buyers** (2+ completed orders) — a strong retention signal for a mid-market DTC retailer. **Evidence:** repeat purchase rate query. **Impact:** the business's growth lever is more likely to be increasing purchase frequency among existing customers than pure acquisition. **Recommendation:** invest in retention/lifecycle marketing (email, loyalty) rather than only top-of-funnel acquisition spend.

2. **The top customer quartile (25% of customers) generates 66.1% of total revenue.** **Evidence:** value-quartile revenue concentration query. **Impact:** this is a textbook Pareto pattern — losing even a small number of top-quartile customers would materially hurt revenue. **Recommendation:** build a defined VIP/retention program specifically for this quartile rather than treating all customers uniformly.

3. **RFM segmentation shows "Champions" (1,195 customers, 17% of the base) generate $2.28M — 58% of all revenue** — while "Lost Customers" (1,354 customers) generate only $281K. **Evidence:** RFM segment revenue table (`data/processed/rfm_segments.csv`). **Impact:** confirms the quartile finding with a behavioral lens — the same core group drives the business. **Recommendation:** prioritize Champion retention (exclusive early access, loyalty perks) over broad-based discounting that dilutes margin across the whole base.

4. **"At Risk" customers (551, previously frequent buyers whose recency has slipped) represent a clear win-back opportunity** worth an estimated $229K in historical spend. **Evidence:** RFM segment table. **Impact:** these customers have proven purchase intent and are cheaper to reactivate than acquiring new customers. **Recommendation:** targeted win-back email/discount campaign specifically for the At Risk segment, tracked separately from general promotions.

5. **Mainstream-segment customers generate the most total revenue ($1.70M)** among the three declared customer segments, consistent with the largest population share, but revenue-per-customer should be compared against Premium before assuming Mainstream is the priority segment. **Evidence:** customer segment performance query. **Impact:** segment labels appear to reasonably track actual spend behavior. **Recommendation:** validate this finding with revenue-per-customer (not just total) before shifting acquisition targeting.
## Product Findings

1. Electronics and Home & Kitchen are the two largest revenue categories, but **Home & Kitchen carries a substantially healthier margin (39.0%) at nearly comparable revenue**, making it arguably the stronger category for promotional investment.
2. **The lowest-margin, lowest-revenue products cluster heavily in Electronics and Fashion** — the product opportunity matrix (`sql/04_product_analysis.sql`, query 6) flags these explicitly as "Review/Discontinue" candidates.
3. **Fashion has the highest return rate of any category (9.8% of units sold)**, nearly double Home & Kitchen's (3.65%) — consistent with known industry patterns around sizing/fit issues.
4. A small number of individual SKUs account for a disproportionate share of category revenue (e.g., top Electronics product alone drove $170K), meaning single-SKU stockouts carry outsized revenue risk.
5. Beauty's high margin (55.9%) combined with comparatively modest revenue ($411K) marks it as a "Low Revenue + High Margin — Grow Awareness" opportunity rather than a category to deprioritize.
## Marketing Findings

1. **Email is by far the most efficient channel (ROAS 2.84)** — more than double Paid Search (1.97) and nearly triple Social Media (1.08) — despite receiving less total spend than Affiliate or Social. **Recommendation:** reallocate incremental budget toward Email before increasing Paid Search or Display spend.
2. **Display advertising is unprofitable (ROAS 0.45)** — spend exceeds attributed revenue. **Recommendation:** pause or substantially restructure Display campaigns pending a targeting review.
3. **Affiliate spend is the second-highest of any channel ($407K) but delivers only 1.15 ROAS**, barely above breakeven. **Recommendation:** audit specific affiliate partners rather than treating the channel as uniformly effective.
## Website Findings

1. **The single biggest funnel drop-off is between Product View and Add to Cart** (36,399 → 12,765 sessions, a ~65% drop), larger than any other stage transition. **Recommendation:** prioritize product page optimization (pricing clarity, reviews, imagery) over checkout-flow fixes.
2. Checkout Start to Purchase conversion is comparatively strong (~67%), suggesting the checkout process itself is not the primary leak.
3. Roughly 22% of tracked sessions never progress past the initial site visit to any product view, pointing to a landing-page/relevance issue worth investigating by traffic source.
## Key Risks

- Revenue concentration in a small customer segment (top quartile = 66% of revenue) creates vulnerability to churn among high-value customers.
- Margin compression risk in Electronics if discounting continues without cost review.
- Display marketing spend is actively destroying value at current ROAS.

## Recommendations Summary

| Priority | Action | Owner |
|---|---|---|
| High | Build retention program for Champions/top quartile | CX/Retention |
| High | Reallocate budget from Display to Email | CMO |
| High | Win-back campaign for At Risk RFM segment | CX/Retention |
| Medium | Audit Electronics discounting and supplier costs | Merchandising/Finance |
| Medium | Optimize product pages to fix Product View → Add to Cart drop-off | Website/UX |
| Medium | Review Fashion category return drivers (sizing/fit) | Merchandising |

## Expected Business Impact

Directionally, retaining even a modest share of the At Risk segment (551 customers, ~$229K historical value) and reallocating Display spend toward Email (2.84 vs 0.45 ROAS) represent the two highest-confidence, lowest-risk levers identified in this analysis. Exact dollar impact would require a controlled test (e.g. holdout group for the win-back campaign) rather than being asserted from historical data alone.

## Conclusion

Verona's business is healthier than flat top-line revenue suggests — retention is strong, a loyal core customer base drives the majority of revenue, and clear efficiency gaps exist in both marketing channel allocation and specific product categories. The priority is not "grow harder" but "convert and retain smarter" within the patterns this analysis has surfaced.
*This report was generated as part of a data analytics portfolio project. All company details, data, and figures are synthetic and created for demonstration purposes only.*
