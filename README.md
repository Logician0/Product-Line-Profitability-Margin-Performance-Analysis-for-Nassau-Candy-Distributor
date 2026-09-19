# Nassau Candy Distributor: Product Line Profitability & Margin Performance Dashboard

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18%2B-3F4F75.svg)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An award-winning, production-grade enterprise analytics web application and research project for **Nassau Candy Distributor**. This project delivers comprehensive unit-economic diagnostics, profit concentration (80/20 Pareto) analysis, multi-division benchmarking, manufacturing plant throughput tracking, and an interactive what-if repricing simulator.

---

## 📁 Repository Structure

```
├── Nassau Candy Distributor.csv      # Primary commercial transaction dataset (10,194 records)
├── app.py                            # World-class Streamlit web dashboard application
├── analysis.py                       # Analytical calculation engine (Pareto, BCG, CVP, Volatility)
├── data_loader.py                    # Data ingestion, cleaning, validation & factory mapping
├── generate_synthetic_data.py        # Synthetic dataset generator for tests/missing dataset fallback
├── requirements.txt                  # Pinned dependencies for local & cloud deployment
├── RESEARCH_PAPER.md                 # Rigorous academic & empirical CVP research paper
├── EXECUTIVE_SUMMARY.md              # High-impact C-Suite executive briefing & action plan
└── README.md                         # Project documentation and deployment manual
```

---

## 🚀 Key Dashboard Features

1. **Executive KPI Ribbon:**
   - Real-time Gross Revenue, Gross Profit, Blended Margin %, Units Shipped, and Diagnostic Action Flags.
2. **Tab 1: Product Profitability Overview:**
   - Interactive Margin Leaderboard with conditional gradient heatmaps.
   - Top products by Gross Profit ($) and Gross Margin (%) horizontal bar charts.
   - Multi-dimensional Bubble Chart (Sales vs. Gross Margin % with profit sizing and median quadrant dividers).
3. **Tab 2: Division & Factory Performance:**
   - Division revenue vs gross profit grouped bar charts.
   - Gross margin distribution boxplots showing transaction-level dispersion.
   - Manufacturing plant throughput and interactive US facility map for 5 regional plants.
4. **Tab 3: Cost Structure & Margin Diagnostics:**
   - Cost vs. Sales diagnostic scatter plot with 70% cost threshold alert line.
   - Automated Remedial Action Register highlighting critical cost-heavy SKUs (e.g. *Kazookles*).
   - Interactive What-If Repricing & Profit Recovery Simulator with price elasticity modeling.
5. **Tab 4: Profit Concentration (Pareto 80/20):**
   - Dual-axis Gross Profit and Gross Revenue Pareto curves with 80% threshold line.
   - Dependency indicators, Top 20% SKU share, and Herfindahl-Hirschman Index (HHI) score.
6. **Tab 5: Strategic Growth Matrix & Volatility:**
   - BCG-style 4-quadrant portfolio classification (*Star Drivers, Volume Anchors, Niche Gems, Underperformers*).
   - Time-series monthly gross margin volatility tracking.
7. **Tab 6: Executive Briefing & Data Export:**
   - Structured C-Suite strategic roadmap.
   - One-click CSV export center for filtered transactions, product summaries, and action registers.

---

## 💻 Local Quickstart

### Prerequisites
- Python 3.9 or higher
- `pip` package manager

### 1. Clone or Open Workspace
```bash
cd "Product Line Profitability & Margin Performance Analysis for Nassau Candy Distributor"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Streamlit Application
```bash
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

---

## ☁️ Deployment on Streamlit Community Cloud

Deploying this dashboard to the web takes under 2 minutes:

1. **Push to GitHub:**
   - Initialize git and push this repository to GitHub:
     ```bash
     git init
     git add .
     git commit -m "Initial commit: Nassau Candy Profitability Dashboard"
     git branch -M main
     git remote add origin https://github.com/<your-username>/nassau-candy-profitability.git
     git push -u origin main
     ```
2. **Deploy on Streamlit Community Cloud:**
   - Visit [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
   - Click **New App**.
   - Select your repository: `<your-username>/nassau-candy-profitability`.
   - Set **Main file path** to `app.py`.
   - Click **Deploy**!

---

## 📊 Core Analytical Findings

| Finding | Metric / Insight |
| :--- | :--- |
| **Gross Margin Integrity** | Recalculated Gross Profit enforces $\text{Sales} - \text{Cost} = \text{Gross Profit}$ without rounding drift. |
| **Division Concentration** | **Chocolate accounts for 95.06% of total company profit** ($88.8k out of $93.4k). |
| **80/20 Pareto Rule** | **5 out of 15 products (33.3%) drive 95.1% of gross profit**. |
| **Critical Margin Leakage** | *Kazookles* exhibits a **92.31% cost ratio**, earning only $92.75 profit on $1,205.75 sales (7.69% margin). |
| **High-Margin Niche** | *Everlasting Gobstoppers* (80.0% margin) and *Hair Toffee* (77.8% margin) have high margin potential but require volume scaling. |

---

## 🛠️ Testing & Data Pipeline

You can run automated validation on the data pipeline and analytics engine at any time:

```bash
python -c "
from data_loader import load_and_clean_data
from analysis import calculate_executive_kpis, get_cost_structure_diagnostics

df, audit = load_and_clean_data()
print('Cleaned rows:', len(df))
print('Executive KPIs:', calculate_executive_kpis(df))
"
```

To regenerate synthetic test data:
```bash
python generate_synthetic_data.py
```

---

## 📄 Documentation Deliverables

- [**RESEARCH_PAPER.md**](file:///Users/surajkumar/Desktop/Programs/Python%20Projects/Product%20Line%20Profitability%20&%20Margin%20Performance%20Analysis%20for%20Nassau%20Candy%20Distributor/RESEARCH_PAPER.md): Comprehensive academic & empirical research paper.
- [**EXECUTIVE_SUMMARY.md**](file:///Users/surajkumar/Desktop/Programs/Python%20Projects/Product%20Line%20Profitability%20&%20Margin%20Performance%20Analysis%20for%20Nassau%20Candy%20Distributor/EXECUTIVE_SUMMARY.md): Strategic C-Suite briefing with financial projections and 4-pillar action plan.

---
*Developed for Nassau Candy Distributor Executive Leadership.*
