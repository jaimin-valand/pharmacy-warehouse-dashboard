from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analytics import RISK_ORDER, add_inventory_measures, low_stock_report, value_at_risk
from generate_data import generate_data


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CHART_TEMPLATE = "plotly_dark"
ACCENT = "#39D0B4"

st.set_page_config(
    page_title="PharmaFlow | Warehouse Intelligence",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)


REQUIRED_TABLES = ["products", "inventory", "orders", "shipments", "suppliers", "warehouses"]


@st.cache_data(show_spinner="Loading warehouse data...")
def load_data():
    required = REQUIRED_TABLES
    if any(not (DATA_DIR / f"{name}.csv").exists() for name in required):
        # First run (or a fresh cloud deploy): build the synthetic dataset automatically.
        generate_data(DATA_DIR)

    data = {name: pd.read_csv(DATA_DIR / f"{name}.csv") for name in required}
    for column in ("expiry_date", "last_updated"):
        data["inventory"][column] = pd.to_datetime(data["inventory"][column])
    for column in ("order_date",):
        data["orders"][column] = pd.to_datetime(data["orders"][column])
    for column in ("order_date", "expected_delivery", "actual_delivery"):
        data["shipments"][column] = pd.to_datetime(data["shipments"][column])
    return data


def style_expiry(value):
    styles = {
        "Expired": "background-color: #642e39; color: #ffd8df",
        "≤30 days": "background-color: #704126; color: #ffe0bb",
        "31–90 days": "background-color: #665b2d; color: #fff0b3",
    }
    return styles.get(value, "")


def metric_card(label, value, detail, icon):
    st.markdown(
        f"""<div class="metric-card"><div class="metric-top"><span>{label}</span><span class="metric-icon">{icon}</span></div>
        <div class="metric-value">{value}</div><div class="metric-detail">{detail}</div></div>""",
        unsafe_allow_html=True,
    )


def main():
    st.markdown(
        """<style>
        .block-container {padding-top: 1.5rem; padding-bottom: 2.2rem; max-width: 1500px;}
        [data-testid="stSidebar"] {border-right: 1px solid #263344;}
        .eyebrow {color:#39D0B4; text-transform:uppercase; letter-spacing:.15em; font-size:.72rem; font-weight:700;}
        .hero-title {font-size:2rem; line-height:1.12; font-weight:750; letter-spacing:-.04em; margin:.2rem 0 .4rem;}
        .hero-subtitle {color:#91A0B5; margin-bottom:1.2rem; font-size:.95rem;}
        .metric-card {background:linear-gradient(145deg,#172332,#121b27); border:1px solid #28394b; border-radius:14px; padding:16px 17px 15px; min-height:132px;}
        .metric-top {display:flex; justify-content:space-between; color:#9BAABD; font-size:.82rem; font-weight:550;}
        .metric-icon {font-size:1.1rem;}
        .metric-value {font-size:1.72rem; font-weight:750; letter-spacing:-.04em; margin:.48rem 0 .22rem;}
        .metric-detail {font-size:.75rem; color:#7F91A8;}
        .section-kicker {color:#7F91A8; font-size:.75rem; text-transform:uppercase; letter-spacing:.12em; font-weight:650; margin-bottom:-.7rem;}
        </style>""",
        unsafe_allow_html=True,
    )

    data = load_data()
    products = data["products"]
    inventory = data["inventory"].merge(products, on="product_id", how="left")
    inventory = inventory.merge(data["warehouses"], on="warehouse_id", how="left")
    orders = data["orders"].merge(products[["product_id", "category"]], on="product_id", how="left")
    shipments = data["shipments"].merge(data["suppliers"][["supplier_id", "supplier_name"]], on="supplier_id", how="left")

    st.sidebar.markdown("### 💊 PharmaFlow")
    st.sidebar.caption("Warehouse intelligence")
    st.sidebar.divider()
    warehouse_options = ["All warehouses", *sorted(data["warehouses"]["warehouse_name"].unique())]
    selected_warehouse = st.sidebar.selectbox("Warehouse", warehouse_options)
    category_options = ["All categories", *sorted(products["category"].unique())]
    selected_category = st.sidebar.selectbox("Product category", category_options)
    min_date = min(orders["order_date"].min(), shipments["order_date"].min()).date()
    max_date = max(orders["order_date"].max(), shipments["order_date"].max()).date()
    selected_dates = st.sidebar.date_input("Activity date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date, end_date = map(pd.Timestamp, selected_dates)
    else:
        start_date = end_date = pd.Timestamp(selected_dates)
    st.sidebar.divider()
    st.sidebar.caption("All dashboard data is synthetic and generated for demonstration.")

    inv = inventory.copy()
    if selected_warehouse != "All warehouses":
        inv = inv[inv["warehouse_name"] == selected_warehouse]
    if selected_category != "All categories":
        inv = inv[inv["category"] == selected_category]
    wh_ids = inv["warehouse_id"].unique()
    filtered_orders = orders[(orders["order_date"] >= start_date) & (orders["order_date"] <= end_date)]
    filtered_shipments = shipments[(shipments["order_date"] >= start_date) & (shipments["order_date"] <= end_date)]
    if selected_warehouse != "All warehouses":
        filtered_orders = filtered_orders[filtered_orders["warehouse_id"].isin(wh_ids)]
        filtered_shipments = filtered_shipments[filtered_shipments["warehouse_id"].isin(wh_ids)]
    if selected_category != "All categories":
        category_ids = products.loc[products["category"] == selected_category, "product_id"]
        filtered_orders = filtered_orders[filtered_orders["product_id"].isin(category_ids)]
        filtered_shipments = filtered_shipments[filtered_shipments["product_id"].isin(category_ids)]

    today = pd.Timestamp.today().normalize()
    inv = add_inventory_measures(inv, today)
    summary, low_stock = low_stock_report(inv, inv["warehouse_id"].nunique())
    expiry_window = inv[inv["days_to_expiry"].between(0, 90)]
    expiry_risk = inv[inv["days_to_expiry"] <= 90].copy()
    expired_value, expiring_value = value_at_risk(inv)

    stock_value = inv["stock_value"].sum()
    average_inventory = max(inv["quantity"].sum(), 1)
    period_days = max((end_date - start_date).days + 1, 1)
    annualized_turnover = (filtered_orders["quantity"].sum() / average_inventory) * (365 / period_days)
    actual = filtered_orders["quantity"].sum()
    forecast_error = (filtered_orders["forecast_quantity"] - filtered_orders["quantity"]).abs().sum()
    forecast_accuracy = max(0, 1 - forecast_error / max(actual, 1)) * 100
    on_time_rate = filtered_shipments["on_time"].astype(bool).mean() * 100 if not filtered_shipments.empty else 0

    st.markdown('<div class="eyebrow">Operations overview · Live snapshot</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Pharmacy Warehouse Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Monitor inventory health, expiry exposure, replenishment and supplier reliability across your network.</div>', unsafe_allow_html=True)

    cards = st.columns(6)
    metrics = [
        ("Total stock value", f"${stock_value:,.0f}", "At current unit cost", "◈"),
        ("Stock-out risk", f"{len(low_stock)}", f"Below reorder point · ${low_stock['reorder_cost'].sum():,.0f} to restock", "⚠"),
        ("Expiring ≤ 90 days", f"{len(expiry_window)}", f"Batches · ${expiring_value:,.0f} at risk", "◷"),
        ("On-time delivery", f"{on_time_rate:.1f}%", f"{len(filtered_shipments):,} receipts in period", "↗"),
        ("Inventory turnover", f"{annualized_turnover:.2f}×", "Annualized from selected period", "⟳"),
        ("Forecast accuracy", f"{forecast_accuracy:.1f}%", "1 − WAPE, selected period", "◎"),
    ]
    for col, metric in zip(cards, metrics):
        with col:
            metric_card(*metric)

    st.write("")
    left, right = st.columns([1.18, 1])
    with left:
        st.markdown('<div class="section-kicker">Replenishment</div>', unsafe_allow_html=True)
        stock_chart = summary.sort_values("usable").head(14).sort_values("usable", ascending=True)
        fig_stock = go.Figure()
        fig_stock.add_trace(go.Bar(y=stock_chart["product_name"], x=stock_chart["usable"], name="Usable on hand", orientation="h", marker_color=ACCENT))
        fig_stock.add_trace(go.Scatter(y=stock_chart["product_name"], x=stock_chart["reorder_level"], name="Reorder point", mode="markers", marker=dict(color="#FFB454", size=10, symbol="line-ns-open", line=dict(width=2))))
        fig_stock.update_layout(template=CHART_TEMPLATE, height=390, margin=dict(l=5, r=10, t=25, b=5), xaxis_title="Units", yaxis_title="", legend=dict(orientation="h", y=1.12), barmode="overlay")
        st.plotly_chart(fig_stock, width="stretch")
    with right:
        st.markdown('<div class="section-kicker">Storage capacity</div>', unsafe_allow_html=True)
        capacity = data["warehouses"].merge(
            inv.groupby("warehouse_id", as_index=False)["quantity"].sum(), on="warehouse_id", how="inner"
        )
        total_capacity = capacity["capacity_units"].sum()
        utilization = capacity["quantity"].sum() / max(total_capacity, 1) * 100
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=utilization, number={"suffix": "%", "font": {"size": 42}},
            title={"text": "Network utilization", "font": {"size": 15, "color": "#9BAABD"}},
            gauge={"axis": {"range": [0, 100], "ticksuffix": "%", "tickcolor": "#718096"},
                   "bar": {"color": ACCENT}, "bgcolor": "#172332", "bordercolor": "#28394b",
                   "steps": [{"range": [0, 70], "color": "#1A2A38"}, {"range": [70, 90], "color": "#3B3827"}, {"range": [90, 100], "color": "#432B35"}],
                   "threshold": {"line": {"color": "#FFB454", "width": 3}, "thickness": .8, "value": 90}}
        ))
        fig_gauge.update_layout(template=CHART_TEMPLATE, height=280, margin=dict(l=20, r=20, t=55, b=5))
        st.plotly_chart(fig_gauge, width="stretch")
        st.caption(f"{capacity['warehouse_id'].nunique()} warehouse(s) in scope · {capacity['quantity'].sum():,.0f} / {total_capacity:,.0f} units")

    left, right = st.columns([1.15, 1])
    with left:
        st.markdown('<div class="section-kicker">Expiry exposure · batches expiring or expired within 90 days</div>', unsafe_allow_html=True)
        expiry_counts = expiry_risk.groupby("risk", as_index=False).agg(batches=("batch_number", "nunique"), units=("quantity", "sum"))
        expiry_counts["risk"] = pd.Categorical(expiry_counts["risk"], categories=RISK_ORDER, ordered=True)
        expiry_counts = expiry_counts.sort_values("risk")
        fig_expiry = px.bar(expiry_counts, x="risk", y="units", color="risk", text="batches", color_discrete_map={"Expired": "#E56B78", "≤30 days": "#F0A45D", "31–90 days": "#D8C66A"})
        fig_expiry.update_layout(template=CHART_TEMPLATE, height=290, margin=dict(l=5, r=10, t=20, b=5), showlegend=False, xaxis_title="", yaxis_title="Units at risk")
        fig_expiry.update_traces(texttemplate="%{text} batches", textposition="outside", cliponaxis=False)
        st.plotly_chart(fig_expiry, width="stretch")
        st.caption(f"${expired_value:,.0f} of stock already expired (likely write-off) · ${expiring_value:,.0f} expiring within 90 days")
    with right:
        st.markdown('<div class="section-kicker">Supplier on-time performance</div>', unsafe_allow_html=True)
        supplier_performance = filtered_shipments.groupby("supplier_name", as_index=False).agg(
            on_time_rate=("on_time", "mean"), receipts=("shipment_id", "count")
        ).sort_values("on_time_rate")
        supplier_performance["on_time_rate"] *= 100
        fig_supplier = px.bar(supplier_performance, x="on_time_rate", y="supplier_name", orientation="h", color="on_time_rate", color_continuous_scale=["#E56B78", "#F0A45D", ACCENT], text="on_time_rate", hover_data=["receipts"])
        fig_supplier.update_layout(template=CHART_TEMPLATE, height=290, margin=dict(l=5, r=25, t=20, b=5), coloraxis_showscale=False, xaxis_title="On-time receipts (%)", yaxis_title="", xaxis_range=[0, 110])
        fig_supplier.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
        st.plotly_chart(fig_supplier, width="stretch")

    left, right = st.columns([1.15, 1])
    with left:
        st.markdown('<div class="section-kicker">Monthly inbound / outbound movement</div>', unsafe_allow_html=True)
        inbound = filtered_shipments.groupby(filtered_shipments["order_date"].dt.to_period("M"))["quantity"].sum().rename("Inbound").to_frame()
        outbound = filtered_orders.groupby(filtered_orders["order_date"].dt.to_period("M"))["quantity"].sum().rename("Outbound").to_frame()
        movement = inbound.join(outbound, how="outer").fillna(0).rename_axis("month").reset_index()
        movement["month"] = movement["month"].astype(str)
        movement_long = movement.melt(id_vars="month", var_name="flow", value_name="units")
        fig_flow = px.line(movement_long, x="month", y="units", color="flow", markers=True, color_discrete_map={"Inbound": ACCENT, "Outbound": "#829CFF"})
        fig_flow.update_layout(template=CHART_TEMPLATE, height=300, margin=dict(l=5, r=10, t=20, b=5), xaxis_title="Month", yaxis_title="Units", legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig_flow, width="stretch")
    with right:
        st.markdown('<div class="section-kicker">Top moving products</div>', unsafe_allow_html=True)
        top_products = filtered_orders.groupby("product_id", as_index=False).agg(units_moved=("quantity", "sum")).merge(products, on="product_id").nlargest(8, "units_moved").sort_values("units_moved")
        fig_top = px.bar(top_products, x="units_moved", y="product_name", orientation="h", color="units_moved", color_continuous_scale=["#325D70", ACCENT], text="units_moved")
        fig_top.update_layout(template=CHART_TEMPLATE, height=300, margin=dict(l=5, r=15, t=20, b=5), xaxis_title="Units moved", yaxis_title="", coloraxis_showscale=False)
        fig_top.update_traces(texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False)
        st.plotly_chart(fig_top, width="stretch")

    st.markdown('<div class="section-kicker">Expiry risk detail</div>', unsafe_allow_html=True)
    if expiry_risk.empty:
        st.success("No expired or near-expiry batches in the current scope.")
    else:
        expiry_columns = ["product_name", "category", "warehouse_name", "batch_number", "quantity", "expiry_date", "days_to_expiry", "risk"]
        expiry_view = expiry_risk[expiry_columns].sort_values("days_to_expiry").rename(columns={
            "product_name": "Product", "category": "Category", "warehouse_name": "Warehouse", "batch_number": "Batch",
            "quantity": "Units", "expiry_date": "Expiry date", "days_to_expiry": "Days left", "risk": "Expiry risk"
        })
        expiry_view["Expiry date"] = expiry_view["Expiry date"].dt.date
        st.dataframe(expiry_view.style.map(style_expiry, subset=["Expiry risk"]), width="stretch", hide_index=True)
        st.download_button("Download expiry list (CSV)", expiry_view.to_csv(index=False), "expiry_risk.csv", "text/csv")

    st.markdown('<div class="section-kicker">Low-stock alerts</div>', unsafe_allow_html=True)
    if low_stock.empty:
        st.success("No products are at or below their reorder point in the current scope.")
    else:
        low_view = low_stock[["product_name", "category", "quantity", "usable", "reorder_level", "gap", "unit_cost", "reorder_cost"]].copy()
        low_view = low_view.rename(columns={
            "product_name": "Product", "category": "Category", "quantity": "On hand (incl. expired)", "usable": "Usable stock",
            "reorder_level": "Reorder point", "gap": "Below reorder by", "unit_cost": "Unit cost ($)", "reorder_cost": "Cost to restock ($)",
        })
        st.caption("Usable stock excludes expired batches, which can't be dispensed.")
        st.dataframe(low_view.style.format({"Unit cost ($)": "${:,.2f}", "Cost to restock ($)": "${:,.0f}"}), width="stretch", hide_index=True)
        st.download_button("Download reorder list (CSV)", low_view.to_csv(index=False), "reorder_list.csv", "text/csv")

    st.caption("PharmaFlow · Synthetic demonstration dataset · Operational insights are indicative, not a substitute for validated inventory controls.")


if __name__ == "__main__":
    main()
