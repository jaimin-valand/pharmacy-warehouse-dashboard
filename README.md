# PharmaFlow: Pharmacy Warehouse Management Dashboard

An interactive analytics dashboard for a multi-warehouse pharmacy supply network. Built by **Jaimin Valand** with Streamlit, pandas, NumPy and Plotly.

## Business problem and value

Pharmacy warehouse teams must keep essential medicines available without letting excess or short-dated stock tie up capital or become waste. Stock, batch expiry, supplier reliability and demand signals are often spread across operational exports. PharmaFlow brings those signals into one view so a team can spot replenishment needs, prioritise expiry risk, compare supplier service and balance warehouse capacity before service levels are affected.

## Features

- Sidebar filters for warehouse, therapeutic category and activity date range.
- KPI cards: stock value, low-stock risk, near-expiry batches, on-time delivery, annualised inventory turnover and forecast accuracy.
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
python generate_data.py
streamlit run app.py
```

The dashboard opens in your browser at the URL printed in the terminal. The generator uses a fixed random seed (2026), so the sample data is reproducible.

## Data note

**All records are synthetic.** Product names and operational metrics are demonstration data, not real customer, supplier, patient or regulated inventory records. The dashboard is not validated for clinical, regulatory or production inventory decisions.

## Skills demonstrated

- SQL-style relational modelling and joins across product, supplier, warehouse, order, shipment and batch-level inventory entities.
- KPI definition, aggregation, date-window analysis and operational storytelling.
- Dimensional thinking: reusable dimensions, facts, grain awareness and interactive slice-and-dice filters.
- Python data generation, data quality checks and dashboard visualisation.

## Project structure

```text
pharmacy-warehouse-dashboard/
├── .streamlit/config.toml
├── tests/test_generate_data.py
├── app.py
├── generate_data.py
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```
