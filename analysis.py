import pandas as pd
import numpy as np

def get_kpis(df):
    if df.empty:
        return {'sales': 0, 'cost': 0, 'profit': 0, 'margin': 0, 'units': 0, 'orders': 0, 'ppu': 0}
    s = df['Sales'].sum()
    c = df['Cost'].sum()
    p = df['Gross Profit'].sum()
    u = df['Units'].sum()
    o = df['Order ID'].nunique()
    return {
        'sales': s,
        'cost': c,
        'profit': p,
        'margin': (p / s * 100.0) if s > 0 else 0,
        'units': u,
        'orders': o,
        'ppu': (p / u) if u > 0 else 0,
        'aov': (s / o) if o > 0 else 0
    }

def get_product_summary(df):
    if df.empty:
        return pd.DataFrame()
    tot_s = df['Sales'].sum()
    tot_p = df['Gross Profit'].sum()
    
    prod = df.groupby(['Product Name', 'Division', 'Factory']).agg(
        Total_Sales=('Sales', 'sum'),
        Total_Cost=('Cost', 'sum'),
        Total_Profit=('Gross Profit', 'sum'),
        Total_Units=('Units', 'sum'),
        Orders=('Order ID', 'nunique')
    ).reset_index()
    
    prod['Gross_Margin_%'] = (prod['Total_Profit'] / prod['Total_Sales']) * 100.0
    prod['Cost_Ratio_%'] = (prod['Total_Cost'] / prod['Total_Sales']) * 100.0
    prod['Profit_per_Unit'] = prod['Total_Profit'] / prod['Total_Units']
    prod['Revenue_Share_%'] = (prod['Total_Sales'] / tot_s * 100.0) if tot_s > 0 else 0
    prod['Profit_Share_%'] = (prod['Total_Profit'] / tot_p * 100.0) if tot_p > 0 else 0
    
    # Calculate monthly margin volatility
    m = df.groupby(['Product Name', 'YearMonth']).agg(
        ms=('Sales', 'sum'),
        mp=('Gross Profit', 'sum')
    ).reset_index()
    m['mm'] = (m['mp'] / m['ms']) * 100.0
    vol = m.groupby('Product Name')['mm'].std().fillna(0).round(2).reset_index()
    vol.columns = ['Product Name', 'Margin_Volatility_%']
    
    prod = prod.merge(vol, on='Product Name', how='left')
    prod['Margin_Volatility_%'] = prod['Margin_Volatility_%'].fillna(0)

    # Classify products based on median splits
    med_s = prod['Total_Sales'].median()
    med_m = prod['Gross_Margin_%'].median()
    
    def tag_sku(r):
        if r['Cost_Ratio_%'] >= 70.0:
            return 'Supplier Cost Trap'
        if r['Total_Sales'] >= med_s and r['Gross_Margin_%'] >= med_m:
            return 'Cash Cow / Core Star'
        if r['Total_Sales'] >= med_s and r['Gross_Margin_%'] < med_m:
            return 'Volume Anchor (Needs Reprice)'
        if r['Total_Sales'] < med_s and r['Gross_Margin_%'] >= med_m:
            return 'High-Margin Sleeper'
        return 'Tail Drag (Evaluate Dropping)'
        
    prod['Classification'] = prod.apply(tag_sku, axis=1)
    return prod.sort_values(by='Total_Profit', ascending=False).reset_index(drop=True)

def get_division_summary(df):
    if df.empty:
        return pd.DataFrame()
    tot_s = df['Sales'].sum()
    tot_p = df['Gross Profit'].sum()
    
    div = df.groupby('Division').agg(
        Total_Sales=('Sales', 'sum'),
        Total_Cost=('Cost', 'sum'),
        Total_Profit=('Gross Profit', 'sum'),
        Total_Units=('Units', 'sum'),
        Orders=('Order ID', 'nunique'),
        SKUs=('Product Name', 'nunique')
    ).reset_index()
    
    div['Gross_Margin_%'] = (div['Total_Profit'] / div['Total_Sales']) * 100.0
    div['Cost_Ratio_%'] = (div['Total_Cost'] / div['Total_Sales']) * 100.0
    div['Profit_per_Unit'] = div['Total_Profit'] / div['Total_Units']
    div['Revenue_Share_%'] = (div['Total_Sales'] / tot_s * 100.0) if tot_s > 0 else 0
    div['Profit_Share_%'] = (div['Total_Profit'] / tot_p * 100.0) if tot_p > 0 else 0
    
    return div.sort_values(by='Total_Profit', ascending=False).reset_index(drop=True)

def get_pareto(df, col='Gross Profit'):
    if df.empty:
        return pd.DataFrame(), {}
    
    p = df.groupby('Product Name')[col].sum().reset_index()
    p = p.sort_values(by=col, ascending=False).reset_index(drop=True)
    
    tot = p[col].sum()
    p['Cumulative'] = p[col].cumsum()
    p['Cumulative_%'] = (p['Cumulative'] / tot) * 100.0
    p['Share_%'] = (p[col] / tot) * 100.0
    p['Rank'] = range(1, len(p) + 1)
    p['Catalog_Pct'] = (p['Rank'] / len(p)) * 100.0
    
    # 80% line count
    under_80 = p[p['Cumulative_%'] <= 80.0]
    count_80 = len(under_80) + 1 if len(under_80) < len(p) else len(p)
    
    # Herfindahl index (sum of squared market share percentages)
    hhi = (p['Share_%'] ** 2).sum()
    
    meta = {
        'total': tot,
        'skus_for_80': count_80,
        'pct_catalog_for_80': (count_80 / len(p)) * 100.0,
        'top_sku': p.iloc[0]['Product Name'],
        'top_sku_share': p.iloc[0]['Share_%'],
        'hhi': round(hhi, 1)
    }
    return p, meta

def get_cost_diagnostics(df):
    prod = get_product_summary(df)
    if prod.empty:
        return pd.DataFrame()
        
    def flag_sku(r):
        reasons = []
        urgency = 'Normal'
        
        # 1. Supplier Cost Trap
        if r['Cost_Ratio_%'] >= 70.0:
            reasons.append('Supplier COGS exceeds 70% of price')
            urgency = 'High'
            
        # 2. Volume pricing leak
        if r['Revenue_Share_%'] > 5.0 and r['Gross_Margin_%'] < 55.0:
            reasons.append('High turnover with depressed margin; +5% reprice recommended')
            if urgency != 'High':
                urgency = 'Medium'
                
        # 3. Low profit tail
        if r['Total_Sales'] < 150.0 and r['Gross_Margin_%'] < 50.0:
            reasons.append('Low sales, weak margin; candidate to delist')
            if urgency != 'High':
                urgency = 'Medium'
                
        # 4. Hidden gem
        if r['Gross_Margin_%'] >= 75.0 and r['Total_Sales'] < 300.0:
            reasons.append('Exceptional margin (>75%) with low volume; promote aggressively')
            urgency = 'Opportunity'
            
        if not reasons:
            reasons.append('Healthy unit economics; maintain current pricing')
            
        return pd.Series([' | '.join(reasons), urgency], index=['Action_Plan', 'Urgency'])
        
    res = prod.apply(flag_sku, axis=1)
    prod['Action_Plan'] = res['Action_Plan']
    prod['Urgency'] = res['Urgency']
    return prod

def simulate_price_impact(df, product_name, price_pct=5.0, cost_pct=0.0, elasticity=-0.3):
    p_df = df[df['Product Name'] == product_name]
    if p_df.empty:
        return None
        
    base_s = float(p_df['Sales'].sum())
    base_c = float(p_df['Cost'].sum())
    base_p = float(p_df['Gross Profit'].sum())
    base_u = int(p_df['Units'].sum())
    
    price_0 = base_s / base_u
    cost_0 = base_c / base_u
    
    # Elasticity formula: % delta Q = e * % delta P
    price_1 = price_0 * (1.0 + price_pct / 100.0)
    cost_1 = cost_0 * (1.0 - cost_pct / 100.0)
    
    unit_pct_change = elasticity * price_pct
    units_1 = max(1, int(round(base_u * (1.0 + unit_pct_change / 100.0))))
    
    sales_1 = round(price_1 * units_1, 2)
    cost_1 = round(cost_1 * units_1, 2)
    profit_1 = round(sales_1 - cost_1, 2)
    margin_1 = (profit_1 / sales_1 * 100.0) if sales_1 > 0 else 0
    margin_0 = (base_p / base_s * 100.0) if base_s > 0 else 0
    
    return {
        'name': product_name,
        'base_profit': base_p,
        'new_profit': profit_1,
        'profit_diff': profit_1 - base_p,
        'profit_pct_gain': ((profit_1 - base_p) / base_p * 100.0) if base_p > 0 else 0,
        'base_margin': margin_0,
        'new_margin': margin_1,
        'margin_diff': margin_1 - margin_0,
        'base_units': base_u,
        'new_units': units_1,
        'base_sales': base_s,
        'new_sales': sales_1
    }
