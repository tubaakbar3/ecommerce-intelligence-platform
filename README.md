# E-Commerce Revenue, Customer & Product Intelligence Platform

**An end-to-end analytics case study for Verona Home & Lifestyle Co.**, a fictional mid-market e-commerce retailer. This project simulates a real Data Analyst engagement: raw business data → cleaned → modeled → analyzed in SQL and Python → visualized in Power BI → translated into evidence-based business recommendations.

> All company details and data are synthetic (fixed random seed, fully reproducible). See [`data/processed/cleaning_log.txt`](data/processed/cleaning_log.txt) and [`docs/data_dictionary.md`](docs/data_dictionary.md) for full data provenance.

---

## Business Problem

Verona's leadership had no unified view of performance — reporting was manual, siloed by team, and couldn't answer: *Why are sales changing? Who are our best customers? Which products are working? What's hurting profitability? Where should we act?*

This project builds that analytics foundation from the ground up.

## Key Business Questions Answered

- Revenue trend, seasonality, and drivers of change
- Customer value distribution, repeat purchase rate, RFM segmentation, cohort retention
- Product/category profitability and return-rate hotspots
- Marketing channel ROI (ROAS) and budget allocation
- Website funnel drop-off points

## Key Findings (full detail in [`reports/business_insights.md`](reports/business_insights.md) / PDF)

- Revenue was **flat across 3 years (~$1.3M/year)** despite rising marketing spend — the real lever is retention, not acquisition volume
- **Top 25% of customers generate 66% of revenue** — justifies a dedicated retention program over blanket discounting
- **Electronics leads revenue but has the weakest margin (24.8%)** of any major category
- **Email marketing (2.84 ROAS) vastly outperforms Display (0.45 ROAS)** — a clear budget reallocation case
- **Fashion has the highest return rate (9.8% of units)** — likely fit/sizing related

---

## Architecture

```
Raw synthetic data (CSV)
        │
        ▼
Python cleaning (src/data_cleaning.py) ──► data/processed/
        │
        ▼
SQLite database (raw + clean layers) ──► SQL analysis (sql/*.sql)
        │
        ▼
Python EDA + Feature Engineering (notebooks/, src/feature_engineering.py)
        │
        ▼
Power BI Dashboard (dashboard/) ──► Business Insights Report (reports/)
```

## Tech Stack

Python (Pandas, NumPy, Matplotlib, Seaborn) · SQL (SQLite) · Power BI (DAX, Power Query) · Jupyter · Git/GitHub

---

## Repository Structure

```
ecommerce-intelligence-platform/
├── data/
│   ├── raw/                  # Synthetic raw data (with intentional imperfections)
│   └── processed/            # Cleaned data + RFM/cohort feature tables
├── database/
│   ├── schema.sql            # Table definitions, PK/FK, indexes
│   └── ecommerce.db          # SQLite DB (raw_* tables + clean constrained tables)
├── sql/
│   ├── 01_data_quality.sql   # NULL/duplicate/referential-integrity checks
│   ├── 02_sales_analysis.sql
│   ├── 03_customer_analysis.sql
│   ├── 04_product_analysis.sql
│   └── 05_business_kpis.sql
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_eda.ipynb
│   └── 03_customer_analysis.ipynb  # RFM + cohort analysis
├── src/
│   ├── data_generator.py     # Reproducible synthetic data generator (seed=42)
│   ├── data_cleaning.py
│   ├── feature_engineering.py # RFM + cohort logic
│   └── load_database.py
├── dashboard/
│   └── POWERBI_BUILD_GUIDE.md # Full DAX + page-by-page build guide
├── reports/
│   ├── business_insights.md
│   └── business_insights.pdf
└── docs/
    └── data_dictionary.md
```

## Skills Demonstrated

SQL (CTEs, window functions, joins, aggregations) · Python (Pandas data cleaning, EDA, feature engineering) · Statistics (distribution analysis, Pareto/concentration analysis) · RFM Segmentation · Cohort Analysis · Data Modeling (star-schema-style relational design) · Business Intelligence (Power BI, DAX) · Data Quality Auditing · Business Communication (evidence-based recommendations)

---

## How to Run This Project

**Requirements:** Python 3.10+, pip

```bash
# 1. Clone and set up environment
git clone <your-repo-url>
cd ecommerce-intelligence-platform
pip install -r requirements.txt

# 2. Generate the synthetic dataset (reproducible, seed=42)
python src/data_generator.py

# 3. Clean the data
python src/data_cleaning.py

# 4. Build the SQLite database (raw + clean layers)
python src/load_database.py

# 5. Run feature engineering (RFM + cohorts)
python src/feature_engineering.py

# 6. Explore the SQL analysis
#    Open database/ecommerce.db in any SQLite client (DB Browser for SQLite,
#    VS Code SQLite extension, or `python3 -c "import sqlite3; ..."`)
#    and run the queries in sql/01-05*.sql

# 7. Run the notebooks
jupyter notebook notebooks/
```

## Screenshots

Add a dashboard screenshot to `screenshots/dashboard.png` after building the Power BI file (see `dashboard/POWERBI_BUILD_GUIDE.md`).

## Future Improvements

- Streamlit app for interactive exploration without opening Power BI
- Predictive CLV model (vs. the current observed/historical CLV) using survival analysis
- Automated data quality monitoring / alerting
- A/B test framework to validate the retention recommendations against a holdout group

---

## License

MIT — see [LICENSE](LICENSE).
