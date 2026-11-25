"""Business logic for the PharmaFlow dashboard, kept separate from the UI so it can be tested."""

import numpy as np
import pandas as pd


RISK_ORDER = ["Expired", "≤30 days", "31–90 days"]


def classify_expiry(days_to_expiry):
    """Bucket days-to-expiry into risk bands. Anything beyond 90 days is 'OK'."""
    days = pd.Series(days_to_expiry)
    return pd.Series(
        np.select([days < 0, days <= 30, days <= 90], RISK_ORDER, default="OK"),
        index=days.index,
    )


def add_inventory_measures(inventory, today):
    """Add stock value, days to expiry, risk band and usable quantity to batch-level inventory."""
    inv = inventory.copy()
    inv["stock_value"] = inv["quantity"] * inv["unit_cost"]
    inv["days_to_expiry"] = (inv["expiry_date"] - today).dt.days
    inv["risk"] = classify_expiry(inv["days_to_expiry"]).values
    # Expired batches can't be dispensed, so they don't count towards usable stock.
    inv["usable_quantity"] = np.where(inv["days_to_expiry"] < 0, 0, inv["quantity"])
    return inv


def low_stock_report(inv, warehouses_in_scope):
    """Products whose usable stock is at or below the reorder point for the selected scope.

    The product reorder level is set per warehouse, so it is scaled by the number of
    warehouses in scope when looking at the whole network.
    """
    summary = inv.groupby(["product_id", "product_name", "category", "unit_cost", "reorder_level"], as_index=False).agg(
        quantity=("quantity", "sum"), usable=("usable_quantity", "sum"), batches=("batch_number", "nunique")
    )
    summary["reorder_level"] = summary["reorder_level"] * max(1, warehouses_in_scope)
    summary["gap"] = summary["reorder_level"] - summary["usable"]
    summary["reorder_cost"] = summary["gap"].clip(lower=0) * summary["unit_cost"]
    low = summary[summary["usable"] <= summary["reorder_level"]].sort_values("gap", ascending=False)
    return summary, low


def value_at_risk(inv):
    """Stock value already expired and stock value expiring within 90 days."""
    expired = inv.loc[inv["days_to_expiry"] < 0, "stock_value"].sum()
    expiring = inv.loc[inv["days_to_expiry"].between(0, 90), "stock_value"].sum()
    return float(expired), float(expiring)
