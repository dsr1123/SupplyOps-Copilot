from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


@dataclass(frozen=True)
class Order:
    order_id: str
    sku_id: str
    warehouse_id: str
    quantity: int
    priority: str

@dataclass(frozen=True)
class InventoryItem:
    sku_id: str
    warehouse_id: str
    available: int

@dataclass(frozen=True)
class PriorityRule:
    priority: str
    delay_penalty: float
    allow_delay: bool
    
@dataclass(frozen=True)
class TransferLane:
    from_warehouse_id: str
    to_warehouse_id: str
    unit_cost: float
    fixed_cost: float
    capacity: int

@dataclass(frozen=True)
class ExpediteOption:
    warehouse_id: str
    sku_id: str
    unit_cost: float
    capacity: int

@dataclass(frozen=True)
class Problem:
    orders: List[Order]
    inventory_items: List[InventoryItem]
    priority_rules: List[PriorityRule]
    transfer_lanes: List[TransferLane]
    expedite_options: List[ExpediteOption]
    time_limit_seconds: Optional[float] = 10.0

class SolveStatus(Enum):
    OPTIMAL = 'OPTIMAL'
    FEASIBLE = 'FEASIBLE'
    INFEASIBLE = 'INFEASIBLE'
    TIMEOUT = 'TIMEOUT'
    ERROR = 'ERROR'
    
@dataclass(frozen=True)
class Transfer:
    from_warehouse_id: str
    to_warehouse_id: str
    sku_id: str
    quantity: int

@dataclass(frozen=True)
class Expedite:
    warehouse_id: str
    sku_id: str
    quantity: int
    
@dataclass(frozen=True)
class DelayedOrder:
    order_id: str
    quantity: int
    
@dataclass(frozen=True)
class DelayedOrder:
    order_id: str
    quantity: int

@dataclass(frozen=True)
class CostBreakdown:
    transfer: float
    expedite: float
    delay: float
    lane: float
    @property
    def total(self) -> float:
        return self.transfer + self.expedite + self.delay + self.lane

@dataclass(frozen=True)
class Solution:
    status: SolveStatus
    method: str
    transfers: List[Transfer] = field(default_factory=list)
    expedites: List[Expedite] = field(default_factory=list)
    delayed_orders: List[DelayedOrder] = field(default_factory=list)
    cost_breakdown: Optional[CostBreakdown] = None
    solver_time_seconds: Optional[float] = None
    message: Optional[str] = None