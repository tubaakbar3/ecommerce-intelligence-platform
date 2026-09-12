"""
Verona E-Commerce — Data Cleaning
Reads raw CSVs from data/raw/, applies documented cleaning rules, and
writes cleaned versions to data/processed/. data/raw/ is never modified.

Cleaning rules are intentionally explicit and logged so every
transformation is auditable — this mirrors how a real analyst
should document data cleaning decisions for stakeholders.

Usage:
    python src/data_cleaning.py
"""

import pandas as pd
import numpy as np
import os

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROC_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)

log = []


def note(msg):
    log.append(msg)
    print(msg)


def clean_customers():
    df = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))
    before = len(df)

    # Standardize text fields (strip whitespace, fix casing)
    df["country"] = df["country"].astype(str).str.strip().str.title()
    df["city"] = df["city"].astype(str).str.strip().str.title().replace("Nan", np.nan)

    # Normalize inconsistent gender labels
    gender_map = {"F": "Female", "M": "Male", "other": "Other/Undisclosed",
                  "Female": "Female", "Male": "Male", "Other/Undisclosed": "Other/Undisclosed"}
    df["gender"] = df["gender"].map(gender_map).fillna("Unknown")

    # Fix invalid ages (negative, 0, or absurdly high) -> null, then flag
    invalid_age = ~df["age"].between(13, 100, inclusive="both") | df["age"].isna()
    n_invalid_age = invalid_age.sum()
    df.loc[df["age"].notna() & ~df["age"].between(13, 100), "age"] = np.nan
    # Impute missing age with segment-level median (documented business rule)
    df["age"] = df.groupby("customer_segment")["age"].transform(lambda x: x.fillna(x.median()))
    df["age"] = df["age"].round().astype("Int64")

    # Standardize dates
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")

    # Remove exact duplicate rows
    df_dedup = df.drop_duplicates(subset=["customer_id"], keep="first")
    n_dupes = before - len(df_dedup)
    df = df_dedup

    # Fill missing city with "Unknown"
    df["city"] = df["city"].fillna("Unknown")

    note(f"[customers] rows in: {before}, duplicates removed: {n_dupes}, "
         f"invalid ages corrected: {n_invalid_age}, final rows: {len(df)}")
    return df


def clean_products():
    df = pd.read_csv(os.path.join(RAW_DIR, "products.csv"))
    before = len(df)

    df["category"] = df["category"].astype(str).str.strip().str.title()
    df["launch_date"] = pd.to_datetime(df["launch_date"], errors="coerce")

    # Fix cost > selling_price (impossible negative-margin data entry errors)
    bad_cost = df["cost"] > df["selling_price"]
    n_bad_cost = bad_cost.sum()
    # Business rule: cap cost at 70% of selling price when cost exceeds price
    df.loc[bad_cost, "cost"] = (df.loc[bad_cost, "selling_price"] * 0.65).round(2)

    # Impute missing cost using category-average margin
    df["_margin_pct"] = 1 - (df["cost"] / df["selling_price"])
    cat_margin = df.groupby("category")["_margin_pct"].transform("mean")
    missing_cost = df["cost"].isna()
    n_missing_cost = missing_cost.sum()
    df.loc[missing_cost, "cost"] = (df.loc[missing_cost, "selling_price"] * (1 - cat_margin)).round(2)
    df = df.drop(columns=["_margin_pct"])

    note(f"[products] rows in: {before}, cost>price errors fixed: {n_bad_cost}, "
         f"missing cost imputed: {n_missing_cost}, final rows: {len(df)}")
    return df


def clean_orders(valid_customers):
    df = pd.read_csv(os.path.join(RAW_DIR, "orders.csv"))
    before = len(df)

    df["order_status"] = df["order_status"].astype(str).str.strip().str.title()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    # Remove exact duplicate order rows
    df = df.drop_duplicates(subset=["order_id"], keep="first")
    n_dupes = before - len(df)

    # Referential integrity: drop orders referencing unknown customers
    before_ref = len(df)
    df = df[df["customer_id"].isin(valid_customers)]
    n_orphan = before_ref - len(df)

    # Missing shipping_cost -> 0 (business rule: treat missing as free/waived shipping)
    n_missing_ship = df["shipping_cost"].isna().sum()
    df["shipping_cost"] = df["shipping_cost"].fillna(0)

    # Discount must be within [0, 1]
    df["discount"] = df["discount"].clip(0, 1)

    note(f"[orders] rows in: {before}, duplicates removed: {n_dupes}, "
         f"orphan customer refs removed: {n_orphan}, missing shipping filled: {n_missing_ship}, "
         f"final rows: {len(df)}")
    return df


def clean_order_items(valid_orders, valid_products):
    df = pd.read_csv(os.path.join(RAW_DIR, "order_items.csv"))
    before = len(df)

    # Referential integrity
    df = df[df["order_id"].isin(valid_orders) & df["product_id"].isin(valid_products)]
    n_orphan = before - len(df)

    # Invalid (negative/zero) quantities -> drop (can't reliably impute a sale quantity)
    before_qty = len(df)
    df = df[df["quantity"] > 0]
    n_bad_qty = before_qty - len(df)

    # Missing unit_price -> impute from product's known selling_price (join not needed here;
    # fallback to median price within the same product_id group, else global median)
    df["unit_price"] = df.groupby("product_id")["unit_price"].transform(lambda x: x.fillna(x.median()))
    df["unit_price"] = df["unit_price"].fillna(df["unit_price"].median())

    df["discount"] = df["discount"].fillna(0).clip(0, 1)

    note(f"[order_items] rows in: {before}, orphan refs removed: {n_orphan}, "
         f"invalid quantities removed: {n_bad_qty}, final rows: {len(df)}")
    return df


def clean_payments(valid_orders):
    df = pd.read_csv(os.path.join(RAW_DIR, "payments.csv"))
    before = len(df)
    df = df[df["order_id"].isin(valid_orders)]
    n_orphan = before - len(df)

    df["payment_date"] = pd.to_datetime(df["payment_date"], errors="coerce")
    n_missing_method = df["payment_method"].isna().sum()
    df["payment_method"] = df["payment_method"].fillna("Unknown")

    note(f"[payments] rows in: {before}, orphan refs removed: {n_orphan}, "
         f"missing method filled: {n_missing_method}, final rows: {len(df)}")
    return df


def clean_returns(valid_orders, valid_products):
    df = pd.read_csv(os.path.join(RAW_DIR, "returns.csv"))
    before = len(df)
    df = df[df["order_id"].isin(valid_orders) & df["product_id"].isin(valid_products)]
    n_orphan = before - len(df)

    df["return_date"] = pd.to_datetime(df["return_date"], errors="coerce")
    n_missing_reason = df["return_reason"].isna().sum()
    df["return_reason"] = df["return_reason"].fillna("Not Specified")

    note(f"[returns] rows in: {before}, orphan refs removed: {n_orphan}, "
         f"missing reason filled: {n_missing_reason}, final rows: {len(df)}")
    return df


def clean_marketing():
    df = pd.read_csv(os.path.join(RAW_DIR, "marketing.csv"))
    before = len(df)
    df["campaign_date"] = pd.to_datetime(df["campaign_date"], errors="coerce")

    n_missing_spend = df["spend"].isna().sum()
    # Impute missing spend from channel average CPC * clicks (documented business rule)
    df["_cpc"] = df["spend"] / df["clicks"].replace(0, np.nan)
    channel_cpc = df.groupby("channel")["_cpc"].transform("mean")
    df.loc[df["spend"].isna(), "spend"] = (df["clicks"] * channel_cpc).round(2)
    df = df.drop(columns=["_cpc"])

    note(f"[marketing] rows in: {before}, missing spend imputed: {n_missing_spend}, final rows: {len(df)}")
    return df


def clean_website_events(valid_customers, valid_products):
    df = pd.read_csv(os.path.join(RAW_DIR, "website_events.csv"))
    before = len(df)
    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"], errors="coerce")

    # customer_id is intentionally nullable (guest sessions) — do NOT drop these
    # but do drop rows with a customer_id that doesn't exist in customers
    known_or_null = df["customer_id"].isna() | df["customer_id"].isin(valid_customers)
    df = df[known_or_null]
    n_orphan = before - len(df)

    n_missing_device = df["device"].isna().sum()
    df["device"] = df["device"].fillna("Unknown")

    # product_id null is valid for site_visit stage events
    invalid_product = df["product_id"].notna() & ~df["product_id"].isin(valid_products)
    n_bad_product = invalid_product.sum()
    df = df[~invalid_product]

    note(f"[website_events] rows in: {before}, orphan customer refs removed: {n_orphan}, "
         f"missing device filled: {n_missing_device}, invalid product refs removed: {n_bad_product}, "
         f"final rows: {len(df)}")
    return df


def main():
    note("=== Verona Data Cleaning Log ===\n")

    customers = clean_customers()
    products = clean_products()
    orders = clean_orders(set(customers["customer_id"]))
    items = clean_order_items(set(orders["order_id"]), set(products["product_id"]))
    payments = clean_payments(set(orders["order_id"]))
    returns = clean_returns(set(orders["order_id"]), set(products["product_id"]))
    marketing = clean_marketing()
    events = clean_website_events(set(customers["customer_id"]), set(products["product_id"]))

    customers.to_csv(os.path.join(PROC_DIR, "customers.csv"), index=False)
    products.to_csv(os.path.join(PROC_DIR, "products.csv"), index=False)
    orders.to_csv(os.path.join(PROC_DIR, "orders.csv"), index=False)
    items.to_csv(os.path.join(PROC_DIR, "order_items.csv"), index=False)
    payments.to_csv(os.path.join(PROC_DIR, "payments.csv"), index=False)
    returns.to_csv(os.path.join(PROC_DIR, "returns.csv"), index=False)
    marketing.to_csv(os.path.join(PROC_DIR, "marketing.csv"), index=False)
    events.to_csv(os.path.join(PROC_DIR, "website_events.csv"), index=False)

    with open(os.path.join(PROC_DIR, "cleaning_log.txt"), "w") as f:
        f.write("\n".join(log))

    note("\nAll cleaned files written to data/processed/")
    note("Cleaning log saved to data/processed/cleaning_log.txt")


if __name__ == "__main__":
    main()
