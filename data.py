import os
import pandas as pd
from synthetic import factories, make_fake_data

def get_clean_data(file_name=None):
    # look for csv file or just make one quietly
    files_to_check = [
        file_name,
        'Nassau Candy Distributor.csv',
        'nassau_candy.csv',
        'nassau_candy_distributor.csv'
    ]
    path = None
    for f in files_to_check:
        if f and os.path.exists(f):
            path = f
            break
            
    if not path:
        path = 'nassau_candy.csv'
        make_fake_data(path=path)
        
    df = pd.read_csv(path)
    
    # trim string spaces
    str_cols = ['Division', 'Region', 'Product Name', 'City', 'State/Province', 'Ship Mode']
    for c in str_cols:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
            
    # fix that one typo in the dataset
    df['Product Name'] = df['Product Name'].str.replace('Wonka Bar -Scrumdiddlyumptious', 'Wonka Bar - Scrumdiddlyumptious', regex=False)
    
    # numeric check
    for c in ['Sales', 'Cost', 'Units']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
        
    df = df[(df['Sales'] > 0) & (df['Cost'] >= 0) & (df['Units'] > 0)].copy()
    
    # parse dates
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='mixed', dayfirst=True)
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='mixed', dayfirst=True)
    
    # recalc profit and margins so math is clean
    df['Gross Profit'] = df['Sales'] - df['Cost']
    df['Gross Margin %'] = (df['Gross Profit'] / df['Sales']) * 100.0
    df['Profit per Unit'] = df['Gross Profit'] / df['Units']
    df['Cost Ratio %'] = (df['Cost'] / df['Sales']) * 100.0
    df['YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)
    
    # add factory info if available
    df['Factory'] = df['Product Name'].apply(lambda x: factories.get(x, ('Hicksville HQ Facility', 40.7684, -73.5251))[0])
    
    return df
