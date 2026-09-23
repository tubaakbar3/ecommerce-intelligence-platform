"""
Verona E-Commerce — Database Loader
Builds database/ecommerce.db with TWO layers:

1. raw_<table>   — unconstrained mirror of data/raw/*.csv, used by
                    sql/01_data_quality.sql to demonstrate finding issues
                    (nulls, dupes, invalid values, referential breaks).
2. <table>        — clean, constrained tables (PK/FK, from schema.sql),
                    loaded from data/processed/*.csv. All analytical SQL
                    (02-05) runs against this layer.

Usage:
    python src/load_database.py
"""

import sqlite3
import pandas as pd
import os

BASE = os.path.join(os.path.dirname(__file__), "..")
RAW_DIR = os.path.join(BASE, "data", "raw")
PROC_DIR = os.path.join(BASE, "data", "processed")
DB_PATH = os.path.join(BASE, "database", "ecommerce.db")
SCHEMA_PATH = os.path.join(BASE, "database", "schema.sql")

TABLES = ["customers", "products", "orders", "order_items",
          "payments", "returns", "marketing", "website_events"]


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ---- Layer 1: raw (unconstrained) ----
    print("Loading RAW layer (for data quality auditing)...")
    for t in TABLES:
        df = pd.read_csv(os.path.join(RAW_DIR, f"{t}.csv"))
        df.to_sql(f"raw_{t}", conn, if_exists="replace", index=False)
        print(f"  raw_{t}: {len(df):,} rows")

    # ---- Layer 2: clean (constrained schema) ----
    print("\nCreating clean schema...")
    with open(SCHEMA_PATH, "r") as f:
        cur.executescript(f.read())
    conn.commit()

    print("Loading CLEAN layer (from data/processed)...")
    for t in TABLES:
        df = pd.read_csv(os.path.join(PROC_DIR, f"{t}.csv"))
        df.to_sql(t, conn, if_exists="append", index=False)
        print(f"  {t}: {len(df):,} rows")

    conn.commit()
    conn.close()
    print(f"\nDatabase built at {DB_PATH}")


if __name__ == "__main__":
    main()
