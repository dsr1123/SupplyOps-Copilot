import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

from optimizer.models import (
    ExpediteOption,
    InventoryItem,
    Order,
    PriorityRule,
    Problem,
    TransferLane,
)


class DataValidationError(Exception):
    """Input data is invalid."""


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    planning_date: date
    horizon_days: int
    disruption: dict


# 每个表需要哪些列。表名同时也是文件名（加 .csv）
REQUIRED_COLUMNS = {
    "warehouses": ["warehouse_id", "warehouse_name", "region"],
    "skus": ["sku_id", "sku_name"],
    "inventory": ["warehouse_id", "sku_id", "on_hand"],
    "orders": ["order_id", "sku_id", "warehouse_id", "quantity", "due_date", "priority"],
    "priority_rules": ["priority", "delay_penalty", "allow_delay"],
    "purchase_orders": ["po_id", "supplier_id", "sku_id", "warehouse_id", "quantity", "expected_arrival", "status"],
    "transfer_lanes": ["from_warehouse_id", "to_warehouse_id", "unit_cost", "fixed_cost", "capacity"],
    "expedite_options": ["warehouse_id", "sku_id", "unit_cost", "capacity"],
}

PRIORITIES = {"VIP", "HIGH", "NORMAL", "LOW"}
PO_STATUSES = {"CONFIRMED", "DELAYED", "CANCELLED", "RECEIVED"}


def load_tables(data_dir: Path) -> Dict[str, pd.DataFrame]:
    # dtype=str：所有列都按字符串读入，关闭 pandas 的自动推断。
    # 类型转换由我们在 build_problem 中显式完成。
    return {name: pd.read_csv(data_dir / f"{name}.csv", dtype=str) for name in REQUIRED_COLUMNS}


def load_scenario(path: Path) -> Scenario:
    # TODO: 用 json.load 读取文件，构造并返回 Scenario
    #       注意：planning_date 要用 date.fromisoformat() 转成日期
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Scenario(
        scenario_id=data["scenario_id"],
        planning_date=date.fromisoformat(data["planning_date"]),
        horizon_days=data["horizon_days"],
        disruption=data.get("disruption", {}),
    )


def _check_duplicates(errors: List[str], df: pd.DataFrame, table: str, key: str) -> None:
    """示范 1：主键不能重复。"""
    dup = df[df[key].duplicated()][key].tolist()
    if dup:
        errors.append(f"{table}.csv: duplicate {key}: {dup}")


def _check_references(errors: List[str], df: pd.DataFrame, table: str, column: str, valid: set) -> None:
    """示范 2：引用的对象必须存在。"""
    unknown = sorted(set(df[column]) - valid)
    if unknown:
        errors.append(f"{table}.csv: {column} has unknown values {unknown}")

def _check_non_negative(errors: List[str], df: pd.DataFrame, table: str, column: str) -> None:
    """示范 3：数量必须是非负整数。"""
    values = pd.to_numeric(df[column], errors="coerce")
    bad = df[values.isna() | (values < 0)]

    if not bad.empty:
        errors.append(f"Table {table}, column {column} contains negative or non-numeric values: {bad[column].tolist()}")

def validate_tables(tables: Dict[str, pd.DataFrame]) -> None:
    # 第 1 关：列。缺列时后续检查没有意义，立刻停下。
    errors = []
    for name, columns in REQUIRED_COLUMNS.items():
        missing = [c for c in columns if c not in tables[name].columns]
        if missing:
            errors.append(f"{name}.csv: missing columns {missing}")
    if errors:
        raise DataValidationError("\n".join(errors))

    # 第 2 关：内容。收集所有问题，最后一次性报告。
    warehouse_ids = set(tables["warehouses"]["warehouse_id"])
    sku_ids = set(tables["skus"]["sku_id"])

    _check_duplicates(errors, tables["orders"], "orders", "order_id")
    _check_references(errors, tables["orders"], "orders", "warehouse_id", warehouse_ids)
    _check_references(errors, tables["orders"], "orders", "sku_id", sku_ids)

    # TODO 1：其他表的主键重复检查（warehouses, skus, purchase_orders）
    _check_duplicates(errors, tables["warehouses"], "warehouses", "warehouse_id")
    _check_duplicates(errors, tables["skus"], "skus", "sku_id")
    _check_duplicates(errors, tables["purchase_orders"], "purchase_orders", "po_id")

    # TODO 2：其他表的引用检查（inventory, purchase_orders, transfer_lanes 的两列, expedite_options）
    _check_references(errors, tables["inventory"], "inventory", "warehouse_id", warehouse_ids)
    _check_references(errors, tables["inventory"], "inventory", "sku_id", sku_ids)
    _check_references(errors, tables["purchase_orders"], "purchase_orders", "warehouse_id", warehouse_ids)
    _check_references(errors, tables["purchase_orders"], "purchase_orders", "sku_id", sku_ids)
    _check_references(errors, tables["transfer_lanes"], "transfer_lanes", "from_warehouse_id", warehouse_ids)
    _check_references(errors, tables["transfer_lanes"], "transfer_lanes", "to_warehouse_id", warehouse_ids)
    _check_references(errors, tables["expedite_options"], "expedite_options", "warehouse_id", warehouse_ids)  
    _check_references(errors, tables["expedite_options"], "expedite_options", "sku_id", sku_ids)      
    # TODO 3：枚举值检查 —— 提示：枚举值检查和引用检查是同一个模式，可以复用 _check_references
    #         orders.priority ∈ PRIORITIES, purchase_orders.status ∈ PO_STATUSES,
    #         priority_rules.allow_delay ∈ {"true", "false"}
    _check_references(errors, tables["orders"], "orders", "priority", PRIORITIES)
    _check_references(errors, tables["purchase_orders"], "purchase_orders", "status", PO_STATUSES)
    _check_references(errors, tables["priority_rules"], "priority_rules", "allow_delay", {"true", "false"})
    # TODO 4：数量非负 —— 写一个 _check_non_negative(errors, df, table, column)
    #         提示：pd.to_numeric(df[column], errors="coerce") 会把转不成数字的值变成 NaN，
    #         所以 "非数字" 和 "负数" 可以一起检查：
    #         values = pd.to_numeric(df[column], errors="coerce")
    #         bad = df[values.isna() | (values < 0)]

    _check_non_negative(errors, tables["inventory"], "inventory", "on_hand")
    _check_non_negative(errors, tables["orders"], "orders", "quantity")
    _check_non_negative(errors, tables["purchase_orders"], "purchase_orders", "quantity")
    _check_non_negative(errors, tables["transfer_lanes"], "transfer_lanes", "unit_cost")
    _check_non_negative(errors, tables["transfer_lanes"], "transfer_lanes", "fixed_cost")
    _check_non_negative(errors, tables["transfer_lanes"], "transfer_lanes", "capacity")
    _check_non_negative(errors, tables["expedite_options"], "expedite_options", "unit_cost")
    _check_non_negative(errors, tables["expedite_options"], "expedite_options", "capacity")
    _check_non_negative(errors, tables["priority_rules"], "priority_rules", "delay_penalty")
    if errors:
        raise DataValidationError("\n".join(errors))


def apply_disruption(tables: Dict[str, pd.DataFrame], scenario: Scenario) -> Dict[str, pd.DataFrame]:
    # TODO: 只处理 SUPPLIER_DELAY，其他类型 raise NotImplementedError
    #   1. 复制：tables = {name: df.copy() for name, df in tables.items()}
    #   2. 找到 po_id 对应的那一行；如果找不到，raise DataValidationError
    #   3. 把 expected_arrival 往后推 delay_days 天，再转回字符串写回去
    tables = {name: df.copy() for name, df in tables.items()}
    if scenario.disruption.get("type") != "SUPPLIER_DELAY":
        raise NotImplementedError(f"Disruption type {scenario.disruption.get('type')} is not implemented.")
    po = tables["purchase_orders"].loc[tables["purchase_orders"]["po_id"] == scenario.disruption.get("po_id")]
    if po.empty:
        raise DataValidationError(f"Scenario references unknown po_id {scenario.disruption.get('po_id')!r}")


    tables["purchase_orders"].loc[po.index, "expected_arrival"] = (
        pd.to_datetime(tables["purchase_orders"].loc[po.index, "expected_arrival"]) + pd.Timedelta(days=scenario.disruption["delay_days"])
    ).dt.strftime("%Y-%m-%d")
    
    return tables


def build_problem(tables: Dict[str, pd.DataFrame], scenario: Scenario, time_limit_seconds: float = 10.0) -> Problem:
    horizon_end = scenario.planning_date + timedelta(days=scenario.horizon_days)

    def in_horizon(d: date) -> bool:
        # OPT_MODEL 第 3 节：左闭右开 [planning_date, planning_date + horizon_days)
        return scenario.planning_date <= d < horizon_end

    orders = [
        Order(
            order_id=row["order_id"],
            sku_id=row["sku_id"],
            warehouse_id=row["warehouse_id"],
            quantity=int(row["quantity"]),
            priority=row["priority"],
        )
        for _, row in tables["orders"].iterrows()
        if in_horizon(date.fromisoformat(row["due_date"]))
    ]

    # available[w, s] = on_hand + 规划期内到货的 CONFIRMED PO（OPT_MODEL 第 5 节）
    available: Dict[Tuple[str, str], int] = {}
    for _, row in tables["inventory"].iterrows():
        key = (row["warehouse_id"], row["sku_id"])
        available[key] = available.get(key, 0) + int(row["on_hand"])
    for _, row in tables["purchase_orders"].iterrows():
        if row["status"] == "CONFIRMED" and in_horizon(date.fromisoformat(row["expected_arrival"])):
            key = (row["warehouse_id"], row["sku_id"])
            available[key] = available.get(key, 0) + int(row["quantity"])
    inventory = [InventoryItem(warehouse_id=w, sku_id=s, available=q) for (w, s), q in sorted(available.items())]

    priority_rules = [
        PriorityRule(
            priority=row["priority"],
            delay_penalty=float(row["delay_penalty"]),
            allow_delay=row["allow_delay"] == "true",
        )
        for _, row in tables["priority_rules"].iterrows()
    ]

    transfer_lanes = [
        TransferLane(
            from_warehouse_id=row["from_warehouse_id"],
            to_warehouse_id=row["to_warehouse_id"],
            unit_cost=float(row["unit_cost"]),
            fixed_cost=float(row["fixed_cost"]),
            capacity=int(row["capacity"]),
        )
        for _, row in tables["transfer_lanes"].iterrows()
    ]

    expedite_options = [
        ExpediteOption(
            warehouse_id=row["warehouse_id"],
            sku_id=row["sku_id"],
            unit_cost=float(row["unit_cost"]),
            capacity=int(row["capacity"]),
        )
        for _, row in tables["expedite_options"].iterrows()
    ]

    return Problem(
        orders=orders,
        inventory=inventory,
        priority_rules=priority_rules,
        transfer_lanes=transfer_lanes,
        expedite_options=expedite_options,
        time_limit_seconds=time_limit_seconds,
    )


def load_problem(data_dir: Path, scenario_path: Path) -> Problem:
    tables = load_tables(data_dir)
    validate_tables(tables)
    scenario = load_scenario(scenario_path)
    tables = apply_disruption(tables, scenario)
    return build_problem(tables, scenario)
