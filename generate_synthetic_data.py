"""
generate_synthetic_data.py
---------------------------
Synthetic Data Generator for Nassau Candy Distributor.
Generates realistic product, sales, cost, and logistics transactions
matching the Nassau Candy schema if the primary dataset is absent or for testing.
"""

import pandas as pd
import numpy as np
import datetime
from pathlib import Path

# Factory Master Data
FACTORY_MASTER = {
    "Hicksville HQ Facility": {"lat": 40.7684, "lon": -73.5251, "city": "Hicksville", "state": "New York"},
    "Livonia Specialty Plant": {"lat": 42.3684, "lon": -83.3527, "city": "Livonia", "state": "Michigan"},
    "Dallas Confectionery Works": {"lat": 32.7767, "lon": -96.7970, "city": "Dallas", "state": "Texas"},
    "Los Angeles Sweet Lab": {"lat": 34.0522, "lon": -118.2437, "city": "Los Angeles", "state": "California"},
    "Jacksonville Sugar Mill": {"lat": 30.3322, "lon": -81.6557, "city": "Jacksonville", "state": "Florida"}
}

# Product Catalog with Economics & Factory Mapping
PRODUCT_CATALOG = [
    {
        "Division": "Chocolate",
        "Product ID": "CHO-SCR-58000",
        "Product Name": "Wonka Bar - Scrumdiddlyumptious",
        "Unit_Sales": 3.60,
        "Unit_Cost": 1.10,
        "Factory": "Hicksville HQ Facility",
        "Weight": 0.20
    },
    {
        "Division": "Chocolate",
        "Product ID": "CHO-TRI-54000",
        "Product Name": "Wonka Bar - Triple Dazzle Caramel",
        "Unit_Sales": 3.75,
        "Unit_Cost": 1.30,
        "Factory": "Livonia Specialty Plant",
        "Weight": 0.20
    },
    {
        "Division": "Chocolate",
        "Product ID": "CHO-MIL-31000",
        "Product Name": "Wonka Bar - Milk Chocolate",
        "Unit_Sales": 3.25,
        "Unit_Cost": 1.14,
        "Factory": "Hicksville HQ Facility",
        "Weight": 0.21
    },
    {
        "Division": "Chocolate",
        "Product ID": "CHO-NUT-13000",
        "Product Name": "Wonka Bar - Nutty Crunch Surprise",
        "Unit_Sales": 3.49,
        "Unit_Cost": 1.00,
        "Factory": "Dallas Confectionery Works",
        "Weight": 0.18
    },
    {
        "Division": "Chocolate",
        "Product ID": "CHO-FUD-51000",
        "Product Name": "Wonka Bar - Fudge Mallows",
        "Unit_Sales": 3.60,
        "Unit_Cost": 1.20,
        "Factory": "Livonia Specialty Plant",
        "Weight": 0.17
    },
    {
        "Division": "Other",
        "Product ID": "OTH-LIC-88000",
        "Product Name": "Lickable Wallpaper",
        "Unit_Sales": 20.00,
        "Unit_Cost": 10.00,
        "Factory": "Dallas Confectionery Works",
        "Weight": 0.015
    },
    {
        "Division": "Other",
        "Product ID": "OTH-KAZ-22000",
        "Product Name": "Kazookles",
        "Unit_Sales": 3.25,
        "Unit_Cost": 3.00,
        "Factory": "Los Angeles Sweet Lab",
        "Weight": 0.012
    },
    {
        "Division": "Other",
        "Product ID": "OTH-GUM-11000",
        "Product Name": "Wonka Gum",
        "Unit_Sales": 1.25,
        "Unit_Cost": 0.60,
        "Factory": "Los Angeles Sweet Lab",
        "Weight": 0.010
    },
    {
        "Division": "Sugar",
        "Product ID": "SUG-GOB-44000",
        "Product Name": "Everlasting Gobstopper",
        "Unit_Sales": 10.00,
        "Unit_Cost": 2.00,
        "Factory": "Jacksonville Sugar Mill",
        "Weight": 0.0005
    },
    {
        "Division": "Sugar",
        "Product ID": "SUG-TOF-77000",
        "Product Name": "Hair Toffee",
        "Unit_Sales": 4.50,
        "Unit_Cost": 1.00,
        "Factory": "Jacksonville Sugar Mill",
        "Weight": 0.0005
    },
    {
        "Division": "Sugar",
        "Product ID": "SUG-FIZ-66000",
        "Product Name": "Fizzy Lifting Drinks",
        "Unit_Sales": 3.75,
        "Unit_Cost": 1.50,
        "Factory": "Los Angeles Sweet Lab",
        "Weight": 0.0005
    },
    {
        "Division": "Sugar",
        "Product ID": "SUG-TAF-99000",
        "Product Name": "Laffy Taffy",
        "Unit_Sales": 1.99,
        "Unit_Cost": 0.75,
        "Factory": "Jacksonville Sugar Mill",
        "Weight": 0.0005
    },
    {
        "Division": "Sugar",
        "Product ID": "SUG-SWE-33000",
        "Product Name": "SweeTARTS",
        "Unit_Sales": 1.50,
        "Unit_Cost": 0.80,
        "Factory": "Jacksonville Sugar Mill",
        "Weight": 0.0005
    },
    {
        "Division": "Sugar",
        "Product ID": "SUG-NER-55000",
        "Product Name": "Nerds",
        "Unit_Sales": 1.50,
        "Unit_Cost": 0.80,
        "Factory": "Jacksonville Sugar Mill",
        "Weight": 0.0003
    },
    {
        "Division": "Sugar",
        "Product ID": "SUG-DIP-12000",
        "Product Name": "Fun Dip",
        "Unit_Sales": 1.50,
        "Unit_Cost": 0.90,
        "Factory": "Jacksonville Sugar Mill",
        "Weight": 0.0002
    }
]

REGIONS = ["Pacific", "Atlantic", "Interior", "Gulf"]
REGION_PROBS = [0.32, 0.29, 0.23, 0.16]

SHIP_MODES = ["Standard Class", "Second Class", "First Class", "Same Day"]
SHIP_PROBS = [0.60, 0.20, 0.15, 0.05]

SAMPLE_LOCATIONS = {
    "Pacific": [
        {"city": "Los Angeles", "state": "California", "postal": "90049"},
        {"city": "San Francisco", "state": "California", "postal": "94107"},
        {"city": "Seattle", "state": "Washington", "postal": "98101"},
        {"city": "Portland", "state": "Oregon", "postal": "97201"}
    ],
    "Atlantic": [
        {"city": "Philadelphia", "state": "Pennsylvania", "postal": "19143"},
        {"city": "New York City", "state": "New York", "postal": "10001"},
        {"city": "Boston", "state": "Massachusetts", "postal": "02108"},
        {"city": "Newark", "state": "New Jersey", "postal": "07102"}
    ],
    "Interior": [
        {"city": "Houston", "state": "Texas", "postal": "77095"},
        {"city": "Naperville", "state": "Illinois", "postal": "60540"},
        {"city": "Chicago", "state": "Illinois", "postal": "60601"},
        {"city": "Columbus", "state": "Ohio", "postal": "43215"}
    ],
    "Gulf": [
        {"city": "Henderson", "state": "Kentucky", "postal": "42420"},
        {"city": "Athens", "state": "Georgia", "postal": "30605"},
        {"city": "Springfield", "state": "Virginia", "postal": "22153"},
        {"city": "Tampa", "state": "Florida", "postal": "33602"}
    ]
}


def generate_synthetic_nassau_data(
    num_rows: int = 10194,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
    seed: int = 42,
    output_path: str = "nassau_candy.csv"
) -> pd.DataFrame:
    """
    Generate synthetic transactions matching Nassau Candy dataset structure.
    """
    np.random.seed(seed)
    
    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    days_range = (end_dt - start_dt).days

    prod_weights = [p["Weight"] for p in PRODUCT_CATALOG]
    prod_weights = [w / sum(prod_weights) for w in prod_weights]

    rows = []
    
    for i in range(1, num_rows + 1):
        # Product selection
        prod = np.random.choice(PRODUCT_CATALOG, p=prod_weights)
        
        # Order Date
        rand_days = np.random.randint(0, days_range + 1)
        order_date = start_dt + datetime.timedelta(days=rand_days)
        ship_date = order_date + datetime.timedelta(days=int(np.random.choice([2, 3, 4, 5, 6])))
        
        # Region & Geography
        region = np.random.choice(REGIONS, p=REGION_PROBS)
        loc = np.random.choice(SAMPLE_LOCATIONS[region])
        
        # Customer ID & Ship Mode
        cust_id = np.random.randint(100000, 199999)
        ship_mode = np.random.choice(SHIP_MODES, p=SHIP_PROBS)
        order_id = f"US-{order_date.year}-{cust_id}-{prod['Product ID'][:7]}"
        
        # Units and Financials
        units = int(np.random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14], p=[0.25, 0.25, 0.18, 0.12, 0.08, 0.04, 0.03, 0.02, 0.01, 0.01, 0.005, 0.005]))
        sales = round(prod["Unit_Sales"] * units, 2)
        cost = round(prod["Unit_Cost"] * units, 2)
        gross_profit = round(sales - cost, 2)
        
        rows.append({
            "Row ID": i,
            "Order ID": order_id,
            "Order Date": order_date.strftime("%d-%m-%Y"),
            "Ship Date": ship_date.strftime("%d-%m-%Y"),
            "Ship Mode": ship_mode,
            "Customer ID": cust_id,
            "Country/Region": "United States",
            "City": loc["city"],
            "State/Province": loc["state"],
            "Postal Code": loc["postal"],
            "Division": prod["Division"],
            "Region": region,
            "Product ID": prod["Product ID"],
            "Product Name": prod["Product Name"],
            "Sales": sales,
            "Units": units,
            "Gross Profit": gross_profit,
            "Cost": cost
        })

    df = pd.DataFrame(rows)
    if output_path:
        df.to_csv(output_path, index=False)
        print(f"Generated {len(df)} synthetic rows saved to {output_path}")
    return df


if __name__ == "__main__":
    generate_synthetic_nassau_data(num_rows=10194, output_path="nassau_candy.csv")
