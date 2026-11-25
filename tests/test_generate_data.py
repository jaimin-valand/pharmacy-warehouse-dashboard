import pandas as pd

from generate_data import generate_data


def test_generate_data_creates_expected_synthetic_dimensions(tmp_path):
    counts = generate_data(tmp_path, seed=2026)

    assert counts["products"] == 20
    assert counts["suppliers"] == 8
    assert counts["warehouses"] == 4
    assert counts["inventory"] >= counts["products"] * counts["warehouses"] * 2
    assert counts["orders"] == 900
    assert counts["shipments"] == 480

    products = pd.read_csv(tmp_path / "products.csv")
    inventory = pd.read_csv(tmp_path / "inventory.csv")
    orders = pd.read_csv(tmp_path / "orders.csv")
    assert products["product_id"].is_unique
    assert inventory["batch_number"].is_unique
    assert inventory["quantity"].ge(0).all()
    assert orders["forecast_quantity"].gt(0).all()


def test_generator_is_reproducible_for_same_seed(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    generate_data(first, seed=43)
    generate_data(second, seed=43)

    for filename in ("products.csv", "inventory.csv", "orders.csv", "shipments.csv"):
        assert (first / filename).read_bytes() == (second / filename).read_bytes()
