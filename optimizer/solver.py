"""MIP recovery model (OPT_MODEL 第 4–8 节), solved with OR-Tools + SCIP."""

import time
from typing import Dict, Set, Tuple

from ortools.linear_solver import pywraplp

from optimizer.models import (
    CostBreakdown,
    DelayedOrder,
    Expedite,
    Problem,
    Solution,
    SolveStatus,
    Transfer,
)

METHOD = "mip"

# 求解器自己的状态码 → 我们对外承诺的 5 种状态（OPT_MODEL 第 14 节）。
# 不在表里的（UNBOUNDED / ABNORMAL / MODEL_INVALID）一律视为 ERROR。
_STATUS_MAP = {
    pywraplp.Solver.OPTIMAL: SolveStatus.OPTIMAL,
    pywraplp.Solver.FEASIBLE: SolveStatus.FEASIBLE,
    pywraplp.Solver.INFEASIBLE: SolveStatus.INFEASIBLE,
    pywraplp.Solver.NOT_SOLVED: SolveStatus.TIMEOUT,
}


def solve(problem: Problem) -> Solution:
    """Never raises: any failure is reported as Solution(status=ERROR)."""
    start = time.perf_counter()
    try:
        return _solve(problem, start)
    except Exception as exc:
        return Solution(
            status=SolveStatus.ERROR,
            method=METHOD,
            solve_time_seconds=time.perf_counter() - start,
            message=f"{type(exc).__name__}: {exc}",
        )


def _solve(problem: Problem, start: float) -> Solution:
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if solver is None:
        raise RuntimeError("SCIP backend is not available in this OR-Tools build")
    solver.SetTimeLimit(int(problem.time_limit_seconds * 1000))  # 单位是毫秒

    rules = {r.priority: r for r in problem.priority_rules}
    missing = {o.priority for o in problem.orders} - set(rules)
    if missing:
        raise ValueError(f"no priority rule for {sorted(missing)}")

    # ---------- Sets ----------
    lanes = [(l.from_warehouse_id, l.to_warehouse_id) for l in problem.transfer_lanes]
    lane_by_key = {(l.from_warehouse_id, l.to_warehouse_id): l for l in problem.transfer_lanes}
    warehouses: Set[str] = (
        {i.warehouse_id for i in problem.inventory}
        | {o.warehouse_id for o in problem.orders}
        | {w for lane in lanes for w in lane}
    )
    skus: Set[str] = {i.sku_id for i in problem.inventory} | {o.sku_id for o in problem.orders}
    stock: Dict[Tuple[str, str], int] = {(i.warehouse_id, i.sku_id): i.available for i in problem.inventory}
    expedite_cap = {(e.warehouse_id, e.sku_id): e for e in problem.expedite_options}

    # ---------- Variables ----------
    inf = solver.infinity()
    y = {(lane, s): solver.IntVar(0, inf, f"y[{lane[0]}->{lane[1]},{s}]") for lane in lanes for s in skus}
    z = {lane: solver.BoolVar(f"z[{lane[0]}->{lane[1]}]") for lane in lanes}
    # 8.4：e 的上界直接写进变量定义；没有选项的 (w,s) 不建变量，等价于 E_ws = 0
    e = {key: solver.IntVar(0, opt.capacity, f"e[{key[0]},{key[1]}]") for key, opt in expedite_cap.items()}
    # 8.1 + 8.5：u 的上界是 D_o；不允许延期的订单上界为 0
    u = {
        o.order_id: solver.IntVar(0, o.quantity if rules[o.priority].allow_delay else 0, f"u[{o.order_id}]")
        for o in problem.orders
    }

    # ---------- Constraints ----------
    # 8.2 Inventory balance
    for w in warehouses:
        for s in skus:
            shipped = [o for o in problem.orders if o.warehouse_id == w and o.sku_id == s]
            out_lanes = [lane for lane in lanes if lane[0] == w]
            in_lanes = [lane for lane in lanes if lane[1] == w]
            if not shipped and not out_lanes:
                continue  # 没有出库，约束恒成立
            solver.Add(
                sum(o.quantity - u[o.order_id] for o in shipped) + sum(y[lane, s] for lane in out_lanes)
                <= stock.get((w, s), 0) + sum(y[lane, s] for lane in in_lanes) + (e[w, s] if (w, s) in e else 0)
            )

    # 8.3 Lane capacity & activation
    for lane in lanes:
        solver.Add(sum(y[lane, s] for s in skus) <= lane_by_key[lane].capacity * z[lane])

    # ---------- Objective ----------
    transfer_cost = sum(lane_by_key[lane].unit_cost * var for (lane, _), var in y.items())
    lane_cost = sum(lane_by_key[lane].fixed_cost * var for lane, var in z.items())
    expedite_cost = sum(expedite_cap[key].unit_cost * var for key, var in e.items())
    delay_cost = sum(rules[o.priority].delay_penalty * u[o.order_id] for o in problem.orders)
    solver.Minimize(transfer_cost + lane_cost + expedite_cost + delay_cost)

    # ---------- Solve ----------
    raw_status = solver.Solve()
    status = _STATUS_MAP.get(raw_status, SolveStatus.ERROR)
    elapsed = time.perf_counter() - start

    if status not in (SolveStatus.OPTIMAL, SolveStatus.FEASIBLE):
        messages = {
            SolveStatus.INFEASIBLE: "constraints cannot all be satisfied (usually VIP SLA)",
            SolveStatus.TIMEOUT: f"no feasible solution within {problem.time_limit_seconds}s",
            SolveStatus.ERROR: f"solver returned raw status {raw_status}",
        }
        return Solution(status=status, method=METHOD, solve_time_seconds=elapsed, message=messages[status])

    # MIP 求解器内部是浮点数，整数变量可能是 79.9999999。
    # int() 是截断（→ 79），必须用 round()。
    def val(var) -> int:
        return int(round(var.solution_value()))

    transfers = [
        Transfer(from_warehouse_id=lane[0], to_warehouse_id=lane[1], sku_id=s, quantity=val(var))
        for (lane, s), var in sorted(y.items())
        if val(var) > 0
    ]
    expedites = [
        Expedite(warehouse_id=w, sku_id=s, quantity=val(var)) for (w, s), var in sorted(e.items()) if val(var) > 0
    ]
    delayed = [DelayedOrder(order_id=oid, quantity=val(var)) for oid, var in u.items() if val(var) > 0]

    # 成本用取整后的数量重新计算，保证与输出的方案一致（Validator 也会这样算）
    used_lanes = {(t.from_warehouse_id, t.to_warehouse_id) for t in transfers}
    priority_of = {o.order_id: o.priority for o in problem.orders}
    costs = CostBreakdown(
        transfer=sum(lane_by_key[t.from_warehouse_id, t.to_warehouse_id].unit_cost * t.quantity for t in transfers),
        lane=sum(lane_by_key[lane].fixed_cost for lane in used_lanes),
        expedite=sum(expedite_cap[x.warehouse_id, x.sku_id].unit_cost * x.quantity for x in expedites),
        delay=sum(rules[priority_of[d.order_id]].delay_penalty * d.quantity for d in delayed),
    )

    return Solution(
        status=status,
        method=METHOD,
        transfers=transfers,
        expedites=expedites,
        delayed_orders=delayed,
        cost_breakdown=costs,
        solve_time_seconds=elapsed,
        message=None if status is SolveStatus.OPTIMAL else "time limit reached; solution may not be optimal",
    )
