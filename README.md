# PharmaFlow: Pharmacy Warehouse Management Dashboard

![tests](https://github.com/jaimin-valand/pharmacy-warehouse-dashboard/actions/workflows/tests.yml/badge.svg)

An interactive analytics dashboard for a multi-warehouse pharmacy supply network. Built by **Jaimin Valand** with Streamlit, pandas, NumPy and Plotly.

## Business problem and value

Pharmacy warehouse teams must keep essential medicines available without letting excess or short-dated stock tie up capital or become waste. Stock, batch expiry, supplier reliability and demand signals are often spread across operational exports. PharmaFlow brings those signals into one view so a team can spot replenishment needs, prioritise expiry risk, compare supplier service and balance warehouse capacity before service levels are affected.

## Features

- Sidebar filters for warehouse, therapeutic category and activity date range.
- KPI cards: stock value, low-stock risk with cost to restock, near-expiry batches with value at risk, on-time delivery, annualised inventory turnover and forecast accuracy.
- Usable-stock logic: expired batches can't be dispensed, so they are excluded when checking products against their reorder point. On the sample data this raises stock-out risk from 1 product to 10.
- Expiry value at risk: stock value already expired (likely write-off) and value expiring within 90 days.
- CSV export of the expiry list and the reorder list, ready to hand to a buyer or warehouse team.
- Stock-on-hand versus reorder-point chart and low-stock alert table.
- Expiry-risk bar chart and colour-coded batch detail (expired, within 30 days, 31 to 90 days).
- Monthly inbound/outbound movement, supplier on-time performance and top-moving products.
- Warehouse capacity utilisation gauge.
- Seeded data generator with products, batch-level inventory, orders, shipments, suppliers and warehouse dimensions.

## Tech stack

Python, Streamlit, Plotly, pandas, NumPy, CSV

## Setup and run

Python 3.10 or newer is recommended.

```bash
git clone https://github.com/jaimin-valand/pharmacy-warehouse-dashboard.git
cd pharmacy-warehouse-dashboard
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app builds the synthetic dataset on first run if the `data/` folder is missing, so it also deploys to Streamlit Community Cloud with no extra steps. You can still regenerate it any time with `python generate_data.py`.

Run the tests with:

```bash
pip install pytest
pytest -q
```

The dashboard opens in your browser at the URL printed in the terminal. The generator uses a fixed random seed (2026), so the sample data is reproducible.

## Data note

**All records are synthetic.** Product names and operational metrics are demonstration data, not real customer, supplier, patient or regulated inventory records. The dashboard is not validated for clinical, regulatory or production inventory decisions.

## Skills demonstrated

- SQL-style relational modelling and joins across product, supplier, warehouse, order, shipment and batch-level inventory entities.
- KPI definition, aggregation, date-window analysis and operational storytelling.
- Dimensional thinking: reusable dimensions, facts, grain awareness and interactive slice-and-dice filters.
- Python data generation, data quality checks and dashboard visualisation.
- Business logic separated from the UI (`analytics.py`) and covered by unit tests, with CI on GitHub Actions.

## Project structure

```text
pharmacy-warehouse-dashboard/
├── .streamlit/config.toml
├── .github/workflows/tests.yml
├── tests/
│   ├── test_analytics.py
│   └── test_generate_data.py
├── analytics.py
├── app.py
├── generate_data.py
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```
