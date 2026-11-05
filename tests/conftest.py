import pytest

from optimizer.models import (
    ExpediteOption,
    InventoryItem,
    Order,
    PriorityRule,
    Problem,
    TransferLane,
)


@pytest.fixture
def tiny_problem():
    """2 warehouses, 1 SKU. Known optimum: OPTIMAL, total cost 70."""
    return Problem(
        orders=[
            Order("O1", "SKU-X", "WH-A", 30, "VIP"),
            Order("O2", "SKU-X", "WH-B", 10, "NORMAL"),
        ],
        inventory=[
            InventoryItem("WH-A", "SKU-X", 0),
            InventoryItem("WH-B", "SKU-X", 50),
        ],
        priority_rules=[
            PriorityRule("VIP", 100, False),
            PriorityRule("NORMAL", 10, True),
        ],
        transfer_lanes=[TransferLane("WH-B", "WH-A", 2.0, 10.0, 100)],
        expedite_options=[ExpediteOption("WH-A", "SKU-X", 5.0, 100)],
    )
