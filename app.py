import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from data_loader import load_data
from analysis import (
    get_kpis,
    get_product_summary,
    get_division_summary,
    get_pareto,
    get_cost_diagnostics,
    simulate_price_impact
)

st.set_page_config(
    page_title="Nassau Candy | Product Profitability",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom styling - warm editorial look with DM Serif Display + Inter
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Base theme */
    .stApp {
        background-color: #f7f5f2;
        color: #1e293b;
        font-family: 'Inter', sans-serif;
    }
    
    /* Editorial Headings */
    h1, h2, h3, .serif-title {
        font-family: 'DM Serif Display', Georgia, serif;
        font-weight: 400;
        color: #0f172a;
        letter-spacing: -0.01em;
    }

    /* Hero Header Banner */
    .hero-box {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        padding-bottom: 16px;
        border-bottom: 2px solid #e2ded8;
        margin-bottom: 20px;
    }
    .hero-title {
        font-family: 'DM Serif Display', Georgia, serif;
        font-size: 34px;
        margin: 0;
        color: #0f172a;
        line-height: 1.1;
    }
    .hero-sub {
        font-size: 14px;
        color: #64748b;
        margin-top: 4px;
    }
    .hero-tag {
        font-size: 12px;
        background: #e6e2dc;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 600;
        color: #475569;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    /* Top Nav Styling */
    div[data-testid="stRadio"] > div {
        flex-direction: row;
        gap: 8px;
        background: #ede9e3;
        padding: 6px;
        border-radius: 10px;
        margin-bottom: 18px;
    }
    div[data-testid="stRadio"] label {
        background: transparent;
        padding: 6px 18px;
        border-radius: 8px;
        border: none;
        font-weight: 500;
        font-size: 14px;
        color: #475569;
        cursor: pointer;
        transition: all 0.15s ease;
    }
    div[data-testid="stRadio"] label:hover {
        color: #0f172a;
    }

    /* Custom KPI Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e5e0d8;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .metric-label {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748b;
        margin-bottom: 4px;
    }
    .metric-val {
        font-size: 26px;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    .metric-sub {
        font-size: 12px;
        color: #0f766e;
        font-weight: 500;
        margin-top: 4px;
    }
    .metric-sub.alert {
        color: #c2410c;
    }

    /* Commentary Callout Box */
    .note-box {
        background: #ffffff;
        border-left: 3px solid #0f766e;
        padding: 14px 16px;
        border-radius: 0 8px 8px 0;
        font-size: 13px;
        line-height: 1.5;
        color: #334155;
        margin-top: 12px;
        border-top: 1px solid #e5e0d8;
        border-right: 1px solid #e5e0d8;
        border-bottom: 1px solid #e5e0d8;
    }
    .note-box strong {
        color: #0f172a;
    }

    /* Chart captions */
    .chart-caption {
        font-size: 13px;
        color: #64748b;
        margin-bottom: 8px;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Custom color palette for Plotly charts
PALETTE = ["#0f766e", "#c2410c", "#b45309", "#334155", "#64748b", "#0284c7"]

# Load data
@st.cache_data
def get_data():
    return load_data()

raw_df = get_data()

# Header
st.markdown("""
<div class="hero-box">
    <div>
        <h1 class="hero-title">Product Line Profitability & Margins</h1>
        <div class="hero-sub">Nassau Candy Distributor • Unit Economics, Concentration Risk & Remedial Pricing</div>
    </div>
    <div class="hero-tag">FY2024–FY2025 Audit</div>
</div>
""", unsafe_allow_html=True)

# Top Bar Filters in an Expander (Keeps sidebar clean!)
with st.expander("Filter Transactions & Thresholds", expanded=False):
    f1, f2, f3, f4, f5 = st.columns([1.5, 1.2, 1.2, 1.5, 0.8])
    
    with f1:
        min_d = raw_df['Order Date'].min().date()
        max_d = raw_df['Order Date'].max().date()
        date_range = st.date_input("Date Range", [min_d, max_d], min_value=min_d, max_value=max_d)
        
    with f2:
        divisions = sorted(raw_df['Division'].unique())
        selected_divs = st.multiselect("Divisions", divisions, default=divisions)
        
    with f3:
        min_margin = st.slider("Min Margin %", 0, 90, 0, step=5)
        
    with f4:
        search_query = st.text_input("Search SKU Name", placeholder="e.g. Wonka, Kazookles...").strip().lower()
        
    with f5:
        st.write("")
        st.write("")
        reset = st.button("Reset", use_container_width=True)

if reset:
    selected_divs = divisions
    min_margin = 0
    search_query = ""
    date_range = [min_d, max_d]

# Apply filters
start_dt, end_dt = (date_range[0], date_range[1]) if len(date_range) == 2 else (min_d, max_d)

df = raw_df[
    (raw_df['Order Date'].dt.date >= start_dt) &
    (raw_df['Order Date'].dt.date <= end_dt) &
    (raw_df['Division'].isin(selected_divs if selected_divs else divisions)) &
    (raw_df['Gross Margin %'] >= min_margin)
]

if search_query:
    df = df[df['Product Name'].str.lower().str.contains(search_query)]

if df.empty:
    st.info("No orders found matching this filter criteria. Try adjusting the thresholds above.")
    st.stop()

# Compute core summaries
kpis = get_kpis(df)
prod_df = get_product_summary(df)
div_df = get_division_summary(df)

# Horizontal Navigation Bar
sections = [
    "Product Profitability",
    "Division Performance",
    "Cost vs Margin Diagnostics",
    "Profit Concentration (Pareto)",
    "Executive Briefing & Data"
]

nav = st.radio("Navigation", sections, horizontal=True, label_visibility="collapsed")

st.write("")

# -----------------------------------------------------------------------------
# 1. PRODUCT PROFITABILITY
# -----------------------------------------------------------------------------
if nav == "Product Profitability":
    col_main, col_side = st.columns([2.2, 1])
    
    with col_main:
        with st.container(border=True):
            st.markdown("### Product Margin & Turnover Matrix")
            st.markdown('<div class="chart-caption">Bubble size represents Gross Profit ($). Look for large bubbles near the top right—those drive the business.</div>', unsafe_allow_html=True)
            
            med_s = prod_df['Total_Sales'].median()
            med_m = prod_df['Gross_Margin_%'].median()
            
            fig = px.scatter(
                prod_df,
                x='Total_Sales',
                y='Gross_Margin_%',
                size='Total_Profit',
                color='Division',
                hover_name='Product Name',
                hover_data={
                    'Total_Sales': ':$,.2f',
                    'Gross_Margin_%': ':.1f%',
                    'Total_Profit': ':$,.2f',
                    'Cost_Ratio_%': ':.1f%',
                    'Profit_per_Unit': ':$,.2f'
                },
                size_max=38,
                color_discrete_sequence=PALETTE,
                labels={'Total_Sales': 'Gross Sales ($)', 'Gross_Margin_%': 'Gross Margin (%)'}
            )
            
            # Subtle quadrant guidelines
            fig.add_vline(x=med_s, line_dash="dash", line_color="#cbd5e1", line_width=1.5)
            fig.add_hline(y=med_m, line_dash="dash", line_color="#cbd5e1", line_width=1.5)
            fig.update_layout(
                template="plotly_white",
                height=380,
                margin=dict(l=10, r=10, t=20, b=20),
                xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
                yaxis=dict(showgrid=True, gridcolor="#f1f5f9", range=[0, 90])
            )
            st.plotly_chart(fig, use_container_width=True)

        with st.container(border=True):
            st.markdown("### Product Leaderboard")
            st.dataframe(
                prod_df[[
                    'Product Name', 'Division', 'Total_Sales', 'Total_Cost',
                    'Total_Profit', 'Gross_Margin_%', 'Profit_per_Unit',
                    'Profit_Share_%', 'Classification'
                ]],
                column_config={
                    'Product Name': st.column_config.TextColumn("Product Name", width="medium"),
                    'Division': st.column_config.TextColumn("Division"),
                    'Total_Sales': st.column_config.NumberColumn("Sales", format="$%.2f"),
                    'Total_Cost': st.column_config.NumberColumn("Cost", format="$%.2f"),
                    'Total_Profit': st.column_config.NumberColumn("Gross Profit", format="$%.2f"),
                    'Gross_Margin_%': st.column_config.ProgressColumn("Margin %", format="%.1f%%", min_value=0, max_value=100),
                    'Profit_per_Unit': st.column_config.NumberColumn("Profit/Unit", format="$%.2f"),
                    'Profit_Share_%': st.column_config.NumberColumn("Profit Share", format="%.1f%%"),
                    'Classification': st.column_config.TextColumn("Portfolio Tag", width="medium")
                },
                use_container_width=True,
                hide_index=True,
                height=320
            )

    with col_side:
        # Custom KPI cards
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Gross Revenue</div>
            <div class="metric-val">${kpis['sales']:,.2f}</div>
            <div class="metric-sub">{kpis['orders']:,} Total Orders</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Gross Profit</div>
            <div class="metric-val">${kpis['profit']:,.2f}</div>
            <div class="metric-sub">${kpis['ppu']:.2f} Avg Unit Margin</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Blended Gross Margin</div>
            <div class="metric-val">{kpis['margin']:.1f}%</div>
            <div class="metric-sub {'alert' if kpis['margin'] < 60 else ''}">
                {'Requires Reprice Attention' if kpis['margin'] < 60 else 'Healthy Core Baseline'}
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Total Units Distributed</div>
            <div class="metric-val">{kpis['units']:,}</div>
            <div class="metric-sub">${kpis['aov']:.2f} Avg Order Value</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="note-box">
            <strong>Analyst Takeaway:</strong> Wonka Bar chocolate varieties are the lifeblood of Nassau Candy, delivering over 95% of total enterprise profit with steady 65–71% gross margins. Watch out for items in the bottom right of the scatter—those sell volume but leak margin.
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DIVISION PERFORMANCE
# -----------------------------------------------------------------------------
elif nav == "Division Performance":
    c_left, c_right = st.columns([1.8, 1.2])
    
    with c_left:
        with st.container(border=True):
            st.markdown("### Revenue vs. Profit by Division")
            st.markdown('<div class="chart-caption">Chocolate represents nearly the entire revenue bar and profit bar. Other & Sugar are tiny by comparison.</div>', unsafe_allow_html=True)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Sales ($)',
                x=div_df['Division'],
                y=div_df['Total_Sales'],
                marker_color='#0f766e',
                text=div_df['Total_Sales'].apply(lambda x: f"${x:,.0f}"),
                textposition='outside'
            ))
            fig.add_trace(go.Bar(
                name='Gross Profit ($)',
                x=div_df['Division'],
                y=div_df['Total_Profit'],
                marker_color='#c2410c',
                text=div_df['Total_Profit'].apply(lambda x: f"${x:,.0f}"),
                textposition='outside'
            ))
            fig.update_layout(
                barmode='group',
                template='plotly_white',
                height=340,
                margin=dict(l=10, r=10, t=20, b=20),
                yaxis=dict(showgrid=True, gridcolor="#f1f5f9")
            )
            st.plotly_chart(fig, use_container_width=True)

        with st.container(border=True):
            st.markdown("### Transaction Margin Dispersion")
            st.markdown('<div class="chart-caption">Notice the wide spread in "Other" caused by Kazookles (7.7%) pulling down Lickable Wallpaper (50%).</div>', unsafe_allow_html=True)
            
            fig_box = px.box(
                df,
                x='Division',
                y='Gross Margin %',
                color='Division',
                color_discrete_sequence=PALETTE,
                points="outliers"
            )
            fig_box.update_layout(
                template='plotly_white',
                height=260,
                showlegend=False,
                margin=dict(l=10, r=10, t=10, b=20),
                yaxis=dict(showgrid=True, gridcolor="#f1f5f9")
            )
            st.plotly_chart(fig_box, use_container_width=True)

    with c_right:
        with st.container(border=True):
            st.markdown("### Division Summary Table")
            st.dataframe(
                div_df[['Division', 'Total_Sales', 'Total_Profit', 'Gross_Margin_%', 'Revenue_Share_%', 'Profit_Share_%']],
                column_config={
                    'Division': st.column_config.TextColumn("Division"),
                    'Total_Sales': st.column_config.NumberColumn("Sales", format="$%.2f"),
                    'Total_Profit': st.column_config.NumberColumn("Profit", format="$%.2f"),
                    'Gross_Margin_%': st.column_config.ProgressColumn("Margin", format="%.1f%%", min_value=0, max_value=100),
                    'Revenue_Share_%': st.column_config.NumberColumn("Rev %", format="%.1f%%"),
                    'Profit_Share_%': st.column_config.NumberColumn("Profit %", format="%.1f%%")
                },
                use_container_width=True,
                hide_index=True
            )
            
        st.markdown("""
        <div class="note-box">
            <strong>Key Division Findings:</strong><br>
            • <strong>Chocolate:</strong> 92.9% of sales, 95.1% of profit. Rock solid.<br>
            • <strong>Other:</strong> $9.6k sales with 44.8% blended margin; dragged down by high supplier costs.<br>
            • <strong>Sugar:</strong> 66.6% margin, but only $427 in total sales across 2 years. Untapped potential.
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. COST VS MARGIN DIAGNOSTICS
# -----------------------------------------------------------------------------
elif nav == "Cost vs Margin Diagnostics":
    c_diag, c_sim = st.columns([1.6, 1.4])
    
    with c_diag:
        with st.container(border=True):
            st.markdown("### Cost of Goods vs. Revenue")
            st.markdown('<div class="chart-caption">Dots above the red dashed line incur supplier costs >70% of retail price.</div>', unsafe_allow_html=True)
            
            fig_c = px.scatter(
                prod_df,
                x='Total_Sales',
                y='Total_Cost',
                size='Total_Units',
                color='Gross_Margin_%',
                color_continuous_scale='Tealgrn',
                hover_name='Product Name',
                hover_data={'Total_Sales': ':$,.2f', 'Total_Cost': ':$,.2f', 'Cost_Ratio_%': ':.1f%'},
                labels={'Total_Sales': 'Sales ($)', 'Total_Cost': 'Cost ($)'}
            )
            
            max_val = prod_df['Total_Sales'].max()
            fig_c.add_trace(go.Scatter(
                x=[0, max_val],
                y=[0, max_val * 0.70],
                mode="lines",
                name="70% Cost Alert Line",
                line=dict(color="#c2410c", dash="dash", width=2)
            ))
            fig_c.update_layout(
                template='plotly_white',
                height=340,
                margin=dict(l=10, r=10, t=10, b=20),
                yaxis=dict(showgrid=True, gridcolor="#f1f5f9")
            )
            st.plotly_chart(fig_c, use_container_width=True)

        diag_table = get_cost_diagnostics(df)
        with st.container(border=True):
            st.markdown("### Actionable SKU Diagnostic Register")
            st.dataframe(
                diag_table[['Product Name', 'Division', 'Total_Sales', 'Cost_Ratio_%', 'Gross_Margin_%', 'Urgency', 'Action_Plan']],
                column_config={
                    'Product Name': st.column_config.TextColumn("Product Name", width="medium"),
                    'Division': st.column_config.TextColumn("Division"),
                    'Total_Sales': st.column_config.NumberColumn("Sales", format="$%.2f"),
                    'Cost_Ratio_%': st.column_config.NumberColumn("Cost %", format="%.1f%%"),
                    'Gross_Margin_%': st.column_config.ProgressColumn("Margin %", format="%.1f%%", min_value=0, max_value=100),
                    'Urgency': st.column_config.TextColumn("Priority"),
                    'Action_Plan': st.column_config.TextColumn("Prescribed Remedial Action", width="large")
                },
                use_container_width=True,
                hide_index=True,
                height=260
            )

    with c_sim:
        with st.container(border=True):
            st.markdown("### What-If Repricing & Cost Simulator")
            st.markdown('<div class="chart-caption">Simulate price elasticity and supplier cost cuts to see the exact bottom-line profit recovery.</div>', unsafe_allow_html=True)
            
            target_sku = st.selectbox(
                "Select Product to Model",
                prod_df['Product Name'].tolist(),
                index=prod_df[prod_df['Product Name'] == 'Kazookles'].index[0] if 'Kazookles' in prod_df['Product Name'].values else 0
            )
            
            p_adj = st.slider("Selling Price Adjustment (%)", -10.0, 30.0, 10.0, step=1.0)
            c_adj = st.slider("Supplier Cost Reduction (%)", 0.0, 20.0, 5.0, step=1.0)
            elast = st.slider("Price Elasticity of Demand", -1.0, 0.0, -0.3, step=0.05, help="Standard confectionery elasticity is around -0.3 (inelastic).")
            
            sim = simulate_price_impact(df, target_sku, price_pct=p_adj, cost_pct=c_adj, elasticity=elast)
            
            if sim:
                sc1, sc2 = st.columns(2)
                with sc1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">New Gross Profit</div>
                        <div class="metric-val">${sim['new_profit']:,.2f}</div>
                        <div class="metric-sub">{sim['profit_diff']:+,.2f} ({sim['profit_pct_gain']:+.1f}%)</div>
                    </div>
                    """, unsafe_allow_html=True)
                with sc2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">New Gross Margin</div>
                        <div class="metric-val">{sim['new_margin']:.1f}%</div>
                        <div class="metric-sub">{sim['margin_diff']:+.1f}% pts delta</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                fig_sim = go.Figure()
                fig_sim.add_trace(go.Bar(
                    name='Current Baseline',
                    x=['Revenue', 'COGS Cost', 'Gross Profit'],
                    y=[sim['base_sales'], sim['base_sales'] - sim['base_profit'], sim['base_profit']],
                    marker_color='#94a3b8'
                ))
                fig_sim.add_trace(go.Bar(
                    name='Simulated Outcome',
                    x=['Revenue', 'COGS Cost', 'Gross Profit'],
                    y=[sim['new_sales'], sim['new_sales'] - sim['new_profit'], sim['new_profit']],
                    marker_color='#0f766e'
                ))
                fig_sim.update_layout(
                    barmode='group',
                    template='plotly_white',
                    height=240,
                    margin=dict(l=10, r=10, t=10, b=20),
                    yaxis=dict(showgrid=True, gridcolor="#f1f5f9")
                )
                st.plotly_chart(fig_sim, use_container_width=True)

# -----------------------------------------------------------------------------
# 4. PROFIT CONCENTRATION (PARETO)
# -----------------------------------------------------------------------------
elif nav == "Profit Concentration (Pareto)":
    pareto_df, p_meta = get_pareto(df, col='Gross Profit')
    sales_p_df, s_meta = get_pareto(df, col='Sales')
    
    col_p1, col_p2 = st.columns([1.8, 1.2])
    
    with col_p1:
        with st.container(border=True):
            st.markdown("### Gross Profit Pareto Curve (80/20 Rule)")
            st.markdown('<div class="chart-caption">The orange line shows cumulative profit. Notice how quickly it hits the 80% dashed red line.</div>', unsafe_allow_html=True)
            
            fig_p = go.Figure()
            fig_p.add_trace(go.Bar(
                name='Gross Profit ($)',
                x=pareto_df['Product Name'],
                y=pareto_df['Gross Profit'],
                marker_color='#0f766e',
                yaxis='y1'
            ))
            fig_p.add_trace(go.Scatter(
                name='Cumulative %',
                x=pareto_df['Product Name'],
                y=pareto_df['Cumulative_%'],
                marker=dict(color='#c2410c', size=7),
                line=dict(color='#c2410c', width=2.5),
                yaxis='y2'
            ))
            fig_p.add_hline(y=80, line_dash="dash", line_color="#ef4444", yref="y2")
            
            fig_p.update_layout(
                template='plotly_white',
                height=380,
                margin=dict(l=10, r=10, t=20, b=80),
                yaxis=dict(title="Gross Profit ($)", showgrid=True, gridcolor="#f1f5f9"),
                yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 105], showgrid=False),
                xaxis=dict(tickangle=-45),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_p, use_container_width=True)

    with col_p2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">SKUs Generating 80% of Profit</div>
            <div class="metric-val">{p_meta['skus_for_80']} of {len(pareto_df)} SKUs</div>
            <div class="metric-sub alert">{p_meta['pct_catalog_for_80']:.1f}% of catalog drives 80% margin</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Top SKU Profit Contribution</div>
            <div class="metric-val">{p_meta['top_sku_share']:.1f}%</div>
            <div class="metric-sub">{p_meta['top_sku'][:22]}...</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Profit Concentration Index (HHI)</div>
            <div class="metric-val">{p_meta['hhi']:,.0f}</div>
            <div class="metric-sub">Moderate Concentration Risk</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="note-box">
            <strong>Concentration Assessment:</strong> Nassau Candy operates with a classic 80/20 skew. Exactly 5 Wonka chocolate products carry the entire financial weight of the business. A disruption at the primary chocolate lines would immediately compromise cash flows.
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. EXECUTIVE BRIEFING & EXPORT
# -----------------------------------------------------------------------------
else:
    c_sum1, c_sum2 = st.columns([1.6, 1.4])
    
    with c_sum1:
        with st.container(border=True):
            st.markdown("### Executive Summary & Action Plan")
            st.markdown("""
            **1. Protect & Reprice the Core Chocolate Engines**
            - The 5 Wonka Bars account for **95.1% of total gross profit** ($88.8k of $93.4k).
            - Apply a selective **+3.5% price increase** on the top 3 volume drivers to capture ~+$2,850 in bottom-line margin without volume erosion.

            **2. Eliminate the Kazookles Supplier Deficit**
            - Kazookles generates $1,205 in sales but incurs $1,113 in supplier cost (only 7.69% gross margin).
            - Demand a 20% supplier cost reduction or reprice wholesale from $3.25 to $3.75.

            **3. Commercialize High-Margin Sugar Gems**
            - *Everlasting Gobstopper* (80.0% margin) and *Hair Toffee* (77.8% margin) deliver huge margin but low volume.
            - Bundle them with chocolate wholesale cartons to scale distribution.

            **4. Prune Negative-ROI Tail SKUs**
            - Discontinue *Fun Dip* and *Nerds* if minimum batch order sizes are not met to free up warehouse slotting.
            """)

    with c_sum2:
        with st.container(border=True):
            st.markdown("### Export Cleaned Data")
            st.markdown('<div class="chart-caption">Download timestamped CSVs for financial reporting and external spreadsheets.</div>', unsafe_allow_html=True)
            
            ts = datetime.now().strftime("%Y%m%d")
            
            st.download_button(
                "📥 Export Filtered Orders CSV",
                df.to_csv(index=False).encode('utf-8'),
                f"nassau_candy_filtered_{ts}.csv",
                "text/csv",
                use_container_width=True
            )
            
            st.download_button(
                "📥 Export Product Performance Summary",
                prod_df.to_csv(index=False).encode('utf-8'),
                f"nassau_product_performance_{ts}.csv",
                "text/csv",
                use_container_width=True
            )
            
            st.download_button(
                "📥 Export SKU Diagnostic Register",
                get_cost_diagnostics(df).to_csv(index=False).encode('utf-8'),
                f"nassau_sku_diagnostics_{ts}.csv",
                "text/csv",
                use_container_width=True
            )
