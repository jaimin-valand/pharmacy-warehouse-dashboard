import pandas as pd

from analytics import add_inventory_measures, classify_expiry, low_stock_report, value_at_risk


TODAY = pd.Timestamp("2026-01-01")


def sample_inventory():
    return pd.DataFrame({
        "product_id": ["P1", "P1", "P2"],
        "product_name": ["Alpha", "Alpha", "Beta"],
        "category": ["A", "A", "B"],
        "unit_cost": [2.0, 2.0, 1.0],
        "reorder_level": [100, 100, 50],
        "warehouse_id": ["W1", "W1", "W1"],
        "batch_number": ["b1", "b2", "b3"],
        "quantity": [80, 60, 200],
        "expiry_date": pd.to_datetime(["2025-12-20", "2026-01-20", "2027-01-01"]),
    })


def test_classify_expiry_bands():
    assert list(classify_expiry([-1, 0, 30, 31, 90, 91])) == ["Expired", "≤30 days", "≤30 days", "31–90 days", "31–90 days", "OK"]


def test_expired_batches_do_not_count_as_usable_stock():
    inv = add_inventory_measures(sample_inventory(), TODAY)
    _, low = low_stock_report(inv, warehouses_in_scope=1)
    # Alpha has 140 units on hand but only 60 usable, so it is below its reorder point of 100.
    assert list(low["product_name"]) == ["Alpha"]
    row = low.iloc[0]
    assert row["usable"] == 60 and row["gap"] == 40 and row["reorder_cost"] == 80


def test_reorder_level_scales_with_warehouses_in_scope():
    inv = add_inventory_measures(sample_inventory(), TODAY)
    summary, _ = low_stock_report(inv, warehouses_in_scope=3)
    assert summary.set_index("product_name").loc["Beta", "reorder_level"] == 150


def test_value_at_risk():
    inv = add_inventory_measures(sample_inventory(), TODAY)
    expired, expiring = value_at_risk(inv)
    assert expired == 160 and expiring == 120
