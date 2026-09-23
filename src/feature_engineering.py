"""
Verona E-Commerce — Feature Engineering
Builds two customer-intelligence outputs from cleaned data:

1. RFM (Recency, Frequency, Monetary) segmentation
2. Monthly acquisition cohort retention table

Outputs:
    data/processed/rfm_segments.csv
    data/processed/cohort_retention.csv

Usage:
    python src/feature_engineering.py
"""

import pandas as pd
import numpy as np
import os

PROC_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

# RFM METHODOLOGY (documented for the report / interview explanation)
# Recency  = days since each customer's most recent COMPLETED order,
#            measured from the day after the last date in the dataset
#            (i.e. "as of" the analysis snapshot date).
# Frequency = count of distinct COMPLETED orders per customer.
# Monetary = total realized revenue per customer (completed orders only).
#
# Each dimension is scored 1-5 using quintiles (5 = best: most recent,
# most frequent, highest spend). RFM_Score is the 3-digit concatenation
# (e.g. "555" = best possible customer). Segments are then assigned using
# common, defensible RFM segment rules (not arbitrary):
#
#   Champions          : R>=4, F>=4, M>=4
#   Loyal Customers     : F>=4 (regardless of recency), not Champions
#   Potential Loyalists : R>=4, F in (2,3)
#   New Customers       : R>=4, F==1
#   At Risk             : R in (2,3), F>=3  (used to buy often, slipping)
#   Lost Customers      : R<=2, F<=2
#   Others              : anything not captured above (kept for completeness)

def build_rfm():
    orders = pd.read_csv(os.path.join(PROC_DIR, "orders.csv"), parse_dates=["order_date"])
    items = pd.read_csv(os.path.join(PROC_DIR, "order_items.csv"))
    customers = pd.read_csv(os.path.join(PROC_DIR, "customers.csv"))

    completed = orders[orders["order_status"] == "Completed"].copy()
    merged = completed.merge(items, on="order_id", how="inner", suffixes=("_order", "_item"))
    merged["line_revenue"] = merged["quantity"] * merged["unit_price"] * (1 - merged["discount_item"])

    snapshot_date = orders["order_date"].max() + pd.Timedelta(days=1)

    rfm = merged.groupby("customer_id").agg(
        last_order_date=("order_date", "max"),
        frequency=("order_id", "nunique"),
        monetary=("line_revenue", "sum"),
    ).reset_index()
    rfm["recency_days"] = (snapshot_date - rfm["last_order_date"]).dt.days

    # Quintile scoring (1-5). Recency: lower days = better = higher score, so reverse.
    rfm["R_score"] = pd.qcut(rfm["recency_days"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["RFM_score"] = rfm["R_score"].astype(str) + rfm["F_score"].astype(str) + rfm["M_score"].astype(str)

    def segment(row):
        r, f, m = row["R_score"], row["F_score"], row["M_score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        if f >= 4:
            return "Loyal Customers"
        if r >= 4 and f in (2, 3):
            return "Potential Loyalists"
        if r >= 4 and f == 1:
            return "New Customers"
        if r in (2, 3) and f >= 3:
            return "At Risk"
        if r <= 2 and f <= 2:
            return "Lost Customers"
        return "Others"

    rfm["segment"] = rfm.apply(segment, axis=1)
    rfm = rfm.merge(customers[["customer_id", "customer_segment", "acquisition_channel"]],
                     on="customer_id", how="left")

    out_path = os.path.join(PROC_DIR, "rfm_segments.csv")
    rfm.to_csv(out_path, index=False)

    print("RFM segment distribution:")
    print(rfm["segment"].value_counts())
    print(f"\nSaved: {out_path}")
    return rfm


def build_cohorts():
    orders = pd.read_csv(os.path.join(PROC_DIR, "orders.csv"), parse_dates=["order_date"])
    items = pd.read_csv(os.path.join(PROC_DIR, "order_items.csv"))
    customers = pd.read_csv(os.path.join(PROC_DIR, "customers.csv"), parse_dates=["signup_date"])

    completed = orders[orders["order_status"] == "Completed"].copy()

    # Cohort = signup month (acquisition cohort — when the customer first joined)
    customers["cohort_month"] = customers["signup_date"].dt.to_period("M")
    completed = completed.merge(customers[["customer_id", "cohort_month"]], on="customer_id", how="left")
    completed["order_month"] = completed["order_date"].dt.to_period("M")
    completed["period_number"] = (completed["order_month"] - completed["cohort_month"]).apply(lambda x: x.n)
    completed = completed[completed["period_number"] >= 0]  # safety: drop any anomalies

    cohort_data = completed.groupby(["cohort_month", "period_number"])["customer_id"].nunique().reset_index()
    cohort_pivot = cohort_data.pivot(index="cohort_month", columns="period_number", values="customer_id")

    cohort_sizes = customers.groupby("cohort_month")["customer_id"].nunique()
    retention = cohort_pivot.divide(cohort_sizes, axis=0).round(4)

    out_path = os.path.join(PROC_DIR, "cohort_retention.csv")
    retention.to_csv(out_path)
    print(f"\nCohort retention table shape: {retention.shape}")
    print(f"Saved: {out_path}")
    return retention


if __name__ == "__main__":
    print("=== Building RFM Segments ===")
    build_rfm()
    print("\n=== Building Cohort Retention ===")
    build_cohorts()
