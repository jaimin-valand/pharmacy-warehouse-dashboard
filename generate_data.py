from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


PRODUCTS = [
    ("Amoxicillin 500 mg", "Antibiotics", "capsules", 0.18),
    ("Azithromycin 250 mg", "Antibiotics", "tablets", 0.32),
    ("Cefalexin 500 mg", "Antibiotics", "capsules", 0.27),
    ("Metformin 500 mg", "Diabetes", "tablets", 0.08),
    ("Insulin glargine 100 IU", "Diabetes", "vials", 12.40),
    ("Atorvastatin 20 mg", "Cardiovascular", "tablets", 0.11),
    ("Amlodipine 5 mg", "Cardiovascular", "tablets", 0.06),
    ("Losartan 50 mg", "Cardiovascular", "tablets", 0.09),
    ("Omeprazole 20 mg", "Gastrointestinal", "capsules", 0.13),
    ("Pantoprazole 40 mg", "Gastrointestinal", "tablets", 0.15),
    ("Cetirizine 10 mg", "Respiratory & Allergy", "tablets", 0.05),
    ("Salbutamol inhaler", "Respiratory & Allergy", "inhalers", 2.15),
    ("Budesonide inhaler", "Respiratory & Allergy", "inhalers", 3.80),
    ("Paracetamol 500 mg", "Pain & Fever", "tablets", 0.04),
    ("Ibuprofen 400 mg", "Pain & Fever", "tablets", 0.07),
    ("Diclofenac gel 1%", "Pain & Fever", "tubes", 1.45),
    ("Vitamin D3 1000 IU", "Vitamins & Supplements", "softgels", 0.10),
    ("Folic acid 5 mg", "Vitamins & Supplements", "tablets", 0.03),
    ("Apixaban 5 mg", "Cardiovascular", "tablets", 0.72),
    ("Ondansetron 4 mg", "Gastrointestinal", "tablets", 0.20),
]

SUPPLIERS = [
    ("SUP-001", "Northstar Pharma", "USA", .94),
    ("SUP-002", "MedAxis Laboratories", "India", .88),
    ("SUP-003", "CuraSource Medical", "UK", .91),
    ("SUP-004", "Everwell Generics", "Canada", .83),
    ("SUP-005", "HelixCare Distribution", "Germany", .97),
    ("SUP-006", "BluePeak Therapeutics", "Ireland", .90),
    ("SUP-007", "NovaMed Supply", "Singapore", .86),
    ("SUP-008", "Pioneer Health Products", "Australia", .93),
]

WAREHOUSES = [
    ("WH-01", "East Coast DC", "Newark, NJ", 30_000),
    ("WH-02", "Central DC", "Columbus, OH", 27_500),
    ("WH-03", "West Coast DC", "Reno, NV", 24_000),
    ("WH-04", "South Distribution Hub", "Dallas, TX", 22_000),
]


TABLES = ["products", "inventory", "orders", "shipments", "suppliers", "warehouses"]


def data_is_current(data_dir=DATA_DIR, as_of=None, tables=TABLES):
    """True if every CSV exists and the data was generated on `as_of` (ISO date).

    Dates in the sample data are relative to the day it was generated, so data
    left over from an earlier day would slowly drift into the past.
    """
    data_dir = Path(data_dir)
    if any(not (data_dir / f"{name}.csv").exists() for name in tables):
        return False
    as_of = as_of or pd.Timestamp.today().date().isoformat()
    try:
        stamp = pd.read_csv(data_dir / "inventory.csv", usecols=["last_updated"], nrows=1)["last_updated"]
    except (ValueError, pd.errors.EmptyDataError):
        return False
    return not stamp.empty and str(stamp.iloc[0]) == as_of


def generate_data(output_dir=DATA_DIR, seed=2026):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    today = pd.Timestamp.today().normalize()
    supplier_ids = [item[0] for item in SUPPLIERS]
    warehouse_ids = [item[0] for item in WAREHOUSES]

    products = pd.DataFrame([
        {
            "product_id": f"PH-{index:03d}", "product_name": name, "category": category,
            "unit": unit, "unit_cost": cost, "supplier_id": supplier_ids[index % len(supplier_ids)],
            "reorder_level": int(rng.integers(140, 420)),
        }
        for index, (name, category, unit, cost) in enumerate(PRODUCTS, start=1)
    ])
    suppliers = pd.DataFrame(SUPPLIERS, columns=["supplier_id", "supplier_name", "country", "historical_on_time_rate"])
    warehouses = pd.DataFrame(WAREHOUSES, columns=["warehouse_id", "warehouse_name", "location", "capacity_units"])

    inventory_rows = []
    for _, product in products.iterrows():
        for warehouse_index, warehouse_id in enumerate(warehouse_ids):
            batch_count = int(rng.integers(2, 4))
            total_stock = int(product["reorder_level"] * rng.uniform(.65, 2.2))
            if (int(product["product_id"].split("-")[1]) + warehouse_index) % 11 == 0:
                total_stock = int(product["reorder_level"] * rng.uniform(.25, .8))
            allocation = rng.multinomial(total_stock, np.full(batch_count, 1 / batch_count))
            for batch_index, quantity in enumerate(allocation, start=1):
                expiry_offset = int(rng.choice([rng.integers(-20, 0), rng.integers(0, 30), rng.integers(31, 91), rng.integers(91, 731)]))
                inventory_rows.append({
                    "inventory_id": f"INV-{len(inventory_rows) + 1:05d}", "product_id": product["product_id"],
                    "warehouse_id": warehouse_id,
                    "batch_number": f"{product['product_id'][-3:]}-{warehouse_index + 1}{batch_index}-{rng.integers(1000, 9999)}",
                    "quantity": int(quantity), "expiry_date": (today + pd.Timedelta(days=expiry_offset)).date().isoformat(),
                    "last_updated": today.date().isoformat(),
                })
    inventory = pd.DataFrame(inventory_rows)

    start = today - pd.DateOffset(months=17)
    date_span = max((today - start).days, 1)
    order_rows = []
    for order_index in range(900):
        product = products.iloc[int(rng.integers(0, len(products)))]
        quantity = int(rng.lognormal(mean=3.5, sigma=.65))
        order_rows.append({
            "order_id": f"ORD-{order_index + 1:05d}", "order_date": (start + pd.Timedelta(days=int(rng.integers(0, date_span + 1)))).date().isoformat(),
            "product_id": product["product_id"], "warehouse_id": str(rng.choice(warehouse_ids)),
            "quantity": quantity, "forecast_quantity": max(1, int(quantity * rng.normal(1, .13))),
        })
    orders = pd.DataFrame(order_rows)

    shipment_rows = []
    for shipment_index in range(480):
        product = products.iloc[int(rng.integers(0, len(products)))]
        supplier_id = product["supplier_id"]
        historical_rate = suppliers.loc[suppliers["supplier_id"] == supplier_id, "historical_on_time_rate"].iloc[0]
        order_date = start + pd.Timedelta(days=int(rng.integers(0, date_span + 1)))
        expected = order_date + pd.Timedelta(days=int(rng.integers(5, 13)))
        on_time = bool(rng.random() < historical_rate)
        actual = expected + pd.Timedelta(days=int(rng.integers(-2, 1) if on_time else rng.integers(1, 8)))
        shipment_rows.append({
            "shipment_id": f"SHP-{shipment_index + 1:05d}", "supplier_id": supplier_id,
            "product_id": product["product_id"], "warehouse_id": str(rng.choice(warehouse_ids)),
            "order_date": order_date.date().isoformat(), "expected_delivery": expected.date().isoformat(),
            "actual_delivery": actual.date().isoformat(), "quantity": int(rng.integers(100, 1600)),
            "on_time": on_time,
        })
    shipments = pd.DataFrame(shipment_rows)

    for name, frame in {
        "products": products, "inventory": inventory, "orders": orders, "shipments": shipments,
        "suppliers": suppliers, "warehouses": warehouses,
    }.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False)
    return {name: len(frame) for name, frame in {
        "products": products, "inventory": inventory, "orders": orders, "shipments": shipments,
        "suppliers": suppliers, "warehouses": warehouses,
    }.items()}


if __name__ == "__main__":
    counts = generate_data()
    print("Generated synthetic pharmacy warehouse data:")
    for name, count in counts.items():
        print(f"  {name}.csv: {count:,} rows")
