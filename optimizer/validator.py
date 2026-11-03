"""Independent plan checker (OPT_MODEL 第 13 节).

Works on a Solution from ANY source (MIP / heuristic / fallback / LLM-edited) and
recomputes everything from Problem alone. Deliberately imports nothing from
solver.py or heuristic.py: a checker that shares code with what it checks would
share its bugs too.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from optimizer.models import Problem, Solution

COST_TOLERANCE = 1e-6


@dataclass(frozen=True)
class Violation:
    check: str   # Integrality / Demand / Inventory / Lane / Expedite / VIP SLA / Cost
    target: str  # 哪个对象，例如 "WH-SH/SKU-A"、"O017"
    detail: str  # 差多少


@dataclass(frozen=True)
class ValidationResult:
    violations: List[Violation] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.violations


def validate(problem: Problem, solution: Solution) -> ValidationResult:
    v: List[Violation] = []

    def bad(check: str, target: str, detail: str) -> None:
        v.append(Violation(check, target, detail))

    orders = {o.order_id: o for o in problem.orders}
    rules = {r.priority: r for r in problem.priority_rules}
    lanes = {(l.from_warehouse_id, l.to_warehouse_id): l for l in problem.transfer_lanes}
    exp_opts = {(e.warehouse_id, e.sku_id): e for e in problem.expedite_options}

    # ---------- Integrality ----------
    quantities = (
        [(f"{t.from_warehouse_id}->{t.to_warehouse_id}/{t.sku_id}", t.quantity) for t in solution.transfers]
        + [(f"{e.warehouse_id}/{e.sku_id}", e.quantity) for e in solution.expedites]
        + [(d.order_id, d.quantity) for d in solution.delayed_orders]
    )
    for target, q in quantities:
        # bool 是 int 的子类（True == 1），要单独排除
        if not isinstance(q, int) or isinstance(q, bool) or q < 0:
            bad("Integrality", target, f"quantity {q!r} is not a non-negative integer")

    # ---------- Demand: 0 <= u_o <= D_o ----------
    delayed: Dict[str, int] = defaultdict(int)
    for d in solution.delayed_orders:
        if d.order_id not in orders:
            bad("Demand", d.order_id, "unknown order")
            continue
        delayed[d.order_id] += d.quantity
    for oid, u in delayed.items():
        if u > orders[oid].quantity:
            bad("Demand", oid, f"delayed {u} > ordered {orders[oid].quantity}")

    # ---------- VIP SLA ----------
    for oid, u in delayed.items():
        rule = rules.get(orders[oid].priority)
        if rule is not None and not rule.allow_delay and u > 0:
            bad("VIP SLA", oid, f"{orders[oid].priority} order delayed by {u}")

    # ---------- Lane ----------
    lane_load: Dict[Tuple[str, str], int] = defaultdict(int)
    for t in solution.transfers:
        key = (t.from_warehouse_id, t.to_warehouse_id)
        if key not in lanes:
            bad("Lane", f"{key[0]}->{key[1]}", "lane does not exist")
            continue
        lane_load[key] += t.quantity
    for key, load in lane_load.items():
        if load > lanes[key].capacity:
            bad("Lane", f"{key[0]}->{key[1]}", f"load {load} > capacity {lanes[key].capacity}")

    # ---------- Expedite ----------
    exp_qty: Dict[Tuple[str, str], int] = defaultdict(int)
    for e in solution.expedites:
        exp_qty[e.warehouse_id, e.sku_id] += e.quantity
    for key, q in exp_qty.items():
        cap = exp_opts[key].capacity if key in exp_opts else 0
        if q > cap:
            bad("Expedite", f"{key[0]}/{key[1]}", f"expedite {q} > capacity {cap}")

    # ---------- Inventory: shipped + out <= stock + in + expedite ----------
    balance: Dict[Tuple[str, str], int] = defaultdict(int)  # 可用 - 使用，必须 >= 0
    for i in problem.inventory:
        balance[i.warehouse_id, i.sku_id] += i.available
    for o in problem.orders:
        balance[o.warehouse_id, o.sku_id] -= o.quantity - delayed.get(o.order_id, 0)
    for t in solution.transfers:
        balance[t.from_warehouse_id, t.sku_id] -= t.quantity
        balance[t.to_warehouse_id, t.sku_id] += t.quantity
    for key, q in exp_qty.items():
        balance[key] += q
    for (w, s), b in sorted(balance.items()):
        if b < 0:
            bad("Inventory", f"{w}/{s}", f"short by {-b}")

    # ---------- Cost ----------
    if solution.cost_breakdown is not None and not any(x.check in ("Demand", "Lane") for x in v):
        priority_of = {oid: orders[oid].priority for oid in delayed}
        expected = {
            "transfer": sum(lanes[k].unit_cost * q for k, q in lane_load.items()),
            "lane": sum(lanes[k].fixed_cost for k, q in lane_load.items() if q > 0),
            "expedite": sum(exp_opts[k].unit_cost * q for k, q in exp_qty.items() if k in exp_opts),
            "delay": sum(rules[priority_of[oid]].delay_penalty * u for oid, u in delayed.items()),
        }
        for name, value in expected.items():
            reported = getattr(solution.cost_breakdown, name)
            if abs(reported - value) > COST_TOLERANCE * max(1.0, abs(value)):
                bad("Cost", name, f"reported {reported:.4f}, recomputed {value:.4f}")

    return ValidationResult(v)
