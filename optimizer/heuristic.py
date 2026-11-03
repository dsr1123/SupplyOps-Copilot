"""Baselines (OPT_MODEL 第 12 节). Rule-Based Recovery doubles as the solver fallback (第 15 节)."""

import time
from collections import defaultdict
from typing import Dict, List, Tuple

from optimizer.models import (
    CostBreakdown,
    DelayedOrder,
    Expedite,
    Order,
    Problem,
    Solution,
    SolveStatus,
    Transfer,
)

PRIORITY_RANK = {"VIP": 0, "HIGH": 1, "NORMAL": 2, "LOW": 3}


def do_nothing(problem: Problem) -> Solution:
    """No transfers, no expedites: serve local stock by priority, delay the rest."""
    return _run(problem, "do_nothing", allow_recovery=False)


def rule_based(problem: Problem) -> Solution:
    """Local stock → cheapest lane with surplus → expedite → delay."""
    return _run(problem, "rule_based", allow_recovery=True)


def _sorted_orders(problem: Problem) -> List[Order]:
    # sorted() 是稳定排序：同优先级保持原顺序，而 orders.csv 已按 due_date 排好
    return sorted(problem.orders, key=lambda o: PRIORITY_RANK[o.priority])


def _run(problem: Problem, method: str, allow_recovery: bool) -> Solution:
    start = time.perf_counter()
    stock: Dict[Tuple[str, str], int] = defaultdict(int)
    for item in problem.inventory:
        stock[item.warehouse_id, item.sku_id] += item.available

    # 每个 (w,s) 尚未处理的订单需求。从别的仓调货时只能拿"富余"：stock - pending，
    # 保证不挖空源仓自己后面的订单。
    pending: Dict[Tuple[str, str], int] = defaultdict(int)
    for o in problem.orders:
        pending[o.warehouse_id, o.sku_id] += o.quantity

    lane_left = {(l.from_warehouse_id, l.to_warehouse_id): l.capacity for l in problem.transfer_lanes}
    lanes_into: Dict[str, list] = defaultdict(list)
    for l in sorted(problem.transfer_lanes, key=lambda l: l.unit_cost):
        lanes_into[l.to_warehouse_id].append(l)
    expedite_left = {(e.warehouse_id, e.sku_id): e.capacity for e in problem.expedite_options}

    transfers: Dict[Tuple[str, str, str], int] = defaultdict(int)
    expedites: Dict[Tuple[str, str], int] = defaultdict(int)
    delayed: List[DelayedOrder] = []

    for o in _sorted_orders(problem):
        key = (o.warehouse_id, o.sku_id)
        pending[key] -= o.quantity

        # 1. 本地库存
        need = o.quantity - _take(stock, key, o.quantity)

        if allow_recovery:
            # 2. 调拨：按单位成本从低到高试每条进入本仓的通道
            for lane in lanes_into[o.warehouse_id]:
                if need == 0:
                    break
                src = (lane.from_warehouse_id, o.sku_id)
                surplus = stock[src] - pending[src]
                qty = min(need, max(surplus, 0), lane_left[lane.from_warehouse_id, lane.to_warehouse_id])
                if qty > 0:
                    stock[src] -= qty
                    lane_left[lane.from_warehouse_id, lane.to_warehouse_id] -= qty
                    transfers[lane.from_warehouse_id, lane.to_warehouse_id, o.sku_id] += qty
                    need -= qty

            # 3. 紧急采购
            qty = min(need, expedite_left.get(key, 0))
            if qty > 0:
                expedite_left[key] -= qty
                expedites[key] += qty
                need -= qty

        # 4. 延期
        if need > 0:
            delayed.append(DelayedOrder(order_id=o.order_id, quantity=need))

    transfer_list = [Transfer(f, t, s, q) for (f, t, s), q in sorted(transfers.items())]
    expedite_list = [Expedite(w, s, q) for (w, s), q in sorted(expedites.items())]
    return Solution(
        status=SolveStatus.FEASIBLE,
        method=method,
        transfers=transfer_list,
        expedites=expedite_list,
        delayed_orders=delayed,
        cost_breakdown=_costs(problem, transfer_list, expedite_list, delayed),
        solve_time_seconds=time.perf_counter() - start,
        message="heuristic plan; not optimal, VIP SLA not guaranteed",
    )


def _take(stock: Dict[Tuple[str, str], int], key: Tuple[str, str], want: int) -> int:
    got = min(want, stock[key])
    stock[key] -= got
    return got


def _costs(
    problem: Problem, transfers: List[Transfer], expedites: List[Expedite], delayed: List[DelayedOrder]
) -> CostBreakdown:
    lanes = {(l.from_warehouse_id, l.to_warehouse_id): l for l in problem.transfer_lanes}
    exp = {(e.warehouse_id, e.sku_id): e for e in problem.expedite_options}
    penalty = {r.priority: r.delay_penalty for r in problem.priority_rules}
    priority_of = {o.order_id: o.priority for o in problem.orders}
    used = {(t.from_warehouse_id, t.to_warehouse_id) for t in transfers}
    return CostBreakdown(
        transfer=sum(lanes[t.from_warehouse_id, t.to_warehouse_id].unit_cost * t.quantity for t in transfers),
        lane=sum(lanes[k].fixed_cost for k in used),
        expedite=sum(exp[x.warehouse_id, x.sku_id].unit_cost * x.quantity for x in expedites),
        delay=sum(penalty[priority_of[d.order_id]] * d.quantity for d in delayed),
    )
