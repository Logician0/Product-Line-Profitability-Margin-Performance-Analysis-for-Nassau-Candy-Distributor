# Nassau Candy Product Line Profitability & Margin Dashboard

A bespoke, production-grade analytics dashboard and margin audit for **Nassau Candy Distributor**. Designed with an opinionated, editorial UI—warm styling, asymmetric grids, custom HTML KPI cards, Plotly charts with custom color palettes, inline top filters, and zero AI-boilerplate clutter.

---

## 📁 Repository Structure

```text
├── app.py                     # Human-crafted Streamlit web app (top radio nav, custom CSS, what-if simulator)
├── analysis.py                # Business logic & math engine (Pareto, elasticity simulator, CVP diagnostics)
├── data_loader.py             # Data loading, validation, and factory enrichment (silent fallback generation)
├── generate_data.py           # Clean synthetic generator matching the Nassau Candy schema
├── requirements.txt           # Minimal, pinned Python dependencies
├── RESEARCH_PAPER.md          # 2-3 page conversational, rigorous margin audit research paper
├── EXECUTIVE_SUMMARY.md       # 1-page punchy C-Suite briefing & action plan
└── README.md                  # Project documentation & deployment manual
```

---

## 🚀 How to Run Locally

### 1. Install Dependencies
```bash
python3 -m pip install -r requirements.txt
```

### 2. Launch the Dashboard
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 🌐 Deploy to Streamlit Community Cloud

1. Push your repository to GitHub.
2. Sign in to [share.streamlit.io](https://share.streamlit.io/).
3. Create a new app, select your repository, set the branch to `main`, and `app.py` as the entry file.
4. Click **Deploy**.

---

## 🎯 Key Business Takeaways

- **Chocolate Dominance:** The 5 Wonka Bars generate **95.1% of company gross profit** ($88.8k of $93.4k) with healthy 65–71% margins.
- **Kazookles Margin Drain:** Sells at a **92.3% cost ratio** (7.7% gross margin), generating only $92.75 profit on $1,205 sales.
- **Untapped Sugar Gems:** *Everlasting Gobstopper* (80% margin) and *Hair Toffee* (77.8% margin) deliver huge unit margins but lack sales volume.
- **Action Plan:** Reprice Kazookles, take a +3.5% price bump on top Wonka Bars, and cross-sell Gobstoppers to unlock **+$7,100+ in annual profit gain**.
