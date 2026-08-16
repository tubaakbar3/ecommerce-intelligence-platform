"""
Verona Home & Lifestyle Co. — Synthetic E-Commerce Dataset Generator
Generates realistic (not random-meaningless) e-commerce data across 8
related tables, with intentional seasonality, customer behavior patterns,
category economics, and realistic data imperfections for cleaning practice.
 
Usage:
    python src/data_generator.py
 
Output:
    data/raw/customers.csv
    data/raw/products.csv
    data/raw/orders.csv
    data/raw/order_items.csv
    data/raw/payments.csv
    data/raw/returns.csv
    data/raw/marketing.csv
    data/raw/website_events.csv
 
Reproducibility:
    Fixed random seed (SEED = 42). Re-running produces identical data.
"""
 
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os
import uuid
 
SEED = 42
rng = np.random.default_rng(SEED)
 
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUT_DIR, exist_ok=True)
 
# GLOBAL TIMELINE: 3 full years of business history
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 12, 31)
TOTAL_DAYS = (END_DATE - START_DATE).days
 
N_CUSTOMERS = 7000
N_PRODUCTS = 260
N_ORDERS = 32000
N_CAMPAIGNS = 150
N_WEBSITE_EVENTS = 120000
 
CHANNELS = ["Website", "Marketplace", "Mobile App"]
CHANNEL_WEIGHTS = [0.55, 0.30, 0.15]
 
ACQUISITION_CHANNELS = ["Paid Search", "Organic Search", "Social Media", "Email", "Referral", "Direct", "Affiliate"]
ACQ_WEIGHTS = [0.22, 0.20, 0.18, 0.12, 0.08, 0.12, 0.08]
 
SEGMENTS = ["Budget", "Mainstream", "Premium"]
SEGMENT_WEIGHTS = [0.35, 0.45, 0.20]
 
COUNTRIES_CITIES = {
    "USA": ["Austin", "Dallas", "Houston", "Chicago", "New York", "Los Angeles",
            "Seattle", "Denver", "Atlanta", "Miami", "Phoenix", "Boston",
            "Portland", "San Diego", "Nashville", "Minneapolis"],
    "Canada": ["Toronto", "Vancouver", "Montreal", "Calgary"],
}
 
CATEGORIES = {
    "Electronics":     {"subcats": ["Headphones", "Smart Home", "Small Gadgets", "Chargers & Cables"], "margin": 0.28, "price_range": (25, 350)},
    "Home & Kitchen":   {"subcats": ["Cookware", "Small Appliances", "Home Decor", "Storage & Organization"], "margin": 0.42, "price_range": (15, 220)},
    "Beauty":          {"subcats": ["Skincare", "Haircare", "Beauty Tools", "Fragrance"], "margin": 0.55, "price_range": (10, 90)},
    "Fashion":         {"subcats": ["Apparel", "Footwear", "Outerwear"], "margin": 0.38, "price_range": (20, 160)},
    "Sports & Outdoors": {"subcats": ["Fitness Gear", "Outdoor Equipment", "Athletic Wear"], "margin": 0.35, "price_range": (15, 300)},
    "Accessories":     {"subcats": ["Bags", "Tech Accessories", "Jewelry & Watches"], "margin": 0.48, "price_range": (10, 130)},
}
 
BRANDS = ["Verona Basics", "Novalux", "Kindra", "UrbanEdge", "Lumio", "TrueForm",
          "Northstead", "Everly", "Pulse", "Meadowlane", "Craftly", "Solstice"]
 
SUPPLIERS = [f"Supplier_{i:03d}" for i in range(1, 41)]
 
PAYMENT_METHODS = ["Credit Card", "Debit Card", "PayPal", "Buy Now Pay Later", "Gift Card"]
PAYMENT_METHOD_WEIGHTS = [0.45, 0.20, 0.20, 0.10, 0.05]
 
RETURN_REASONS = ["Defective/Damaged", "Not as Described", "Wrong Item Shipped",
                   "No Longer Needed", "Better Price Found", "Size/Fit Issue", "Changed Mind"]
 
DEVICES = ["Mobile", "Desktop", "Tablet"]
DEVICE_WEIGHTS = [0.58, 0.32, 0.10]
 
TRAFFIC_SOURCES = ["Paid Search", "Organic Search", "Social Media", "Email", "Direct", "Referral"]
TRAFFIC_WEIGHTS = [0.24, 0.22, 0.18, 0.12, 0.14, 0.10]
 
FUNNEL_STAGES = ["site_visit", "product_view", "add_to_cart", "checkout_start", "purchase"]
 
def seasonality_multiplier(date: datetime) -> float:
    """Return a demand multiplier for a given date: holiday bumps + weekly pattern."""
    mult = 1.0
    month, day = date.month, date.day
    # Black Friday / Cyber Monday / Holiday season
    if month == 11 and 20 <= day <= 30:
        mult *= 2.3
    elif month == 12 and day <= 20:
        mult *= 1.6
    elif month == 12 and day > 25:
        mult *= 0.6
    # Summer slowdown
    elif month in (6, 7):
        mult *= 0.85
    # Back to school bump
    elif month in (8, 9) and day <= 15:
        mult *= 1.15
    # January post-holiday dip
    elif month == 1 and day <= 10:
        mult *= 0.7
    # Mild weekly pattern (weekend bump for a DTC retailer)
    if date.weekday() in (5, 6):
        mult *= 1.1
    return mult
 
def random_dates(n, start=START_DATE, end=END_DATE, weighted=True):
    """Generate n dates across the range, weighted by seasonality if requested."""
    if not weighted:
        offsets = rng.integers(0, TOTAL_DAYS, size=n)
        return [start + timedelta(days=int(o)) for o in offsets]
    all_days = [start + timedelta(days=i) for i in range(TOTAL_DAYS)]
    weights = np.array([seasonality_multiplier(d) for d in all_days])
    weights = weights / weights.sum()
    chosen = rng.choice(len(all_days), size=n, p=weights)
    # add random time-of-day
    return [all_days[i] + timedelta(hours=int(rng.integers(0, 24)), minutes=int(rng.integers(0, 60))) for i in chosen]
 
# 1. CUSTOMERS
def generate_customers(n=N_CUSTOMERS):
    signup_dates = random_dates(n, weighted=False)
    signup_dates.sort()
 
    genders = rng.choice(["Female", "Male", "Other/Undisclosed"], size=n, p=[0.56, 0.40, 0.04])
    ages = rng.normal(36, 11, size=n).clip(18, 75).astype(int)
 
    countries = rng.choice(list(COUNTRIES_CITIES.keys()), size=n, p=[0.88, 0.12])
    cities = [rng.choice(COUNTRIES_CITIES[c]) for c in countries]
 
    acquisition = rng.choice(ACQUISITION_CHANNELS, size=n, p=ACQ_WEIGHTS)
    segment = rng.choice(SEGMENTS, size=n, p=SEGMENT_WEIGHTS)
 
    df = pd.DataFrame({
        "customer_id": [f"CUST{100000+i}" for i in range(n)],
        "signup_date": [d.strftime("%Y-%m-%d") for d in signup_dates],
        "gender": genders,
        "age": ages,
        "city": cities,
        "country": countries,
        "acquisition_channel": acquisition,
        "customer_segment": segment,
    })
 
    # ---- Inject realistic imperfections ----
    # Missing age (3%)
    miss_idx = rng.choice(n, size=int(n * 0.03), replace=False)
    df.loc[miss_idx, "age"] = np.nan
    # Missing city (1.5%)
    miss_idx = rng.choice(n, size=int(n * 0.015), replace=False)
    df.loc[miss_idx, "city"] = np.nan
    # Inconsistent gender casing/labels (2%)
    inc_idx = rng.choice(n, size=int(n * 0.02), replace=False)
    df.loc[inc_idx, "gender"] = df.loc[inc_idx, "gender"].apply(
        lambda g: {"Female": "F", "Male": "M", "Other/Undisclosed": "other"}.get(g, g))
    # Invalid ages (negative / absurdly high) (0.5%)
    bad_idx = rng.choice(n, size=int(n * 0.005), replace=False)
    df.loc[bad_idx, "age"] = rng.choice([-5, 150, 0], size=len(bad_idx))
    # Duplicate customer rows (0.5%)
    dupes = df.sample(int(n * 0.005), random_state=SEED)
    df = pd.concat([df, dupes], ignore_index=True)
    # Whitespace/formatting issues in country (1%)
    inc_idx = rng.choice(len(df), size=int(len(df) * 0.01), replace=False)
    df.loc[inc_idx, "country"] = df.loc[inc_idx, "country"].apply(lambda c: f" {c.upper()} ")
 
    return df.sample(frac=1, random_state=SEED).reset_index(drop=True)  # shuffle
 
# 2. PRODUCTS
ADJECTIVES = ["Classic", "Pro", "Essential", "Deluxe", "Compact", "Ultra", "Everyday",
              "Signature", "Modern", "Premium", "Portable", "Smart"]
 
def generate_products(n=N_PRODUCTS):
    rows = []
    cats = list(CATEGORIES.keys())
    for i in range(n):
        cat = rng.choice(cats)
        info = CATEGORIES[cat]
        subcat = rng.choice(info["subcats"])
        brand = rng.choice(BRANDS)
        supplier = rng.choice(SUPPLIERS)
        low, high = info["price_range"]
        selling_price = round(float(rng.uniform(low, high)), 2)
        margin = info["margin"] + rng.normal(0, 0.05)
        margin = min(max(margin, 0.05), 0.75)
        cost = round(selling_price * (1 - margin), 2)
        launch_date = START_DATE + timedelta(days=int(rng.integers(0, TOTAL_DAYS - 30)))
        name = f"{rng.choice(ADJECTIVES)} {subcat[:-1] if subcat.endswith('s') else subcat} {rng.integers(100,999)}"
        rows.append({
            "product_id": f"PROD{1000+i}",
            "product_name": name,
            "category": cat,
            "subcategory": subcat,
            "brand": brand,
            "supplier": supplier,
            "cost": cost,
            "selling_price": selling_price,
            "launch_date": launch_date.strftime("%Y-%m-%d"),
        })
    df = pd.DataFrame(rows)
 
    # Imperfections: missing cost (2%), cost > price on a few rows (data entry error, 1%)
    miss_idx = rng.choice(n, size=int(n * 0.02), replace=False)
    df.loc[miss_idx, "cost"] = np.nan
    bad_idx = rng.choice(n, size=int(n * 0.01), replace=False)
    df.loc[bad_idx, "cost"] = df.loc[bad_idx, "selling_price"] * 1.3
    # Inconsistent category labels (1.5%)
    inc_idx = rng.choice(n, size=int(n * 0.015), replace=False)
    df.loc[inc_idx, "category"] = df.loc[inc_idx, "category"].str.lower()
 
    return df
 
# Behavior weighting: give customers a "propensity" so some are one-time,
# some are heavy repeat buyers (realistic skew, not uniform randomness)
def customer_order_propensity(customers_df):
    # Pareto-like: most customers buy 1-2x, a smaller group buys often
    base = rng.pareto(2.2, size=len(customers_df)) + 0.15
    base = base / base.sum()
    return base
 
# 3 & 4. ORDERS + ORDER_ITEMS (generated together — orders depend on items)
def generate_orders_and_items(customers_df, products_df, n_orders=N_ORDERS):
    cust_ids = customers_df["customer_id"].values
    propensity = customer_order_propensity(customers_df)
 
    order_customers = rng.choice(cust_ids, size=n_orders, p=propensity)
    order_dates = random_dates(n_orders, weighted=True)
    # sort by date for realism
    order_pairs = sorted(zip(order_dates, order_customers), key=lambda x: x[0])
 
    order_rows = []
    item_rows = []
    item_counter = 0
 
    prod_ids = products_df["product_id"].values
    prod_price = dict(zip(products_df["product_id"], products_df["selling_price"]))
    prod_cost = dict(zip(products_df["product_id"], products_df["cost"]))
    # Give products a popularity skew (some sell far more than others)
    prod_popularity = rng.pareto(2.5, size=len(prod_ids)) + 0.1
    prod_popularity = prod_popularity / prod_popularity.sum()
 
    order_statuses = ["Completed", "Completed", "Completed", "Completed", "Cancelled", "Refunded"]
 
    for i, (odate, cust) in enumerate(order_pairs):
        order_id = f"ORD{500000+i}"
        channel = rng.choice(CHANNELS, p=CHANNEL_WEIGHTS)
        status = rng.choice(order_statuses)
        n_items = int(rng.choice([1, 1, 2, 2, 3, 4], p=[0.35, 0.25, 0.2, 0.1, 0.06, 0.04]))
        chosen_products = rng.choice(prod_ids, size=n_items, replace=False, p=prod_popularity)
 
        # Seasonal / random discount logic: higher discounts around holidays
        seasonal = seasonality_multiplier(odate)
        base_discount_prob = 0.25 if seasonal < 1.5 else 0.55
        order_discount_pct = float(rng.uniform(0, 0.30)) if rng.random() < base_discount_prob else 0.0
 
        order_total_revenue = 0.0
        for p in chosen_products:
            qty = int(rng.choice([1, 1, 1, 2, 3], p=[0.55, 0.2, 0.1, 0.1, 0.05]))
            unit_price = prod_price.get(p, 20.0)
            item_discount = round(order_discount_pct * float(rng.uniform(0.8, 1.0)), 3)
            cost = prod_cost.get(p, unit_price * 0.6)
            if pd.isna(cost):
                cost = unit_price * 0.6
            item_rows.append({
                "order_item_id": f"ITEM{item_counter:07d}",
                "order_id": order_id,
                "product_id": p,
                "quantity": qty,
                "unit_price": unit_price,
                "discount": item_discount,
                "cost": round(cost, 2),
            })
            order_total_revenue += qty * unit_price * (1 - item_discount)
            item_counter += 1
 
        shipping_cost = round(float(rng.uniform(0, 12)) if order_total_revenue < 50 else 0.0, 2)
 
        order_rows.append({
            "order_id": order_id,
            "customer_id": cust,
            "order_date": odate.strftime("%Y-%m-%d %H:%M:%S"),
            "order_status": status,
            "sales_channel": channel,
            "shipping_cost": shipping_cost,
            "discount": order_discount_pct,
        })
 
    orders_df = pd.DataFrame(order_rows)
    items_df = pd.DataFrame(item_rows)
 
    # ---- Imperfections ----
    # Missing shipping_cost (2%)
    idx = rng.choice(len(orders_df), size=int(len(orders_df) * 0.02), replace=False)
    orders_df.loc[idx, "shipping_cost"] = np.nan
    # Duplicate order rows (0.4%)
    dupes = orders_df.sample(int(len(orders_df) * 0.004), random_state=SEED)
    orders_df = pd.concat([orders_df, dupes], ignore_index=True)
    # Inconsistent status casing (1%)
    idx = rng.choice(len(orders_df), size=int(len(orders_df) * 0.01), replace=False)
    orders_df.loc[idx, "order_status"] = orders_df.loc[idx, "order_status"].str.lower()
    # A few negative/invalid quantities in order_items (data entry errors, 0.3%)
    idx = rng.choice(len(items_df), size=int(len(items_df) * 0.003), replace=False)
    items_df.loc[idx, "quantity"] = -1
    # Missing unit_price (1%)
    idx = rng.choice(len(items_df), size=int(len(items_df) * 0.01), replace=False)
    items_df.loc[idx, "unit_price"] = np.nan
 
    return orders_df, items_df
 
# 5. PAYMENTS
def generate_payments(orders_df, items_df):
    # compute order revenue from items to make payment_amount consistent
    items_df["_line_revenue"] = (items_df["quantity"].clip(lower=0) *
                                  items_df["unit_price"].fillna(0) *
                                  (1 - items_df["discount"].fillna(0)))
    order_rev = items_df.groupby("order_id")["_line_revenue"].sum().to_dict()
 
    rows = []
    for i, o in orders_df.drop_duplicates("order_id").iterrows():
        oid = o["order_id"]
        revenue = order_rev.get(oid, 0.0) + (0 if pd.isna(o["shipping_cost"]) else o["shipping_cost"])
        pay_date = pd.to_datetime(o["order_date"], errors="coerce")
        if pd.isna(pay_date):
            pay_date = START_DATE
        pay_date = pay_date + timedelta(hours=int(rng.integers(0, 6)))
        status = "Success" if str(o["order_status"]).lower() not in ("cancelled",) else rng.choice(["Failed", "Refunded"])
        rows.append({
            "payment_id": f"PAY{700000+i}",
            "order_id": oid,
            "payment_date": pay_date.strftime("%Y-%m-%d %H:%M:%S"),
            "payment_method": rng.choice(PAYMENT_METHODS, p=PAYMENT_METHOD_WEIGHTS),
            "payment_status": status,
            "payment_amount": round(max(revenue, 0), 2),
        })
    df = pd.DataFrame(rows)
    # missing payment_method (1.5%)
    idx = rng.choice(len(df), size=int(len(df) * 0.015), replace=False)
    df.loc[idx, "payment_method"] = np.nan
    return df
 
# 6. RETURNS
def generate_returns(orders_df, items_df, products_df, target_min=2000):
    merged = items_df.merge(orders_df[["order_id", "order_date", "order_status"]], on="order_id", how="left")
    merged = merged.merge(products_df[["product_id", "category"]], on="product_id", how="left")
 
    # Some categories have inherently higher return rates (Fashion, Electronics)
    cat_return_rate = {
        "Electronics": 0.09, "Fashion": 0.11, "Home & Kitchen": 0.04,
        "Beauty": 0.05, "Sports & Outdoors": 0.05, "Accessories": 0.04,
    }
    merged["_ret_prob"] = merged["category"].map(cat_return_rate).fillna(0.06)
    merged = merged[merged["order_status"].astype(str).str.lower() == "completed"]
    merged["_is_returned"] = rng.random(len(merged)) < merged["_ret_prob"]
    candidates = merged[merged["_is_returned"]].copy()
 
    if len(candidates) < target_min:
        extra = merged.sample(target_min - len(candidates), random_state=SEED, replace=True)
        candidates = pd.concat([candidates, extra], ignore_index=True)
 
    rows = []
    for i, r in candidates.reset_index(drop=True).iterrows():
        odate = pd.to_datetime(r["order_date"], errors="coerce")
        if pd.isna(odate):
            odate = START_DATE
        rdate = odate + timedelta(days=int(rng.integers(2, 30)))
        qty = max(1, int(r["quantity"])) if pd.notna(r["quantity"]) and r["quantity"] > 0 else 1
        ret_qty = int(rng.integers(1, qty + 1))
        unit_price = r["unit_price"] if pd.notna(r["unit_price"]) else 20.0
        refund = round(ret_qty * unit_price * (1 - (r["discount"] or 0)), 2)
        rows.append({
            "return_id": f"RET{900000+i}",
            "order_id": r["order_id"],
            "product_id": r["product_id"],
            "return_date": rdate.strftime("%Y-%m-%d"),
            "return_reason": rng.choice(RETURN_REASONS),
            "returned_quantity": ret_qty,
            "refund_amount": refund,
        })
    df = pd.DataFrame(rows)
    # missing return_reason (2%)
    idx = rng.choice(len(df), size=int(len(df) * 0.02), replace=False)
    df.loc[idx, "return_reason"] = np.nan
    return df
 
# 7. MARKETING CAMPAIGNS
def generate_marketing(n=N_CAMPAIGNS):
    channels = ["Paid Search", "Social Media", "Email", "Affiliate", "Display"]
    channel_efficiency = {  # rough conversion-rate-ish quality per channel
        "Paid Search": (0.03, 0.06), "Social Media": (0.015, 0.035),
        "Email": (0.05, 0.09), "Affiliate": (0.02, 0.04), "Display": (0.008, 0.02),
    }
    dates = random_dates(n, weighted=False)
    rows = []
    for i in range(n):
        ch = rng.choice(channels)
        impressions = int(rng.uniform(5000, 500000))
        ctr = float(rng.uniform(0.005, 0.045))
        clicks = int(impressions * ctr)
        conv_low, conv_high = channel_efficiency[ch]
        conv_rate = float(rng.uniform(conv_low, conv_high))
        conversions = int(clicks * conv_rate)
        cost_per_click = float(rng.uniform(0.3, 3.5))
        spend = round(clicks * cost_per_click, 2)
        avg_order_val = float(rng.uniform(45, 110))
        attributed_revenue = round(conversions * avg_order_val, 2)
        rows.append({
            "campaign_id": f"CAMP{i+1:04d}",
            "campaign_date": dates[i].strftime("%Y-%m-%d"),
            "channel": ch,
            "campaign_name": f"{ch.replace(' ', '_')}_{dates[i].strftime('%b%Y')}_{i+1}",
            "impressions": impressions,
            "clicks": clicks,
            "spend": spend,
            "conversions": conversions,
            "attributed_revenue": attributed_revenue,
        })
    df = pd.DataFrame(rows)
    idx = rng.choice(len(df), size=int(len(df) * 0.015), replace=False)
    df.loc[idx, "spend"] = np.nan
    return df
 
# 8. WEBSITE EVENTS (funnel)
def generate_website_events(customers_df, products_df, n_events=N_WEBSITE_EVENTS):
    cust_ids = customers_df["customer_id"].values
    prod_ids = products_df["product_id"].values
    # Empirically, with the funnel drop-off probabilities below, each session
    # produces ~2.0 events on average (most sessions stop after 1-2 stages).
    # Scale session count accordingly so total events reach the target.
    n_sessions = int(n_events / 1.9)
 
    rows = []
    event_counter = 0
    session_dates = random_dates(n_sessions, weighted=True)
 
    # Funnel drop-off probabilities (stage-to-stage conversion)
    stage_conv = {
        "site_visit": 1.0,
        "product_view": 0.62,
        "add_to_cart": 0.35,
        "checkout_start": 0.55,
        "purchase": 0.68,
    }
 
    for s in range(n_sessions):
        session_id = str(uuid.uuid4())[:12]
        cust = rng.choice(cust_ids) if rng.random() < 0.75 else None  # 25% anonymous/guest sessions
        device = rng.choice(DEVICES, p=DEVICE_WEIGHTS)
        source = rng.choice(TRAFFIC_SOURCES, p=TRAFFIC_WEIGHTS)
        base_time = session_dates[s]
        reached = True
        t_offset = 0
        for stage in FUNNEL_STAGES:
            if not reached:
                break
            prob = stage_conv[stage]
            if stage != "site_visit" and rng.random() > prob:
                reached = False
                continue
            prod = rng.choice(prod_ids) if stage in ("product_view", "add_to_cart", "checkout_start", "purchase") else None
            rows.append({
                "event_id": f"EVT{event_counter:08d}",
                "customer_id": cust,
                "session_id": session_id,
                "event_timestamp": (base_time + timedelta(minutes=t_offset)).strftime("%Y-%m-%d %H:%M:%S"),
                "device": device,
                "traffic_source": source,
                "event_type": stage,
                "product_id": prod,
            })
            event_counter += 1
            t_offset += int(rng.integers(1, 6))
            if event_counter >= n_events:
                break
        if event_counter >= n_events:
            break
 
    df = pd.DataFrame(rows)
    # missing device (1%)
    idx = rng.choice(len(df), size=int(len(df) * 0.01), replace=False)
    df.loc[idx, "device"] = np.nan
    return df
 
# MAIN
def main():
    print("Generating customers...")
    customers = generate_customers()
    print(f"  -> {len(customers):,} rows")
 
    print("Generating products...")
    products = generate_products()
    print(f"  -> {len(products):,} rows")
 
    print("Generating orders + order_items...")
    orders, items = generate_orders_and_items(customers, products)
    print(f"  -> {len(orders):,} orders, {len(items):,} order_items")
 
    print("Generating payments...")
    payments = generate_payments(orders, items)
    print(f"  -> {len(payments):,} rows")
 
    print("Generating returns...")
    returns = generate_returns(orders, items, products)
    print(f"  -> {len(returns):,} rows")
 
    print("Generating marketing campaigns...")
    marketing = generate_marketing()
    print(f"  -> {len(marketing):,} rows")
 
    print("Generating website events...")
    events = generate_website_events(customers, products)
    print(f"  -> {len(events):,} rows")
 
    items = items.drop(columns=[c for c in items.columns if c.startswith("_")], errors="ignore")
 
    customers.to_csv(os.path.join(OUT_DIR, "customers.csv"), index=False)
    products.to_csv(os.path.join(OUT_DIR, "products.csv"), index=False)
    orders.to_csv(os.path.join(OUT_DIR, "orders.csv"), index=False)
    items.to_csv(os.path.join(OUT_DIR, "order_items.csv"), index=False)
    payments.to_csv(os.path.join(OUT_DIR, "payments.csv"), index=False)
    returns.to_csv(os.path.join(OUT_DIR, "returns.csv"), index=False)
    marketing.to_csv(os.path.join(OUT_DIR, "marketing.csv"), index=False)
    events.to_csv(os.path.join(OUT_DIR, "website_events.csv"), index=False)
 
    print("\nAll files written to data/raw/")
    print("Done. Seed =", SEED, "(fully reproducible)")
 
if __name__ == "__main__":
    main()
 