"""
analysis.py
-----------
Comprehensive Financial & Product Line Profitability Analytical Engine
for Nassau Candy Distributor.

Provides KPI calculation, product/division ranking, Pareto concentration,
cost-volume-profit diagnostics, margin volatility, and what-if simulation.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np


def calculate_executive_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate executive-level financial and operational KPIs."""
    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_cost": 0.0,
            "total_profit": 0.0,
            "overall_margin": 0.0,
            "total_units": 0,
            "total_orders": 0,
            "avg_order_value": 0.0,
            "avg_profit_per_order": 0.0,
            "profit_per_unit": 0.0
        }

    tot_sales = float(df["Sales"].sum())
    tot_cost = float(df["Cost"].sum())
    tot_profit = float(df["Gross Profit"].sum())
    tot_units = int(df["Units"].sum())
    tot_orders = int(df["Order ID"].nunique())

    margin_pct = (tot_profit / tot_sales * 100.0) if tot_sales > 0 else 0.0
    aov = (tot_sales / tot_orders) if tot_orders > 0 else 0.0
    ppo = (tot_profit / tot_orders) if tot_orders > 0 else 0.0
    ppu = (tot_profit / tot_units) if tot_units > 0 else 0.0

    return {
        "total_revenue": tot_sales,
        "total_cost": tot_cost,
        "total_profit": tot_profit,
        "overall_margin": margin_pct,
        "total_units": tot_units,
        "total_orders": tot_orders,
        "avg_order_value": aov,
        "avg_profit_per_order": ppo,
        "profit_per_unit": ppu
    }


def calculate_margin_volatility(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate month-over-month Gross Margin standard deviation for each product."""
    if df.empty or "YearMonth" not in df.columns:
        return pd.DataFrame(columns=["Product Name", "Margin_Volatility_%", "Monthly_Observations"])

    monthly = df.groupby(["Product Name", "YearMonth"]).agg(
        Monthly_Sales=("Sales", "sum"),
        Monthly_Cost=("Cost", "sum"),
        Monthly_Profit=("Gross Profit", "sum")
    ).reset_index()

    monthly["Monthly_Margin_%"] = (monthly["Monthly_Profit"] / monthly["Monthly_Sales"]) * 100.0

    vol = monthly.groupby("Product Name").agg(
        Margin_Volatility_Pct=("Monthly_Margin_%", "std"),
        Monthly_Observations=("YearMonth", "count"),
        Min_Monthly_Margin=("Monthly_Margin_%", "min"),
        Max_Monthly_Margin=("Monthly_Margin_%", "max")
    ).reset_index()

    vol["Margin_Volatility_Pct"] = vol["Margin_Volatility_Pct"].fillna(0.0).round(2)
    return vol


def get_product_profitability_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Comprehensive product-level profitability, unit economics, contributions,
    and strategic categorization.
    """
    if df.empty:
        return pd.DataFrame()

    total_company_sales = df["Sales"].sum()
    total_company_profit = df["Gross Profit"].sum()
    total_company_units = df["Units"].sum()

    # Product Aggregations
    prod_agg = df.groupby(["Product Name", "Division", "Factory"]).agg(
        Total_Sales=("Sales", "sum"),
        Total_Cost=("Cost", "sum"),
        Total_Profit=("Gross Profit", "sum"),
        Total_Units=("Units", "sum"),
        Order_Count=("Order ID", "nunique")
    ).reset_index()

    # Derived Unit Economics & Margins
    prod_agg["Gross_Margin_%"] = (prod_agg["Total_Profit"] / prod_agg["Total_Sales"]) * 100.0
    prod_agg["Cost_Ratio_%"] = (prod_agg["Total_Cost"] / prod_agg["Total_Sales"]) * 100.0
    prod_agg["Unit_Price"] = prod_agg["Total_Sales"] / prod_agg["Total_Units"]
    prod_agg["Unit_Cost"] = prod_agg["Total_Cost"] / prod_agg["Total_Units"]
    prod_agg["Profit_Per_Unit"] = prod_agg["Total_Profit"] / prod_agg["Total_Units"]

    # Contribution Shares
    prod_agg["Revenue_Share_%"] = (prod_agg["Total_Sales"] / total_company_sales) * 100.0 if total_company_sales > 0 else 0
    prod_agg["Profit_Share_%"] = (prod_agg["Total_Profit"] / total_company_profit) * 100.0 if total_company_profit > 0 else 0
    prod_agg["Units_Share_%"] = (prod_agg["Total_Units"] / total_company_units) * 100.0 if total_company_units > 0 else 0

    # Margin Volatility Integration
    vol_df = calculate_margin_volatility(df)
    prod_agg = prod_agg.merge(vol_df[["Product Name", "Margin_Volatility_Pct"]], on="Product Name", how="left")
    prod_agg["Margin_Volatility_Pct"] = prod_agg["Margin_Volatility_Pct"].fillna(0.0)

    # Strategic Matrix Categorization (BCG & Profitability Matrix)
    median_sales = prod_agg["Total_Sales"].median()
    median_margin = prod_agg["Gross_Margin_%"].median()

    def categorize_product(row):
        sales = row["Total_Sales"]
        margin = row["Gross_Margin_%"]
        cost_ratio = row["Cost_Ratio_%"]
        
        if cost_ratio >= 70.0:
            return "Cost-Heavy Deficit (Renegotiate)"
        elif sales >= median_sales and margin >= median_margin:
            return "Star Driver (High Sales, High Margin)"
        elif sales >= median_sales and margin < median_margin:
            return "Volume Anchor (High Sales, Low Margin - Reprice)"
        elif sales < median_sales and margin >= median_margin:
            return "Niche Opportunity (Low Sales, High Margin - Scale)"
        else:
            return "Underperformer (Low Sales, Low Margin - Discontinue)"

    prod_agg["Strategic_Category"] = prod_agg.apply(categorize_product, axis=1)

    # Sort descending by Profit
    return prod_agg.sort_values(by="Total_Profit", ascending=False).reset_index(drop=True)


def get_division_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate financial performance, margin distributions, and shares by Division."""
    if df.empty:
        return pd.DataFrame()

    total_sales = df["Sales"].sum()
    total_profit = df["Gross Profit"].sum()

    div_agg = df.groupby("Division").agg(
        Total_Sales=("Sales", "sum"),
        Total_Cost=("Cost", "sum"),
        Total_Profit=("Gross Profit", "sum"),
        Total_Units=("Units", "sum"),
        Order_Count=("Order ID", "nunique"),
        Product_Count=("Product Name", "nunique")
    ).reset_index()

    div_agg["Gross_Margin_%"] = (div_agg["Total_Profit"] / div_agg["Total_Sales"]) * 100.0
    div_agg["Cost_Ratio_%"] = (div_agg["Total_Cost"] / div_agg["Total_Sales"]) * 100.0
    div_agg["Profit_Per_Unit"] = div_agg["Total_Profit"] / div_agg["Total_Units"]
    div_agg["Revenue_Share_%"] = (div_agg["Total_Sales"] / total_sales) * 100.0 if total_sales > 0 else 0
    div_agg["Profit_Share_%"] = (div_agg["Total_Profit"] / total_profit) * 100.0 if total_profit > 0 else 0

    return div_agg.sort_values(by="Total_Profit", ascending=False).reset_index(drop=True)


def get_pareto_analysis(df: pd.DataFrame, metric: str = "Gross Profit") -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Perform 80/20 Pareto Analysis for Products on Sales or Gross Profit.
    Computes cumulative sums, cumulative percentages, and concentration risk indices.
    """
    if df.empty:
        return pd.DataFrame(), {}

    target_col = "Gross Profit" if metric == "Gross Profit" else "Sales"
    
    prod_summary = df.groupby(["Product Name", "Division"]).agg(
        Metric_Value=(target_col, "sum"),
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum")
    ).reset_index()

    prod_summary = prod_summary.sort_values(by="Metric_Value", ascending=False).reset_index(drop=True)
    
    total_metric = prod_summary["Metric_Value"].sum()
    total_products = len(prod_summary)

    prod_summary["Rank"] = range(1, total_products + 1)
    prod_summary["Cumulative_Metric"] = prod_summary["Metric_Value"].cumsum()
    prod_summary["Cumulative_%"] = (prod_summary["Cumulative_Metric"] / total_metric) * 100.0
    prod_summary["Product_Cumulative_%"] = (prod_summary["Rank"] / total_products) * 100.0
    prod_summary["Share_%"] = (prod_summary["Metric_Value"] / total_metric) * 100.0

    # Find products reaching 80% threshold
    idx_80 = prod_summary[prod_summary["Cumulative_%"] >= 80.0].index
    if not idx_80.empty:
        count_for_80 = idx_80[0] + 1
    else:
        count_for_80 = total_products

    pct_products_for_80 = (count_for_80 / total_products) * 100.0 if total_products > 0 else 0

    # Top 20% products contribution
    top_20_count = max(1, int(np.ceil(total_products * 0.20)))
    top_20_contrib = prod_summary.iloc[:top_20_count]["Share_%"].sum()

    # Herfindahl-Hirschman Index (HHI) for concentration
    # HHI = sum((market_share_percentage)^2), scale 0 - 10000
    hhi = (prod_summary["Share_%"] ** 2).sum()
    
    if hhi > 2500:
        concentration_level = "High Concentration Risk (Severe Dependency)"
    elif hhi > 1500:
        concentration_level = "Moderate Concentration Risk"
    else:
        concentration_level = "Well-Diversified Portfolio"

    summary_stats = {
        "metric_name": metric,
        "total_metric_value": total_metric,
        "total_products": total_products,
        "products_for_80_pct": count_for_80,
        "pct_of_catalog_for_80_pct": pct_products_for_80,
        "top_20_pct_products_share": top_20_contrib,
        "top_product_name": prod_summary.iloc[0]["Product Name"] if total_products > 0 else "N/A",
        "top_product_share": prod_summary.iloc[0]["Share_%"] if total_products > 0 else 0,
        "hhi_score": round(hhi, 1),
        "concentration_level": concentration_level
    }

    return prod_summary, summary_stats


def get_cost_structure_diagnostics(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cost Structure Diagnostics & Strategic Flagging Engine.
    Identifies margin leakages, cost-heavy SKUs, and flags specific remedial actions:
      1. Repricing Flag: High sales volume, but Gross Margin < 60% (or bottom margin tier)
      2. Cost Renegotiation Flag: Unit Cost > 70% of Sales (Cost Ratio >= 70%)
      3. Discontinuation Flag: Low Sales (< $100) and Low Gross Margin (< 45%) and Low Profit
      4. Scale & Promotion Flag: High Margin (> 70%), but Low Volume (< $500)
    """
    prod_df = get_product_profitability_metrics(df)
    if prod_df.empty:
        return pd.DataFrame(), {}

    sales_median = prod_df["Total_Sales"].median()
    profit_median = prod_df["Total_Profit"].median()

    def generate_flags(row):
        actions = []
        severity = "Low"
        
        # Check Cost Renegotiation
        if row["Cost_Ratio_%"] >= 70.0:
            actions.append("🚨 Cost Renegotiation (Supplier cost >70% of retail)")
            severity = "Critical"
        
        # Check Repricing
        if row["Total_Sales"] >= sales_median and row["Gross_Margin_%"] < 66.0:
            actions.append("🏷️ Reprice (+3-5% price elasticity uplift)")
            if severity != "Critical":
                severity = "Medium"
        elif row["Total_Sales"] >= sales_median and row["Gross_Margin_%"] < 50.0:
            actions.append("🏷️ Reprice Immediately (<50% Margin on High Volume)")
            severity = "High"

        # Check Discontinuation
        if row["Total_Sales"] < 100.0 and row["Gross_Margin_%"] < 50.0 and row["Total_Profit"] < 50.0:
            actions.append("🗑️ Discontinue SKU (Negative ROI / High Admin Cost)")
            if severity == "Low":
                severity = "Medium"

        # Check Scale Opportunity
        if row["Gross_Margin_%"] >= 70.0 and row["Total_Sales"] < 500.0:
            actions.append("🚀 Scale & Promote (High Margin Opportunity)")
            if severity == "Low":
                severity = "Opportunity"

        if not actions:
            actions.append("✅ Healthy Core SKU (Maintain Performance)")

        return pd.Series([", ".join(actions), severity], index=["Recommended_Action", "Action_Severity"])

    flag_results = prod_df.apply(generate_flags, axis=1)
    prod_df["Recommended_Action"] = flag_results["Recommended_Action"]
    prod_df["Action_Severity"] = flag_results["Action_Severity"]

    summary = {
        "renegotiate_count": int(prod_df["Recommended_Action"].str.contains("Cost Renegotiation").sum()),
        "reprice_count": int(prod_df["Recommended_Action"].str.contains("Reprice").sum()),
        "discontinue_count": int(prod_df["Recommended_Action"].str.contains("Discontinue").sum()),
        "scale_count": int(prod_df["Recommended_Action"].str.contains("Scale").sum()),
        "healthy_count": int(prod_df["Recommended_Action"].str.contains("Healthy").sum())
    }

    return prod_df, summary


def simulate_repricing_impact(
    df: pd.DataFrame,
    product_name: str,
    price_pct_change: float = 5.0,
    cost_reduction_pct: float = 0.0,
    demand_elasticity: float = -0.3
) -> Dict[str, Any]:
    """
    Simulate financial impact of price changes and cost renegotiation on a product.
    
    Args:
        df: Input transactions DataFrame
        product_name: Target product to reprice
        price_pct_change: % change in unit selling price (e.g., +5%)
        cost_reduction_pct: % reduction in supplier cost (e.g., +3%)
        demand_elasticity: Price elasticity of demand (default -0.3 for confectionery)
    """
    prod_data = df[df["Product Name"] == product_name]
    if prod_data.empty:
        return {}

    base_sales = float(prod_data["Sales"].sum())
    base_cost = float(prod_data["Cost"].sum())
    base_profit = float(prod_data["Gross Profit"].sum())
    base_units = int(prod_data["Units"].sum())
    base_margin = (base_profit / base_sales * 100.0) if base_sales > 0 else 0.0
    
    base_price = base_sales / base_units if base_units > 0 else 0.0
    base_unit_cost = base_cost / base_units if base_units > 0 else 0.0

    # New Unit Economics
    new_price = base_price * (1.0 + (price_pct_change / 100.0))
    new_unit_cost = base_unit_cost * (1.0 - (cost_reduction_pct / 100.0))

    # Unit volume change based on price elasticity of demand: %ΔQ = Elasticity * %ΔP
    unit_pct_change = demand_elasticity * price_pct_change
    new_units = max(1, int(round(base_units * (1.0 + (unit_pct_change / 100.0)))))

    new_sales = round(new_price * new_units, 2)
    new_cost = round(new_unit_cost * new_units, 2)
    new_profit = round(new_sales - new_cost, 2)
    new_margin = (new_profit / new_sales * 100.0) if new_sales > 0 else 0.0

    profit_delta = new_profit - base_profit
    profit_pct_delta = (profit_delta / base_profit * 100.0) if base_profit > 0 else 0.0

    return {
        "product_name": product_name,
        "base_units": base_units,
        "new_units": new_units,
        "base_sales": base_sales,
        "new_sales": new_sales,
        "base_cost": base_cost,
        "new_cost": new_cost,
        "base_profit": base_profit,
        "new_profit": new_profit,
        "profit_delta": profit_delta,
        "profit_pct_delta": profit_pct_delta,
        "base_margin": base_margin,
        "new_margin": new_margin,
        "margin_delta_pts": new_margin - base_margin
    }


def get_monthly_profitability_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Time-series monthly aggregation of sales, profit, cost, and margin."""
    if df.empty:
        return pd.DataFrame()

    trend = df.groupby("YearMonth").agg(
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum"),
        Order_Count=("Order ID", "nunique")
    ).reset_index()

    trend["Gross_Margin_%"] = (trend["Gross_Profit"] / trend["Sales"]) * 100.0
    trend = trend.sort_values(by="YearMonth").reset_index(drop=True)
    return trend


def get_regional_profitability(df: pd.DataFrame) -> pd.DataFrame:
    """Regional breakdown of sales, profit, and margin performance."""
    if df.empty:
        return pd.DataFrame()

    reg_agg = df.groupby("Region").agg(
        Total_Sales=("Sales", "sum"),
        Total_Cost=("Cost", "sum"),
        Total_Profit=("Gross Profit", "sum"),
        Total_Units=("Units", "sum"),
        Order_Count=("Order ID", "nunique")
    ).reset_index()

    reg_agg["Gross_Margin_%"] = (reg_agg["Total_Profit"] / reg_agg["Total_Sales"]) * 100.0
    reg_agg["Cost_Ratio_%"] = (reg_agg["Total_Cost"] / reg_agg["Total_Sales"]) * 100.0
    reg_agg["Profit_Per_Unit"] = reg_agg["Total_Profit"] / reg_agg["Total_Units"]

    return reg_agg.sort_values(by="Total_Profit", ascending=False).reset_index(drop=True)
