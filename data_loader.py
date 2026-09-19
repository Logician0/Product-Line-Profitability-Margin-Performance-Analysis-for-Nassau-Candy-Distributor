import os
import pandas as pd
from pathlib import Path
from generate_data import FACTORIES, create_dataset

def load_data(file_path=None):
    # Check for existing data file, or generate silently without drama
    candidates = [
        file_path,
        'Nassau Candy Distributor.csv',
        'nassau_candy.csv',
        'nassau_candy_distributor.csv'
    ]
    target = None
    for c in candidates:
        if c and os.path.exists(c):
            target = c
            break
            
    if not target:
        target = 'nassau_candy.csv'
        create_dataset(filename=target)
        
    df = pd.read_csv(target)
    
    # Clean whitespace and standard names
    for col in ['Division', 'Region', 'Product Name', 'City', 'State/Province', 'Ship Mode']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # Quick fix for known legacy typo
    df['Product Name'] = df['Product Name'].str.replace('Wonka Bar -Scrumdiddlyumptious', 'Wonka Bar - Scrumdiddlyumptious', regex=False)
    
    # Financial types & row validity
    for col in ['Sales', 'Cost', 'Units']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    df = df[(df['Sales'] > 0) & (df['Cost'] >= 0) & (df['Units'] > 0)].copy()
    
    # Parse dates cleanly
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='mixed', dayfirst=True)
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='mixed', dayfirst=True)
    
    # Recompute to guarantee zero math drift
    df['Gross Profit'] = df['Sales'] - df['Cost']
    df['Gross Margin %'] = (df['Gross Profit'] / df['Sales']) * 100.0
    df['Profit per Unit'] = df['Gross Profit'] / df['Units']
    df['Cost Ratio %'] = (df['Cost'] / df['Sales']) * 100.0
    df['YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)
    
    # Factory lookup (maps product to primary facility)
    df['Factory'] = df['Product Name'].apply(lambda x: FACTORIES.get(x, ('Hicksville HQ Facility', 40.7684, -73.5251))[0])
    
    return df
