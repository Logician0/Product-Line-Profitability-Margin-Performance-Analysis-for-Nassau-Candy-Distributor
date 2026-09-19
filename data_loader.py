"""
data_loader.py
--------------
Data Ingestion, Validation, Cleaning, and Enrichment Engine
for Nassau Candy Distributor Profitability & Margin Performance Analysis.
"""

import os
from pathlib import Path
from typing import Optional, Tuple, Dict
import pandas as pd
import numpy as np

# 5 Factory Master Metadata
FACTORY_COORDINATES: Dict[str, Dict] = {
    "Hicksville HQ Facility": {
        "lat": 40.7684,
        "lon": -73.5251,
        "city": "Hicksville",
        "state": "New York",
        "region": "Atlantic",
        "capacity_utilization": 0.88
    },
    "Livonia Specialty Plant": {
        "lat": 42.3684,
        "lon": -83.3527,
        "city": "Livonia",
        "state": "Michigan",
        "region": "Interior",
        "capacity_utilization": 0.82
    },
    "Dallas Confectionery Works": {
        "lat": 32.7767,
        "lon": -96.7970,
        "city": "Dallas",
        "state": "Texas",
        "region": "Interior",
        "capacity_utilization": 0.75
    },
    "Los Angeles Sweet Lab": {
        "lat": 34.0522,
        "lon": -118.2437,
        "city": "Los Angeles",
        "state": "California",
        "region": "Pacific",
        "capacity_utilization": 0.68
    },
    "Jacksonville Sugar Mill": {
        "lat": 30.3322,
        "lon": -81.6557,
        "city": "Jacksonville",
        "state": "Florida",
        "region": "Gulf",
        "capacity_utilization": 0.62
    }
}

# Product to Factory Mapping
PRODUCT_FACTORY_MAP: Dict[str, str] = {
    "Wonka Bar - Milk Chocolate": "Hicksville HQ Facility",
    "Wonka Bar - Scrumdiddlyumptious": "Hicksville HQ Facility",
    "Wonka Bar - Triple Dazzle Caramel": "Livonia Specialty Plant",
    "Wonka Bar - Fudge Mallows": "Livonia Specialty Plant",
    "Wonka Bar - Nutty Crunch Surprise": "Dallas Confectionery Works",
    "Lickable Wallpaper": "Dallas Confectionery Works",
    "Kazookles": "Los Angeles Sweet Lab",
    "Wonka Gum": "Los Angeles Sweet Lab",
    "Fizzy Lifting Drinks": "Los Angeles Sweet Lab",
    "Everlasting Gobstopper": "Jacksonville Sugar Mill",
    "Hair Toffee": "Jacksonville Sugar Mill",
    "Laffy Taffy": "Jacksonville Sugar Mill",
    "SweeTARTS": "Jacksonville Sugar Mill",
    "Nerds": "Jacksonville Sugar Mill",
    "Fun Dip": "Jacksonville Sugar Mill"
}


def find_dataset_file() -> Optional[Path]:
    """Search for the Nassau Candy CSV file in current directory."""
    possible_names = [
        "Nassau Candy Distributor.csv",
        "nassau_candy.csv",
        "Nassau_Candy_Distributor.csv",
        "nassau_candy_distributor.csv"
    ]
    for name in possible_names:
        p = Path(name)
        if p.exists() and p.is_file():
            return p
    return None


def load_and_clean_data(file_path: Optional[str] = None) -> Tuple[pd.DataFrame, Dict]:
    """
    Load raw CSV data, perform validation and cleaning, recalculate financials,
    and enrich with product, temporal, and factory dimensions.

    Returns:
        Tuple[pd.DataFrame, Dict]: (Cleaned DataFrame, Audit Report Dict)
    """
    # 1. Ingestion check
    if file_path is None or not Path(file_path).exists():
        found = find_dataset_file()
        if found:
            file_path = str(found)
        else:
            from generate_synthetic_data import generate_synthetic_nassau_data
            file_path = "nassau_candy.csv"
            generate_synthetic_nassau_data(output_path=file_path)

    raw_df = pd.read_csv(file_path)
    initial_rows = len(raw_df)

    # 2. String Standardization
    df = raw_df.copy()
    string_cols = ["Division", "Region", "Product Name", "City", "State/Province", "Ship Mode"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Standardize Product Names (clean hyphens, inconsistent spaces)
    if "Product Name" in df.columns:
        df["Product Name"] = df["Product Name"].str.replace("Wonka Bar -Scrumdiddlyumptious", "Wonka Bar - Scrumdiddlyumptious", regex=False)

    # 3. Numeric Conversions & Filtering
    for col in ["Sales", "Cost", "Gross Profit", "Units"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove invalid records: non-positive sales, cost, units, or cost > sales
    valid_mask = (
        (df["Sales"] > 0) &
        (df["Cost"] >= 0) &
        (df["Units"] > 0) &
        (df["Sales"] >= df["Cost"])
    )
    df = df[valid_mask].copy()

    # 4. Date Parsing
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="mixed", dayfirst=True)
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="mixed", dayfirst=True)

    # 5. Financial Recalculation (Enforce Single Source of Truth)
    df["Gross Profit"] = df["Sales"] - df["Cost"]
    df["Gross Margin %"] = (df["Gross Profit"] / df["Sales"]) * 100
    df["Gross Margin Ratio"] = df["Gross Profit"] / df["Sales"]
    df["Profit per Unit"] = df["Gross Profit"] / df["Units"]
    df["Cost Ratio %"] = (df["Cost"] / df["Sales"]) * 100
    df["Unit Price"] = df["Sales"] / df["Units"]
    df["Unit Cost"] = df["Cost"] / df["Units"]

    # 6. Temporal Dimensions
    df["YearMonth"] = df["Order Date"].dt.to_period("M").astype(str)
    df["Year"] = df["Order Date"].dt.year
    df["Quarter"] = df["Order Date"].dt.to_period("Q").astype(str)
    df["DayOfWeek"] = df["Order Date"].dt.day_name()

    # 7. Factory Enrichment
    df["Factory"] = df["Product Name"].map(PRODUCT_FACTORY_MAP).fillna("Hicksville HQ Facility")
    df["Factory Lat"] = df["Factory"].apply(lambda f: FACTORY_COORDINATES.get(f, {}).get("lat", 40.7684))
    df["Factory Lon"] = df["Factory"].apply(lambda f: FACTORY_COORDINATES.get(f, {}).get("lon", -73.5251))
    df["Factory City"] = df["Factory"].apply(lambda f: FACTORY_COORDINATES.get(f, {}).get("city", "Hicksville"))
    df["Factory State"] = df["Factory"].apply(lambda f: FACTORY_COORDINATES.get(f, {}).get("state", "New York"))

    # 8. Audit Statistics
    audit_report = {
        "initial_rows": initial_rows,
        "cleaned_rows": len(df),
        "removed_rows": initial_rows - len(df),
        "total_revenue": df["Sales"].sum(),
        "total_cost": df["Cost"].sum(),
        "total_profit": df["Gross Profit"].sum(),
        "overall_margin_pct": (df["Gross Profit"].sum() / df["Sales"].sum()) * 100 if df["Sales"].sum() > 0 else 0,
        "total_units": df["Units"].sum(),
        "unique_products": df["Product Name"].nunique(),
        "unique_divisions": df["Division"].nunique(),
        "date_range_start": df["Order Date"].min(),
        "date_range_end": df["Order Date"].max()
    }

    return df, audit_report


def get_factory_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate operational and financial metrics by manufacturing plant."""
    factory_agg = df.groupby("Factory").agg(
        Total_Sales=("Sales", "sum"),
        Total_Cost=("Cost", "sum"),
        Total_Profit=("Gross Profit", "sum"),
        Total_Units=("Units", "sum"),
        Orders_Count=("Order ID", "nunique"),
        Product_Count=("Product Name", "nunique")
    ).reset_index()

    factory_agg["Gross_Margin_%"] = (factory_agg["Total_Profit"] / factory_agg["Total_Sales"]) * 100
    factory_agg["Profit_per_Unit"] = factory_agg["Total_Profit"] / factory_agg["Total_Units"]
    
    # Merge coordinate and capacity details
    factory_agg["Lat"] = factory_agg["Factory"].apply(lambda f: FACTORY_COORDINATES.get(f, {}).get("lat"))
    factory_agg["Lon"] = factory_agg["Factory"].apply(lambda f: FACTORY_COORDINATES.get(f, {}).get("lon"))
    factory_agg["City"] = factory_agg["Factory"].apply(lambda f: FACTORY_COORDINATES.get(f, {}).get("city"))
    factory_agg["State"] = factory_agg["Factory"].apply(lambda f: FACTORY_COORDINATES.get(f, {}).get("state"))
    factory_agg["Utilization_%"] = factory_agg["Factory"].apply(lambda f: FACTORY_COORDINATES.get(f, {}).get("capacity_utilization", 0.7) * 100)

    return factory_agg.sort_values(by="Total_Profit", ascending=False)
