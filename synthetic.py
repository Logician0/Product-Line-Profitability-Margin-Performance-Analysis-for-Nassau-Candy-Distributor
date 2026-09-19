import numpy as np
import pandas as pd
import datetime

# quick lookup for the factories
factories = {
    'Wonka Bar - Milk Chocolate': ('Hicksville HQ Facility', 40.7684, -73.5251),
    'Wonka Bar - Scrumdiddlyumptious': ('Hicksville HQ Facility', 40.7684, -73.5251),
    'Wonka Bar - Triple Dazzle Caramel': ('Livonia Specialty Plant', 42.3684, -83.3527),
    'Wonka Bar - Fudge Mallows': ('Livonia Specialty Plant', 42.3684, -83.3527),
    'Wonka Bar - Nutty Crunch Surprise': ('Dallas Confectionery Works', 32.7767, -96.7970),
    'Lickable Wallpaper': ('Dallas Confectionery Works', 32.7767, -96.7970),
    'Kazookles': ('Los Angeles Sweet Lab', 34.0522, -118.2437),
    'Wonka Gum': ('Los Angeles Sweet Lab', 34.0522, -118.2437),
    'Fizzy Lifting Drinks': ('Los Angeles Sweet Lab', 34.0522, -118.2437),
    'Everlasting Gobstopper': ('Jacksonville Sugar Mill', 30.3322, -81.6557),
    'Hair Toffee': ('Jacksonville Sugar Mill', 30.3322, -81.6557),
    'Laffy Taffy': ('Jacksonville Sugar Mill', 30.3322, -81.6557),
    'SweeTARTS': ('Jacksonville Sugar Mill', 30.3322, -81.6557),
    'Nerds': ('Jacksonville Sugar Mill', 30.3322, -81.6557),
    'Fun Dip': ('Jacksonville Sugar Mill', 30.3322, -81.6557)
}

catalog = [
    ('Chocolate', 'CHO-SCR-58000', 'Wonka Bar - Scrumdiddlyumptious', 3.60, 1.10, 0.20),
    ('Chocolate', 'CHO-TRI-54000', 'Wonka Bar - Triple Dazzle Caramel', 3.75, 1.30, 0.20),
    ('Chocolate', 'CHO-MIL-31000', 'Wonka Bar - Milk Chocolate', 3.25, 1.14, 0.21),
    ('Chocolate', 'CHO-NUT-13000', 'Wonka Bar - Nutty Crunch Surprise', 3.49, 1.00, 0.18),
    ('Chocolate', 'CHO-FUD-51000', 'Wonka Bar - Fudge Mallows', 3.60, 1.20, 0.17),
    ('Other', 'OTH-LIC-88000', 'Lickable Wallpaper', 20.00, 10.00, 0.015),
    ('Other', 'OTH-KAZ-22000', 'Kazookles', 3.25, 3.00, 0.012),
    ('Other', 'OTH-GUM-11000', 'Wonka Gum', 1.25, 0.60, 0.010),
    ('Sugar', 'SUG-GOB-44000', 'Everlasting Gobstopper', 10.00, 2.00, 0.0005),
    ('Sugar', 'SUG-TOF-77000', 'Hair Toffee', 4.50, 1.00, 0.0005),
    ('Sugar', 'SUG-FIZ-66000', 'Fizzy Lifting Drinks', 3.75, 1.50, 0.0005),
    ('Sugar', 'SUG-TAF-99000', 'Laffy Taffy', 1.99, 0.75, 0.0005),
    ('Sugar', 'SUG-SWE-33000', 'SweeTARTS', 1.50, 0.80, 0.0005),
    ('Sugar', 'SUG-NER-55000', 'Nerds', 1.50, 0.80, 0.0003),
    ('Sugar', 'SUG-DIP-12000', 'Fun Dip', 1.50, 0.90, 0.0002)
]

regions = ['Pacific', 'Atlantic', 'Interior', 'Gulf']
locations = {
    'Pacific': ('Los Angeles', 'California', '90049'),
    'Atlantic': ('Philadelphia', 'Pennsylvania', '19143'),
    'Interior': ('Naperville', 'Illinois', '60540'),
    'Gulf': ('Henderson', 'Kentucky', '42420')
}

def make_fake_data(n=10194, path='nassau_candy.csv'):
    np.random.seed(42)
    start = datetime.date(2024, 1, 2)
    end = datetime.date(2025, 12, 31)
    day_span = (end - start).days

    w = [item[5] for item in catalog]
    weights = [x / sum(w) for x in w]
    
    rows = []
    for i in range(1, n + 1):
        pick = np.random.choice(len(catalog), p=weights)
        div, pid, name, price, unit_cost, _ = catalog[pick]
        
        ord_date = start + datetime.timedelta(days=int(np.random.randint(0, day_span)))
        ship_date = ord_date + datetime.timedelta(days=int(np.random.choice([2, 3, 4, 5])))
        
        reg = np.random.choice(regions, p=[0.32, 0.29, 0.23, 0.16])
        city, state, zip_code = locations[reg]
        
        # most orders are small batches
        units = int(np.random.choice([1, 2, 3, 4, 6, 8, 10], p=[0.28, 0.28, 0.20, 0.12, 0.07, 0.03, 0.02]))
        sales = round(price * units, 2)
        cost = round(unit_cost * units, 2)
        profit = round(sales - cost, 2)
        
        rows.append({
            'Row ID': i,
            'Order ID': f"US-{ord_date.year}-{100000 + i % 5000}-{pid[:7]}",
            'Order Date': ord_date.strftime('%d-%m-%Y'),
            'Ship Date': ship_date.strftime('%d-%m-%Y'),
            'Ship Mode': np.random.choice(['Standard Class', 'Second Class', 'First Class'], p=[0.65, 0.22, 0.13]),
            'Customer ID': 100000 + (i * 37) % 90000,
            'Country/Region': 'United States',
            'City': city,
            'State/Province': state,
            'Postal Code': zip_code,
            'Division': div,
            'Region': reg,
            'Product ID': pid,
            'Product Name': name,
            'Sales': sales,
            'Units': units,
            'Gross Profit': profit,
            'Cost': cost
        })
        
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    return df

if __name__ == '__main__':
    make_fake_data()
