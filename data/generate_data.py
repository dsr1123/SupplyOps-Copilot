"""Generate the synthetic SupplyOps dataset.

Run from the project root:

    python data/generate_data.py

The output is fully determined by SEED: running the script twice must produce
byte-identical files (checked with `git status`).

Planning horizon convention (used by the data loader as well):

    a date d is inside the horizon  <=>  PLANNING_DATE <= d < PLANNING_DATE + HORIZON_DAYS
"""

import json
import math
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent
SCENARIO_DIR = DATA_DIR / "scenarios"

SEED = 42
PLANNING_DATE = date(2026, 11, 1)
HORIZON_DAYS = 3
HORIZON_END = PLANNING_DATE + timedelta(days=HORIZON_DAYS)  # exclusive

# id, name, region, lat, lon, demand weight
WAREHOUSES = [
    ("WH-SH", "Shanghai", "East", 31.23, 121.47, 1.6),
    ("WH-BJ", "Beijing", "North", 39.90, 116.40, 1.5),
    ("WH-GZ", "Guangzhou", "South", 23.13, 113.26, 1.3),
    ("WH-SZ", "Shenzhen", "South", 22.54, 114.06, 1.2),
    ("WH-CD", "Chengdu", "Southwest", 30.57, 104.07, 1.0),
    ("WH-WH", "Wuhan", "Central", 30.59, 114.31, 0.9),
    ("WH-XA", "Xi'an", "Northwest", 34.34, 108.94, 0.8),
    ("WH-SY", "Shenyang", "Northeast", 41.80, 123.43, 0.7),
    ("WH-HZ", "Hangzhou", "East", 30.27, 120.15, 1.0),
    ("WH-ZZ", "Zhengzhou", "Central", 34.75, 113.62, 0.8),
]

SKUS = [
    ("SKU-A", "Industrial Pump"),
    ("SKU-B", "Control Valve"),
    ("SKU-C", "Pressure Sensor"),
    ("SKU-D", "Motor Assembly"),
    ("SKU-E", "Gear Box"),
    ("SKU-F", "Bearing Kit"),
    ("SKU-G", "Hydraulic Hose"),
    ("SKU-H", "PLC Module"),
    ("SKU-I", "Cooling Fan"),
    ("SKU-J", "Power Supply"),
]

# priority, delay_penalty, allow_delay
PRIORITY_RULES = [
    ("VIP", 100, False),
    ("HIGH", 50, True),
    ("NORMAL", 10, True),
    ("LOW", 5, True),
]
PRIORITY_MIX = [0.10, 0.20, 0.50, 0.20]

# The disruption demo cell: WH-SH / SKU-A is hand-crafted (see OPT_MODEL.md §11).
DEMO_WH, DEMO_SKU = "WH-SH", "SKU-A"
DEMO_ON_HAND = 160
DEMO_ORDERS = [  # quantity, due offset (days), priority
    (80, 0, "VIP"),
    (120, 1, "HIGH"),
    (100, 1, "NORMAL"),
    (120, 2, "NORMAL"),
    (60, 4, "LOW"),  # outside the horizon
]
DEMO_PO = ("PO-1024", "SUP-01", DEMO_SKU, DEMO_WH, 500, PLANNING_DATE + timedelta(days=1), "CONFIRMED")

N_RANDOM_ORDERS = 150 - len(DEMO_ORDERS)
N_RANDOM_POS = 24
NEAREST_NEIGHBORS = 2
TRUNK_LANES = [("WH-SH", "WH-BJ"), ("WH-SH", "WH-GZ")]
EXPEDITE_SHARE = 0.3


def in_horizon(d: date) -> bool:
    return PLANNING_DATE <= d < HORIZON_END


def round10(x: float) -> int:
    return int(round(x / 10.0)) * 10


def haversine_km(a, b) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def make_orders(rng):
    wh_ids = [w[0] for w in WAREHOUSES]
    weights = np.array([w[5] for w in WAREHOUSES])
    weights = weights / weights.sum()
    sku_ids = [s[0] for s in SKUS]
    priorities = [p[0] for p in PRIORITY_RULES]

    rows = []
    for qty, offset, prio in DEMO_ORDERS:
        rows.append((DEMO_SKU, DEMO_WH, qty, PLANNING_DATE + timedelta(days=offset), prio))

    while len(rows) < len(DEMO_ORDERS) + N_RANDOM_ORDERS:
        wh = wh_ids[rng.choice(len(wh_ids), p=weights)]
        sku = sku_ids[rng.integers(len(sku_ids))]
        qty = int(rng.integers(2, 16)) * 10
        due = PLANNING_DATE + timedelta(days=int(rng.integers(0, 6)))
        prio = priorities[rng.choice(len(priorities), p=PRIORITY_MIX)]
        if (wh, sku) == (DEMO_WH, DEMO_SKU):
            continue  # keep the demo cell exactly as hand-crafted
        rows.append((sku, wh, qty, due, prio))

    rows.sort(key=lambda r: (r[3], r[1], r[0]))  # stable sort: deterministic order
    return pd.DataFrame(
        [(f"O{i:03d}", *r) for i, r in enumerate(rows, start=1)],
        columns=["order_id", "sku_id", "warehouse_id", "quantity", "due_date", "priority"],
    )


def make_purchase_orders(rng):
    wh_ids = [w[0] for w in WAREHOUSES]
    sku_ids = [s[0] for s in SKUS]
    statuses = ["CONFIRMED", "DELAYED", "CANCELLED", "RECEIVED"]
    po_numbers = [n for n in range(1001, 1001 + N_RANDOM_POS + 1) if n != 1024]

    rows = [DEMO_PO]
    for n in po_numbers:
        wh = wh_ids[rng.integers(len(wh_ids))]
        sku = sku_ids[rng.integers(len(sku_ids))]
        if (wh, sku) == (DEMO_WH, DEMO_SKU):
            sku = "SKU-B"  # no other inbound to the demo cell
        qty = int(rng.integers(10, 41)) * 10
        status = statuses[rng.choice(len(statuses), p=[0.7, 0.1, 0.1, 0.1])]
        if status == "RECEIVED":
            arrival = PLANNING_DATE - timedelta(days=int(rng.integers(1, 4)))
        elif status == "DELAYED":
            arrival = HORIZON_END + timedelta(days=int(rng.integers(1, 5)))
        else:
            arrival = PLANNING_DATE + timedelta(days=int(rng.integers(0, 8)))
        supplier = f"SUP-{int(rng.integers(1, 6)):02d}"
        rows.append((f"PO-{n}", supplier, sku, wh, qty, arrival, status))

    rows.sort(key=lambda r: r[0])
    return pd.DataFrame(
        rows,
        columns=["po_id", "supplier_id", "sku_id", "warehouse_id", "quantity", "expected_arrival", "status"],
    )


def horizon_demand(orders):
    df = orders[orders["due_date"].map(in_horizon)]
    return df.groupby(["warehouse_id", "sku_id"])["quantity"].sum().to_dict()


def horizon_inbound(pos):
    df = pos[(pos["status"] == "CONFIRMED") & pos["expected_arrival"].map(in_horizon)]
    return df.groupby(["warehouse_id", "sku_id"])["quantity"].sum().to_dict()


def make_inventory(rng, demand, inbound):
    """On-hand stock sized so that most cells are roughly covered before the disruption.

    SKU-A is over-stocked outside Shanghai so the demo shortage can be fixed by transfers.
    """
    rows = []
    for wh, *_ in WAREHOUSES:
        for sku, _ in SKUS:
            # Always draw the same number of random values per cell, so changing
            # one cell's rule never shifts the random stream of the others.
            coverage = rng.uniform(0.85, 1.35)
            surplus_coverage = rng.uniform(1.6, 2.2)
            idle_stock = int(rng.integers(0, 11)) * 10

            d = demand.get((wh, sku), 0)
            if (wh, sku) == (DEMO_WH, DEMO_SKU):
                on_hand = DEMO_ON_HAND
            elif d == 0:
                on_hand = idle_stock
            else:
                factor = surplus_coverage if sku == DEMO_SKU else coverage
                on_hand = max(0, round10(d * factor - inbound.get((wh, sku), 0)))
            if sku == DEMO_SKU and wh != DEMO_WH:
                on_hand += 100  # base safety stock of the demo SKU
            rows.append((wh, sku, on_hand))
    return pd.DataFrame(rows, columns=["warehouse_id", "sku_id", "on_hand"])


def make_lanes(rng):
    coords = {w[0]: (w[3], w[4]) for w in WAREHOUSES}
    ids = [w[0] for w in WAREHOUSES]

    pairs = set()
    for a in ids:
        nearest = sorted((b for b in ids if b != a), key=lambda b: haversine_km(coords[a], coords[b]))
        for b in nearest[:NEAREST_NEIGHBORS]:
            pairs.add((a, b))
            pairs.add((b, a))
    for a, b in TRUNK_LANES:
        pairs.add((a, b))
        pairs.add((b, a))

    rows = []
    # A set has no stable iteration order across runs: always sort before using it.
    for a, b in sorted(pairs):
        km = haversine_km(coords[a], coords[b])
        capacity = int(rng.choice([200, 300, 400, 500]))
        rows.append((a, b, round(0.5 + km / 400, 2), int(round(100 + 0.2 * km)), capacity))
    return pd.DataFrame(rows, columns=["from_warehouse_id", "to_warehouse_id", "unit_cost", "fixed_cost", "capacity"])


def make_expedite(rng):
    rows = []
    for wh, *_ in WAREHOUSES:
        for sku, _ in SKUS:
            offered = rng.random() < EXPEDITE_SHARE
            unit_cost = round(float(rng.uniform(18, 35)), 2)
            capacity = int(rng.integers(5, 16)) * 10
            if (wh, sku) == (DEMO_WH, DEMO_SKU):
                rows.append((wh, sku, 25.0, 100))
            elif offered:
                rows.append((wh, sku, unit_cost, capacity))
    return pd.DataFrame(rows, columns=["warehouse_id", "sku_id", "unit_cost", "capacity"])


def write_csv(df, name):
    # lineterminator="\n": identical bytes on Windows and Linux (pandas defaults to os.linesep).
    df.to_csv(DATA_DIR / name, index=False, lineterminator="\n", float_format="%.2f")


def write_scenario():
    scenario = {
        "scenario_id": "supplier_delay_po1024",
        "planning_date": PLANNING_DATE.isoformat(),
        "horizon_days": HORIZON_DAYS,
        "disruption": {"type": "SUPPLIER_DELAY", "po_id": "PO-1024", "delay_days": 4},
    }
    SCENARIO_DIR.mkdir(exist_ok=True)
    with open(SCENARIO_DIR / "supplier_delay_po1024.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(scenario, f, indent=2)
        f.write("\n")


def print_summary(orders, pos, inventory, lanes, expedite):
    demand = horizon_demand(orders)
    inbound = horizon_inbound(pos)
    on_hand = {(r.warehouse_id, r.sku_id): r.on_hand for r in inventory.itertuples()}
    demo_po_qty = DEMO_PO[4]

    def available(cell, delayed):
        extra = inbound.get(cell, 0)
        if delayed and cell == (DEMO_WH, DEMO_SKU):
            extra -= demo_po_qty
        return on_hand.get(cell, 0) + extra

    print(f"Horizon: {PLANNING_DATE} .. {HORIZON_END - timedelta(days=1)} ({HORIZON_DAYS} days)")
    print(
        f"Rows: orders={len(orders)} (in horizon {orders['due_date'].map(in_horizon).sum()}), "
        f"POs={len(pos)}, lanes={len(lanes)}, expedite options={len(expedite)}"
    )
    print("Order priorities:", orders["priority"].value_counts().to_dict())
    print("PO statuses:", pos["status"].value_counts().to_dict())

    cells = [(w[0], s[0]) for w in WAREHOUSES for s in SKUS]
    short = {c: demand.get(c, 0) - available(c, False) for c in cells}
    short = {c: v for c, v in short.items() if v > 0}
    print(f"\nBefore disruption: {len(short)} local shortage cells, total {sum(short.values())} units")

    print("\nPer SKU (system-wide):  demand | available before | available after")
    for sku, _ in SKUS:
        d = sum(demand.get((w[0], sku), 0) for w in WAREHOUSES)
        before = sum(available((w[0], sku), False) for w in WAREHOUSES)
        after = sum(available((w[0], sku), True) for w in WAREHOUSES)
        print(f"  {sku}: {d:5d} | {before:5d} | {after:5d}")

    cell = (DEMO_WH, DEMO_SKU)
    d = demand.get(cell, 0)
    print(f"\nDemo cell {DEMO_WH} / {DEMO_SKU}:")
    print(f"  on hand {on_hand[cell]}, inbound in horizon {inbound.get(cell, 0)}, demand in horizon {d}")
    print(f"  gap before disruption: {max(0, d - available(cell, False))}")
    print(f"  gap after PO-1024 delay: {max(0, d - available(cell, True))}")

    print(f"  SKU-A surplus at warehouses with a lane into {DEMO_WH}:")
    into = lanes[lanes["to_warehouse_id"] == DEMO_WH]
    for r in into.itertuples():
        src = (r.from_warehouse_id, DEMO_SKU)
        surplus = available(src, True) - demand.get(src, 0)
        print(f"    {r.from_warehouse_id}: surplus {surplus:4d}, lane capacity {r.capacity}, unit cost {r.unit_cost}")


def main():
    rng = np.random.default_rng(SEED)

    orders = make_orders(rng)
    pos = make_purchase_orders(rng)
    inventory = make_inventory(rng, horizon_demand(orders), horizon_inbound(pos))
    lanes = make_lanes(rng)
    expedite = make_expedite(rng)

    write_csv(pd.DataFrame([w[:3] for w in WAREHOUSES], columns=["warehouse_id", "warehouse_name", "region"]), "warehouses.csv")
    write_csv(pd.DataFrame(SKUS, columns=["sku_id", "sku_name"]), "skus.csv")
    write_csv(inventory, "inventory.csv")
    write_csv(orders, "orders.csv")
    write_csv(
        pd.DataFrame(
            [(p, pen, str(allow).lower()) for p, pen, allow in PRIORITY_RULES],
            columns=["priority", "delay_penalty", "allow_delay"],
        ),
        "priority_rules.csv",
    )
    write_csv(pos, "purchase_orders.csv")
    write_csv(lanes, "transfer_lanes.csv")
    write_csv(expedite, "expedite_options.csv")
    write_scenario()

    print_summary(orders, pos, inventory, lanes, expedite)


if __name__ == "__main__":
    main()
