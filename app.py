"""
app.py
------
Nassau Candy Distributor - Product Line Profitability & Margin Performance Dashboard
An enterprise-grade, production-ready Streamlit analytics application.
"""

import streamlit as pd_st  # alias to avoid naming confusion
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Local module imports
from data_loader import load_and_clean_data, get_factory_summary, FACTORY_COORDINATES
from analysis import (
    calculate_executive_kpis,
    get_product_profitability_metrics,
    get_division_metrics,
    get_pareto_analysis,
    get_cost_structure_diagnostics,
    simulate_repricing_impact,
    get_monthly_profitability_trend,
    get_regional_profitability
)

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & METADATA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Nassau Candy | Profitability & Margin Intelligence",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# DESIGN SYSTEM & CUSTOM CSS
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header Gradient & Badge */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f766e 100%);
        padding: 24px 32px;
        border-radius: 16px;
        color: #ffffff;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .main-header h1 {
        font-size: 28px;
        font-weight: 800;
        margin: 0 0 6px 0;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    .main-header p {
        font-size: 14px;
        color: #94a3b8;
        margin: 0;
    }
    .badge-pill {
        display: inline-block;
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        font-size: 12px;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 9999px;
        border: 1px solid rgba(52, 211, 153, 0.3);
        margin-bottom: 8px;
    }

    /* Metric Cards */
    .kpi-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    .kpi-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .kpi-subtext {
        font-size: 12px;
        font-weight: 500;
    }
    .kpi-subtext.positive { color: #10b981; }
    .kpi-subtext.neutral { color: #64748b; }
    .kpi-subtext.warning { color: #f59e0b; }
    .kpi-subtext.danger { color: #ef4444; }

    /* Action Banner */
    .action-banner {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 14px 18px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 20px;
        font-size: 13px;
        color: #334155;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 18px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
    }

    /* Hide Streamlit default branding for clean look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# DATA CACHING
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner="Ingesting and standardizing Nassau Candy data...")
def get_cached_dataset():
    """Load cleaned data with Streamlit caching."""
    return load_and_clean_data()


# -----------------------------------------------------------------------------
# DATA INGESTION & AUDIT
# -----------------------------------------------------------------------------
raw_cleaned_df, audit_stats = get_cached_dataset()

# -----------------------------------------------------------------------------
# SIDEBAR FILTERS & CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1582293041079-7814c2f12063?w=500&auto=format&fit=crop&q=60", use_container_width=True)
    st.markdown("### 🎛️ Analytics Controls")
    st.caption("Filter and segment financial data across dimensions.")

    # Date Range Filter
    min_date = raw_cleaned_df["Order Date"].min().date()
    max_date = raw_cleaned_df["Order Date"].max().date()
    
    date_preset = st.radio(
        "Date Preset",
        ["Full Timeframe (2024-2025)", "Year 2024", "Year 2025", "Custom Range"],
        index=0,
        horizontal=False
    )
    
    if date_preset == "Year 2024":
        start_date, end_date = pd.to_datetime("2024-01-01").date(), pd.to_datetime("2024-12-31").date()
    elif date_preset == "Year 2025":
        start_date, end_date = pd.to_datetime("2025-01-01").date(), pd.to_datetime("2025-12-31").date()
    elif date_preset == "Custom Range":
        selected_dates = st.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
        if len(selected_dates) == 2:
            start_date, end_date = selected_dates
        else:
            start_date, end_date = min_date, max_date
    else:
        start_date, end_date = min_date, max_date

    st.divider()

    # Division Filter
    all_divisions = sorted(raw_cleaned_df["Division"].unique().tolist())
    selected_divisions = st.multiselect("Division Selection", all_divisions, default=all_divisions)

    # Factory Filter
    all_factories = sorted(raw_cleaned_df["Factory"].unique().tolist())
    selected_factories = st.multiselect("Manufacturing Plant", all_factories, default=all_factories)

    # Margin Threshold Filter
    margin_threshold = st.slider("Min Product Gross Margin %", min_value=0.0, max_value=100.0, value=0.0, step=5.0)

    # Product Search
    search_query = st.text_input("🔍 Search Product Name", "").strip().lower()

    st.divider()
    st.caption("Nassau Candy Analytics v2.4 | Production Grade")

# -----------------------------------------------------------------------------
# APPLY GLOBAL FILTERING
# -----------------------------------------------------------------------------
filtered_df = raw_cleaned_df[
    (raw_cleaned_df["Order Date"].dt.date >= start_date) &
    (raw_cleaned_df["Order Date"].dt.date <= end_date) &
    (raw_cleaned_df["Division"].isin(selected_divisions if selected_divisions else all_divisions)) &
    (raw_cleaned_df["Factory"].isin(selected_factories if selected_factories else all_factories)) &
    (raw_cleaned_df["Gross Margin %"] >= margin_threshold)
]

if search_query:
    filtered_df = filtered_df[filtered_df["Product Name"].str.lower().str.contains(search_query)]

# Empty check fallback
if filtered_df.empty:
    st.warning("⚠️ No records match the current filter selection. Please broaden your sidebar filters.")
    st.stop()

# -----------------------------------------------------------------------------
# HEADER & EXECUTIVE BANNER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <div class="badge-pill">NASSAU CANDY DISTRIBUTOR • C-SUITE FINANCIAL INTELLIGENCE</div>
    <h1>Product Line Profitability & Margin Performance</h1>
    <p>Comprehensive unit-economic diagnostics, profit concentration (Pareto), division contribution, and margin optimization roadmap.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# EXECUTIVE KPI RIBBON
# -----------------------------------------------------------------------------
kpi_data = calculate_executive_kpis(filtered_df)
product_metrics_df = get_product_profitability_metrics(filtered_df)
cost_diag_df, cost_diag_summary = get_cost_structure_diagnostics(filtered_df)

top_product_name = product_metrics_df.iloc[0]["Product Name"] if not product_metrics_df.empty else "N/A"
top_product_profit = product_metrics_df.iloc[0]["Total_Profit"] if not product_metrics_df.empty else 0

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Gross Revenue</div>
        <div class="kpi-value">${kpi_data['total_revenue']:,.2f}</div>
        <div class="kpi-subtext neutral">{kpi_data['total_orders']:,} Total Orders</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Gross Profit</div>
        <div class="kpi-value">${kpi_data['total_profit']:,.2f}</div>
        <div class="kpi-subtext positive">Margin: ${kpi_data['profit_per_unit']:.2f} / unit</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Blended Margin</div>
        <div class="kpi-value">{kpi_data['overall_margin']:.1f}%</div>
        <div class="kpi-subtext {'positive' if kpi_data['overall_margin'] >= 60 else 'warning'}">
            {'Strong Margin' if kpi_data['overall_margin'] >= 60 else 'Requires Repricing'}
        </div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Units Sold</div>
        <div class="kpi-value">{kpi_data['total_units']:,}</div>
        <div class="kpi-subtext neutral">Avg Price: ${kpi_data['total_revenue']/max(1, kpi_data['total_units']):.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Top Profit SKU</div>
        <div class="kpi-value" style="font-size: 16px; font-weight: 700; height: 32px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{top_product_name}">{top_product_name}</div>
        <div class="kpi-subtext positive">${top_product_profit:,.2f} Profit</div>
    </div>
    """, unsafe_allow_html=True)

with c6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Action SKU Flags</div>
        <div class="kpi-value" style="color: #ef4444;">{cost_diag_summary['renegotiate_count'] + cost_diag_summary['reprice_count'] + cost_diag_summary['discontinue_count']}</div>
        <div class="kpi-subtext danger">{cost_diag_summary['renegotiate_count']} Critical Vendor Review</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# -----------------------------------------------------------------------------
# TABS ARCHITECTURE
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Product Profitability",
    "🏭 Division & Factory",
    "⚠️ Cost & Margin Diagnostics",
    "📈 Profit Concentration (Pareto)",
    "🎯 Growth Matrix & Volatility",
    "📄 Executive Briefing & Export"
])


# =============================================================================
# TAB 1: PRODUCT PROFITABILITY OVERVIEW
# =============================================================================
with tab1:
    st.markdown("### 🏆 Product Margin & Profitability Leaderboard")
    st.caption("Detailed ranking of product performance, margin percentages, unit economics, and volatility.")

    # Leaderboard Table
    display_prod_df = product_metrics_df[[
        "Product Name", "Division", "Factory", "Total_Sales", "Total_Cost",
        "Total_Profit", "Gross_Margin_%", "Cost_Ratio_%", "Profit_Per_Unit",
        "Revenue_Share_%", "Profit_Share_%", "Margin_Volatility_Pct", "Strategic_Category"
    ]].copy()

    # Format styling with Streamlit native column_config (robust & high performance)
    st.dataframe(
        display_prod_df,
        column_config={
            "Product Name": st.column_config.TextColumn("Product Name", width="medium"),
            "Division": st.column_config.TextColumn("Division"),
            "Factory": st.column_config.TextColumn("Manufacturing Plant"),
            "Total_Sales": st.column_config.NumberColumn("Total Sales", format="$%.2f"),
            "Total_Cost": st.column_config.NumberColumn("Total Cost", format="$%.2f"),
            "Total_Profit": st.column_config.NumberColumn("Gross Profit", format="$%.2f"),
            "Gross_Margin_%": st.column_config.ProgressColumn(
                "Gross Margin %",
                format="%.1f%%",
                min_value=0,
                max_value=100
            ),
            "Cost_Ratio_%": st.column_config.NumberColumn("Cost Ratio %", format="%.1f%%"),
            "Profit_Per_Unit": st.column_config.NumberColumn("Profit / Unit", format="$%.2f"),
            "Revenue_Share_%": st.column_config.NumberColumn("Revenue Share %", format="%.2f%%"),
            "Profit_Share_%": st.column_config.NumberColumn("Profit Share %", format="%.2f%%"),
            "Margin_Volatility_Pct": st.column_config.NumberColumn("Margin Volatility %", format="%.2f%%"),
            "Strategic_Category": st.column_config.TextColumn("Strategic Category", width="medium")
        },
        use_container_width=True,
        hide_index=True,
        height=380
    )

    st.divider()

    # Visual Comparisons: Top by Profit vs Top by Margin
    col_chart_left, col_chart_right = st.columns(2)

    with col_chart_left:
        st.markdown("#### Top Products by Gross Profit ($)")
        top_profit_chart_df = product_metrics_df.sort_values(by="Total_Profit", ascending=True).tail(10)
        
        fig_profit = px.bar(
            top_profit_chart_df,
            x="Total_Profit",
            y="Product Name",
            orientation="h",
            color="Gross_Margin_%",
            color_continuous_scale="Viridis",
            labels={"Total_Profit": "Gross Profit ($)", "Product Name": "Product", "Gross_Margin_%": "Margin %"},
            text="Total_Profit"
        )
        fig_profit.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_profit.update_layout(
            margin=dict(l=10, r=40, t=20, b=20),
            height=380,
            xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
            yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig_profit, use_container_width=True)

    with col_chart_right:
        st.markdown("#### Top Products by Gross Margin (%)")
        top_margin_chart_df = product_metrics_df.sort_values(by="Gross_Margin_%", ascending=True).tail(10)
        
        fig_margin = px.bar(
            top_margin_chart_df,
            x="Gross_Margin_%",
            y="Product Name",
            orientation="h",
            color="Division",
            color_discrete_map={"Chocolate": "#3b82f6", "Other": "#8b5cf6", "Sugar": "#ec4899"},
            labels={"Gross_Margin_%": "Gross Margin (%)", "Product Name": "Product"},
            text="Gross_Margin_%"
        )
        fig_margin.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_margin.update_layout(
            margin=dict(l=10, r=40, t=20, b=20),
            height=380,
            xaxis=dict(showgrid=True, gridcolor="#f1f5f9", range=[0, 100]),
            yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig_margin, use_container_width=True)

    # Scatter: Sales vs Gross Margin with Quadrants
    st.markdown("#### 🔍 Sales vs. Gross Margin Multi-Dimensional Bubble Matrix")
    st.caption("Bubble size corresponds to Gross Profit ($). Hover over points to examine unit economics.")

    median_sales = product_metrics_df["Total_Sales"].median()
    median_margin = product_metrics_df["Gross_Margin_%"].median()

    fig_bubble = px.scatter(
        product_metrics_df,
        x="Total_Sales",
        y="Gross_Margin_%",
        size="Total_Profit",
        color="Division",
        hover_name="Product Name",
        hover_data={
            "Total_Sales": ":$,.2f",
            "Gross_Margin_%": ":.2f%",
            "Total_Profit": ":$,.2f",
            "Total_Cost": ":$,.2f",
            "Profit_Per_Unit": ":$,.2f",
            "Strategic_Category": True
        },
        size_max=45,
        color_discrete_map={"Chocolate": "#1e3a8a", "Other": "#7c3aed", "Sugar": "#db2777"},
        labels={"Total_Sales": "Total Gross Sales ($)", "Gross_Margin_%": "Gross Margin (%)"}
    )
    
    # Add median quadrant benchmark lines
    fig_bubble.add_vline(x=median_sales, line_width=1.5, line_dash="dash", line_color="#94a3b8", annotation_text="Median Sales", annotation_position="top right")
    fig_bubble.add_hline(y=median_margin, line_width=1.5, line_dash="dash", line_color="#94a3b8", annotation_text="Median Margin", annotation_position="top right")

    fig_bubble.update_layout(
        height=480,
        margin=dict(l=20, r=20, t=30, b=30),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", range=[0, 95])
    )
    st.plotly_chart(fig_bubble, use_container_width=True)


# =============================================================================
# TAB 2: DIVISION & FACTORY PERFORMANCE
# =============================================================================
with tab2:
    st.markdown("### 🏢 Division Performance & Distribution Analysis")
    div_df = get_division_metrics(filtered_df)

    d_col1, d_col2 = st.columns([1, 1])

    with d_col1:
        st.markdown("#### Division Revenue vs Gross Profit Comparison")
        fig_div_bar = go.Figure()
        fig_div_bar.add_trace(go.Bar(
            name="Gross Revenue",
            x=div_df["Division"],
            y=div_df["Total_Sales"],
            marker_color="#3b82f6",
            text=div_df["Total_Sales"].apply(lambda v: f"${v:,.0f}"),
            textposition="outside"
        ))
        fig_div_bar.add_trace(go.Bar(
            name="Gross Profit",
            x=div_df["Division"],
            y=div_df["Total_Profit"],
            marker_color="#10b981",
            text=div_df["Total_Profit"].apply(lambda v: f"${v:,.0f}"),
            textposition="outside"
        ))
        fig_div_bar.update_layout(
            barmode="group",
            height=360,
            margin=dict(l=10, r=10, t=30, b=20),
            yaxis=dict(title="USD ($)", showgrid=True, gridcolor="#f1f5f9")
        )
        st.plotly_chart(fig_div_bar, use_container_width=True)

    with d_col2:
        st.markdown("#### Margin Distribution by Division (Boxplot)")
        fig_box = px.box(
            filtered_df,
            x="Division",
            y="Gross Margin %",
            color="Division",
            points="all",
            color_discrete_map={"Chocolate": "#3b82f6", "Other": "#8b5cf6", "Sugar": "#ec4899"},
            labels={"Gross Margin %": "Transaction Margin (%)"}
        )
        fig_box.update_layout(
            height=360,
            margin=dict(l=10, r=10, t=30, b=20),
            showlegend=False,
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9")
        )
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("#### Division Financial Summary Table")
    st.dataframe(
        div_df,
        column_config={
            "Division": st.column_config.TextColumn("Division"),
            "Total_Sales": st.column_config.NumberColumn("Total Sales", format="$%.2f"),
            "Total_Cost": st.column_config.NumberColumn("Total Cost", format="$%.2f"),
            "Total_Profit": st.column_config.NumberColumn("Gross Profit", format="$%.2f"),
            "Total_Units": st.column_config.NumberColumn("Units Shipped", format="%d"),
            "Order_Count": st.column_config.NumberColumn("Orders", format="%d"),
            "Product_Count": st.column_config.NumberColumn("SKU Count", format="%d"),
            "Gross_Margin_%": st.column_config.ProgressColumn("Gross Margin %", format="%.2f%%", min_value=0, max_value=100),
            "Cost_Ratio_%": st.column_config.NumberColumn("Cost Ratio %", format="%.2f%%"),
            "Profit_Per_Unit": st.column_config.NumberColumn("Profit / Unit", format="$%.2f"),
            "Revenue_Share_%": st.column_config.NumberColumn("Revenue Share %", format="%.2f%%"),
            "Profit_Share_%": st.column_config.NumberColumn("Profit Share %", format="%.2f%%")
        },
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # Factory Performance Section
    st.markdown("### 🏭 Manufacturing Plant & Capacity Intelligence")
    st.caption("Aggregated throughput, margin efficiency, and capacity utilization across 5 manufacturing facilities.")
    
    factory_summary_df = get_factory_summary(filtered_df)

    f_col1, f_col2 = st.columns([1.2, 1])

    with f_col1:
        st.markdown("#### Manufacturing Facility Profit Output ($)")
        fig_factory = px.bar(
            factory_summary_df,
            x="Total_Profit",
            y="Factory",
            orientation="h",
            color="Gross_Margin_%",
            color_continuous_scale="Teal",
            text="Total_Profit",
            labels={"Total_Profit": "Gross Profit ($)", "Factory": "Facility"}
        )
        fig_factory.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_factory.update_layout(
            height=320,
            margin=dict(l=10, r=40, t=20, b=20),
            yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig_factory, use_container_width=True)

    with f_col2:
        st.markdown("#### Factory Geographic Footprint")
        fig_geo = px.scatter_geo(
            factory_summary_df,
            lat="Lat",
            lon="Lon",
            hover_name="Factory",
            size="Total_Profit",
            color="Gross_Margin_%",
            color_continuous_scale="Purples",
            scope="usa",
            hover_data={
                "City": True,
                "State": True,
                "Total_Sales": ":$,.2f",
                "Total_Profit": ":$,.2f",
                "Gross_Margin_%": ":.1f%"
            }
        )
        fig_geo.update_layout(
            height=320,
            margin=dict(l=0, r=0, t=10, b=0),
            geo=dict(lakecolor='rgb(255, 255, 255)', landcolor='#f8fafc', subunitcolor='#cbd5e1')
        )
        st.plotly_chart(fig_geo, use_container_width=True)


# =============================================================================
# TAB 3: COST STRUCTURE & MARGIN DIAGNOSTICS
# =============================================================================
with tab3:
    st.markdown("### 🚨 Cost Structure Diagnostics & Remedial Action Engine")
    st.caption("Identify cost-heavy SKUs, supplier price spikes, and actionable repricing / discontinuation flags.")

    # Cost vs Sales Diagnostic Scatter
    fig_cost_scatter = px.scatter(
        product_metrics_df,
        x="Total_Sales",
        y="Total_Cost",
        size="Total_Units",
        color="Gross_Margin_%",
        color_continuous_scale="RdYlGn",
        hover_name="Product Name",
        hover_data={
            "Total_Sales": ":$,.2f",
            "Total_Cost": ":$,.2f",
            "Cost_Ratio_%": ":.1f%",
            "Gross_Margin_%": ":.1f%",
            "Strategic_Category": True
        },
        labels={"Total_Sales": "Gross Sales ($)", "Total_Cost": "Cost of Goods Sold ($)"}
    )
    
    # 70% Cost Warning Boundary
    max_s = product_metrics_df["Total_Sales"].max()
    fig_cost_scatter.add_trace(go.Scatter(
        x=[0, max_s],
        y=[0, max_s * 0.70],
        mode="lines",
        name="70% Cost Limit (Renegotiation Boundary)",
        line=dict(color="#ef4444", dash="dash", width=2)
    ))
    
    fig_cost_scatter.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9")
    )
    st.plotly_chart(fig_cost_scatter, use_container_width=True)

    # Action Trigger Flag Table
    st.markdown("#### 📋 Automated Remedial Action Register")
    action_table = cost_diag_df[[
        "Product Name", "Division", "Total_Sales", "Total_Cost", "Cost_Ratio_%",
        "Gross_Margin_%", "Profit_Per_Unit", "Action_Severity", "Recommended_Action"
    ]].copy()

    st.dataframe(
        action_table,
        column_config={
            "Product Name": st.column_config.TextColumn("Product Name", width="medium"),
            "Division": st.column_config.TextColumn("Division"),
            "Total_Sales": st.column_config.NumberColumn("Total Sales", format="$%.2f"),
            "Total_Cost": st.column_config.NumberColumn("Total Cost", format="$%.2f"),
            "Cost_Ratio_%": st.column_config.NumberColumn("Cost Ratio %", format="%.1f%%"),
            "Gross_Margin_%": st.column_config.ProgressColumn("Gross Margin %", format="%.1f%%", min_value=0, max_value=100),
            "Profit_Per_Unit": st.column_config.NumberColumn("Profit / Unit", format="$%.2f"),
            "Action_Severity": st.column_config.TextColumn("Severity"),
            "Recommended_Action": st.column_config.TextColumn("Strategic Diagnostic & Trigger", width="large")
        },
        use_container_width=True,
        hide_index=True,
        height=320
    )

    st.divider()

    # Interactive What-If Repricing & Margin Simulator
    st.markdown("### 🧪 What-If Repricing & Profit Recovery Simulator")
    st.caption("Model the financial impact of price elasticity and supplier cost negotiations for margin recovery.")

    sim_col1, sim_col2 = st.columns([1, 1.2])

    with sim_col1:
        target_product = st.selectbox(
            "Select SKU to Simulate",
            product_metrics_df["Product Name"].tolist(),
            index=product_metrics_df[product_metrics_df["Product Name"] == "Kazookles"].index[0] if "Kazookles" in product_metrics_df["Product Name"].values else 0
        )
        
        sim_price_pct = st.slider("Selling Price Adjustment (%)", min_value=-10.0, max_value=40.0, value=10.0, step=1.0)
        sim_cost_pct = st.slider("Supplier Cost Reduction (%)", min_value=0.0, max_value=25.0, value=5.0, step=1.0)
        sim_elasticity = st.slider("Demand Price Elasticity (Ed)", min_value=-1.5, max_value=0.0, value=-0.3, step=0.1, help="Confectionery demand is generally inelastic (-0.2 to -0.5).")

    with sim_col2:
        sim_res = simulate_repricing_impact(
            filtered_df,
            product_name=target_product,
            price_pct_change=sim_price_pct,
            cost_reduction_pct=sim_cost_pct,
            demand_elasticity=sim_elasticity
        )

        if sim_res:
            s_c1, s_c2 = st.columns(2)
            with s_c1:
                st.metric("New Gross Margin", f"{sim_res['new_margin']:.1f}%", f"{sim_res['margin_delta_pts']:+.1f}% pts")
                st.metric("New Gross Profit", f"${sim_res['new_profit']:,.2f}", f"${sim_res['profit_delta']:+,.2f} ({sim_res['profit_pct_delta']:+.1f}%)")
            with s_c2:
                st.metric("New Units Demand", f"{sim_res['new_units']:,}", f"{sim_res['new_units'] - sim_res['base_units']:+,} units")
                st.metric("New Gross Revenue", f"${sim_res['new_sales']:,.2f}", f"${sim_res['new_sales'] - sim_res['base_sales']:+,.2f}")

            # Waterfall / Before & After Bar
            fig_sim = go.Figure()
            fig_sim.add_trace(go.Bar(
                name="Baseline",
                x=["Revenue", "COGS (Cost)", "Gross Profit"],
                y=[sim_res["base_sales"], sim_res["base_cost"], sim_res["base_profit"]],
                marker_color="#94a3b8"
            ))
            fig_sim.add_trace(go.Bar(
                name="Simulated Outcome",
                x=["Revenue", "COGS (Cost)", "Gross Profit"],
                y=[sim_res["new_sales"], sim_res["new_cost"], sim_res["new_profit"]],
                marker_color="#10b981"
            ))
            fig_sim.update_layout(
                barmode="group",
                height=240,
                margin=dict(l=10, r=10, t=20, b=20),
                yaxis=dict(title="USD ($)", showgrid=True, gridcolor="#f1f5f9")
            )
            st.plotly_chart(fig_sim, use_container_width=True)


# =============================================================================
# TAB 4: PROFIT CONCENTRATION (PARETO 80/20)
# =============================================================================
with tab4:
    st.markdown("### 📈 Profit & Revenue Concentration Analysis (80/20 Pareto)")
    st.caption("Quantify catalog concentration risk, revenue vs profit skew, and portfolio dependency.")

    pareto_profit_df, pareto_profit_stats = get_pareto_analysis(filtered_df, metric="Gross Profit")
    pareto_sales_df, pareto_sales_stats = get_pareto_analysis(filtered_df, metric="Sales")

    # Pareto Risk Metrics
    par_c1, par_c2, par_c3, par_c4 = st.columns(4)

    with par_c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">80% Profit Driver SKUs</div>
            <div class="kpi-value">{pareto_profit_stats.get('products_for_80_pct', 0)} of {pareto_profit_stats.get('total_products', 0)}</div>
            <div class="kpi-subtext danger">{pareto_profit_stats.get('pct_of_catalog_for_80_pct', 0):.1f}% of SKU catalog</div>
        </div>
        """, unsafe_allow_html=True)

    with par_c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Top 20% SKUs Profit Share</div>
            <div class="kpi-value">{pareto_profit_stats.get('top_20_pct_products_share', 0):.1f}%</div>
            <div class="kpi-subtext warning">High Profit Skew</div>
        </div>
        """, unsafe_allow_html=True)

    with par_c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">HHI Concentration Index</div>
            <div class="kpi-value">{pareto_profit_stats.get('hhi_score', 0):,.0f}</div>
            <div class="kpi-subtext neutral">{pareto_profit_stats.get('concentration_level', '')}</div>
        </div>
        """, unsafe_allow_html=True)

    with par_c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Top Single SKU Contribution</div>
            <div class="kpi-value">{pareto_profit_stats.get('top_product_share', 0):.1f}%</div>
            <div class="kpi-subtext neutral">{pareto_profit_stats.get('top_product_name', '')[:20]}...</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Pareto Dual-Axis Charts
    col_pareto_1, col_pareto_2 = st.columns(2)

    with col_pareto_1:
        st.markdown("#### Gross Profit Pareto Curve")
        fig_pareto_p = go.Figure()
        fig_pareto_p.add_trace(go.Bar(
            name="Gross Profit ($)",
            x=pareto_profit_df["Product Name"],
            y=pareto_profit_df["Metric_Value"],
            marker_color="#1e40af",
            yaxis="y1"
        ))
        fig_pareto_p.add_trace(go.Scatter(
            name="Cumulative Profit %",
            x=pareto_profit_df["Product Name"],
            y=pareto_profit_df["Cumulative_%"],
            marker=dict(color="#f97316", size=8),
            line=dict(color="#f97316", width=3),
            yaxis="y2"
        ))
        # 80% Benchmark
        fig_pareto_p.add_hline(y=80, line_dash="dash", line_color="#ef4444", yref="y2", annotation_text="80% Threshold")
        
        fig_pareto_p.update_layout(
            height=420,
            margin=dict(l=10, r=10, t=30, b=80),
            yaxis=dict(title="Gross Profit ($)", showgrid=True, gridcolor="#f1f5f9"),
            yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 105], showgrid=False),
            xaxis=dict(tickangle=-45),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_pareto_p, use_container_width=True)

    with col_pareto_2:
        st.markdown("#### Gross Revenue Pareto Curve")
        fig_pareto_s = go.Figure()
        fig_pareto_s.add_trace(go.Bar(
            name="Gross Sales ($)",
            x=pareto_sales_df["Product Name"],
            y=pareto_sales_df["Metric_Value"],
            marker_color="#0d9488",
            yaxis="y1"
        ))
        fig_pareto_s.add_trace(go.Scatter(
            name="Cumulative Sales %",
            x=pareto_sales_df["Product Name"],
            y=pareto_sales_df["Cumulative_%"],
            marker=dict(color="#6366f1", size=8),
            line=dict(color="#6366f1", width=3),
            yaxis="y2"
        ))
        fig_pareto_s.add_hline(y=80, line_dash="dash", line_color="#ef4444", yref="y2", annotation_text="80% Threshold")
        
        fig_pareto_s.update_layout(
            height=420,
            margin=dict(l=10, r=10, t=30, b=80),
            yaxis=dict(title="Gross Revenue ($)", showgrid=True, gridcolor="#f1f5f9"),
            yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 105], showgrid=False),
            xaxis=dict(tickangle=-45),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_pareto_s, use_container_width=True)


# =============================================================================
# TAB 5: STRATEGIC GROWTH MATRIX & VOLATILITY
# =============================================================================
with tab5:
    st.markdown("### 🎯 Strategic Growth Matrix (BCG-Style Portfolio Classification)")
    st.caption("Strategic segmentation based on Sales Volume (scale) and Gross Margin % (profitability).")

    # Matrix Table / Counts
    cat_summary = product_metrics_df.groupby("Strategic_Category").agg(
        SKU_Count=("Product Name", "count"),
        Total_Sales=("Total_Sales", "sum"),
        Total_Profit=("Total_Profit", "sum"),
        Avg_Margin=("Gross_Margin_%", "mean")
    ).reset_index()

    st.dataframe(
        cat_summary,
        column_config={
            "Strategic_Category": st.column_config.TextColumn("Strategic Category", width="medium"),
            "SKU_Count": st.column_config.NumberColumn("Active SKUs", format="%d"),
            "Total_Sales": st.column_config.NumberColumn("Total Sales", format="$%.2f"),
            "Total_Profit": st.column_config.NumberColumn("Gross Profit", format="$%.2f"),
            "Avg_Margin": st.column_config.ProgressColumn("Avg Gross Margin %", format="%.1f%%", min_value=0, max_value=100)
        },
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # Time-Series Gross Margin & Volatility
    st.markdown("### 📉 Monthly Margin Volatility Over Time")
    st.caption("Tracking Gross Margin % stability across historical months.")

    trend_df = get_monthly_profitability_trend(filtered_df)
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        name="Gross Margin %",
        x=trend_df["YearMonth"],
        y=trend_df["Gross_Margin_%"],
        mode="lines+markers",
        line=dict(color="#10b981", width=3),
        marker=dict(size=7),
        yaxis="y1"
    ))
    fig_trend.add_trace(go.Bar(
        name="Monthly Revenue ($)",
        x=trend_df["YearMonth"],
        y=trend_df["Sales"],
        marker_color="rgba(59, 130, 246, 0.3)",
        yaxis="y2"
    ))
    
    fig_trend.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=30, b=20),
        yaxis=dict(title="Gross Margin (%)", showgrid=True, gridcolor="#f1f5f9", range=[40, 85]),
        yaxis2=dict(title="Sales Revenue ($)", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_trend, use_container_width=True)


# =============================================================================
# TAB 6: EXECUTIVE BRIEFING & EXPORT
# =============================================================================
with tab6:
    st.markdown("### 📄 Executive Briefing & Strategic Action Roadmap")
    
    st.markdown("""
    <div class="action-banner">
        <strong>Executive Summary:</strong> Nassau Candy Distributor demonstrates robust core profitability driven by the Wonka Bar line in the Chocolate Division. However, critical margin leakage exists in high-cost SKUs (e.g., Kazookles at 92.3% COGS ratio) and severe profit concentration (33% of catalog generates 80% of net margin).
    </div>
    """, unsafe_allow_html=True)

    e1, e2 = st.columns(2)

    with e1:
        st.markdown("""
        #### 🎯 Key Financial Discoveries
        1. **Chocolate Division Dominance**:
           - Represents **92.9% of Total Sales** and **95.1% of Gross Profit**.
           - All 5 Wonka Bars exhibit healthy unit margins exceeding 64%.
        2. **Critical Margin Leakage in 'Other'**:
           - **Kazookles** generates $1,205.75 in sales but incurs $1,113.00 in cost (7.69% margin).
           - Supplier cost renegotiation or +15% price adjustment will yield over **+$168 profit recovery**.
        3. **High-Margin Niche Sugar Opportunities**:
           - **Everlasting Gobstopper** (80.0% margin) and **Hair Toffee** (77.8% margin) demonstrate exceptional margin strength but suffer from severely constrained sales volume.
        """)

    with e2:
        st.markdown("""
        #### 🚀 Recommended C-Suite Actions
        1. **Immediate Vendor Price Renegotiation**:
           - Audit vendor contract for Kazookles. Cap COGS at <60% of wholesale list price.
        2. **Strategic Repricing on Inelastic Volume**:
           - Implement a 3.5% price increase on top 3 chocolate volume anchors (*Wonka Bar - Scrumdiddlyumptious, Triple Dazzle Caramel, Milk Chocolate*).
        3. **SKU Catalog Rationalization**:
           - Discontinue bottom 3 Sugar SKUs (*Fun Dip, Nerds, Laffy Taffy*) if minimum order volume thresholds are not met to eliminate warehouse handling overhead.
        4. **Scale High-Margin Sugar SKUs**:
           - Launch cross-merchandising campaigns pairing Gobstoppers with Wonka Bars.
        """)

    st.divider()

    # Data Export Center
    st.markdown("### 💾 Export Cleaned Dataset & Reports")
    exp_col1, exp_col2, exp_col3 = st.columns(3)

    with exp_col1:
        csv_filtered = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Transactions CSV",
            data=csv_filtered,
            file_name=f"nassau_candy_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with exp_col2:
        csv_product = product_metrics_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Product Performance CSV",
            data=csv_product,
            file_name=f"nassau_product_performance_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with exp_col3:
        csv_diag = cost_diag_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Remedial Action Register CSV",
            data=csv_diag,
            file_name=f"nassau_remedial_action_register_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
