# SupplyOps Copilot — Optimization Model Design

> 本文件定义 SupplyOps 的 OR 模型、数据表与接口约定。
> 课程安排见 `STUDY_PLAN.md`，进度见 `COURSE_STATE.md`。

## 1. 模型目标

SupplyOps Copilot 处理的是**供应链异常发生后的订单履约恢复问题**。

典型异常：

- 供应商延期（Supplier Delay）
- 实际库存低于系统库存（Inventory Discrepancy）
- VIP 紧急插单（Urgent VIP Order）
- 调拨通道能力下降（Lane Capacity Reduction）

系统需要回答：

> 异常发生以后，是否需要跨区调拨？从哪里调、调多少？
> 是否需要紧急采购？
> 哪些订单必须保证按时交付？
> 如果无法全部满足，哪些订单延期、延期多少？

目标是在满足业务约束的前提下，最小化异常恢复的总成本。

这个模型**不是课程重点**：它要求有一定结构（整数变量 + 固定成本 + 网络耦合），但必须能用 OR-Tools 在秒级求解，从而可以作为一个可靠的 Agent 工具被调用。

---

# 2. MVP 范围

| 维度 | 规模 |
| ---- | ---- |
| 区域仓 | 10 个 |
| SKU | 10 个 |
| 客户订单 | 约 150 个（规划期内到期） |
| 调拨通道 | 约 30–40 条有向通道（不是完全图） |
| 采购单 | 约 20–30 个在途 PO |

10 个区域仓：

```text
WH-SH  Shanghai      WH-BJ  Beijing       WH-GZ  Guangzhou
WH-SZ  Shenzhen      WH-CD  Chengdu       WH-WH  Wuhan
WH-XA  Xi'an         WH-SY  Shenyang      WH-HZ  Hangzhou
WH-ZZ  Zhengzhou
```

10 个 SKU：`SKU-A` … `SKU-J`。

所有异常**只改变输入数据，不改变模型结构**。

---

# 3. 关键建模假设

为了保持模型简单、可解释、可快速求解，MVP 采用以下假设：

1. **区域履约**：每个订单只能由其所在区域的仓库发货。跨区供给只能通过**仓间调拨**实现。
   因此本地配送成本是常数，不进入目标函数。
2. **单期模型**：只考虑一个规划期（例如未来 3 天，`horizon_days = 3`）。
   - 规划期内到期的订单进入模型；
   - 规划期内能到货的 PO 计入可用库存；
   - 调拨在规划期内到达（不建模具体运输时间）。
3. **延期 = 规划期内未满足**：不区分延期天数，只计延期数量。
4. **调拨通道有固定成本**：启用一条通道（派一辆车）产生固定成本，通道能力在所有 SKU 之间共享。
5. **所有数量为整数**。

---

# 4. Sets

| 符号 | 含义 |
| ---- | ---- |
| $W$ | 仓库集合 |
| $S$ | SKU 集合 |
| $O$ | 规划期内到期的订单集合 |
| $L \subseteq W \times W$ | 可用调拨通道集合（有向） |

每个订单 $o$ 有：

- SKU $s(o)$
- 履约仓 $w(o)$
- 优先级 $\text{prio}(o) \in \{\text{VIP}, \text{HIGH}, \text{NORMAL}, \text{LOW}\}$

记 $O_{ws} = \{o \in O : w(o)=w,\ s(o)=s\}$。

---

# 5. Parameters

| 符号 | 含义 | 来源 |
| ---- | ---- | ---- |
| $I_{ws}$ | 仓 $w$ 在规划期内可用的 SKU $s$ 库存 | `inventory.csv` + 规划期内到货的 `purchase_orders.csv` |
| $D_o$ | 订单 $o$ 的需求量 | `orders.csv` |
| $c_{l}$ | 通道 $l$ 的单位调拨成本 | `transfer_lanes.csv` |
| $f_{l}$ | 通道 $l$ 的固定启用成本 | `transfer_lanes.csv` |
| $Cap_{l}$ | 通道 $l$ 的总能力（所有 SKU 合计） | `transfer_lanes.csv` |
| $c^{exp}_{ws}$ | 仓 $w$ 紧急采购 SKU $s$ 的单位成本 | `expedite_options.csv` |
| $E_{ws}$ | 仓 $w$ 紧急采购 SKU $s$ 的上限 | `expedite_options.csv` |
| $p_o$ | 订单 $o$ 每延期一件的惩罚 | `priority_rules.csv`（按优先级） |

可用库存：

$$
I_{ws} = \text{on\_hand}_{ws} + \sum_{\text{PO} \to (w,s),\ \text{arrival} \le \text{horizon end},\ \text{status}=\text{CONFIRMED}} \text{qty}_{\text{PO}}
$$

延期惩罚默认值（业务规则，可调整）：

| priority | delay_penalty | allow_delay |
| -------- | ------------: | ----------- |
| VIP      | 100 | false |
| HIGH     |  50 | true  |
| NORMAL   |  10 | true  |
| LOW      |   5 | true  |

---

# 6. Decision Variables

| 变量 | 类型 | 含义 |
| ---- | ---- | ---- |
| $y_{ls} \ge 0$ | 整数 | 通道 $l$ 上调拨 SKU $s$ 的数量 |
| $z_{l} \in \{0,1\}$ | 二元 | 是否启用通道 $l$ |
| $e_{ws} \ge 0$ | 整数 | 仓 $w$ 紧急采购 SKU $s$ 的数量 |
| $u_{o} \ge 0$ | 整数 | 订单 $o$ 延期的数量 |

订单 $o$ 按时满足的数量为 $D_o - u_o$，不需要单独的 allocation 变量（由区域履约假设保证）。

对通道 $l = (w, w')$，记 $\delta^{out}(w)$ 为从 $w$ 出发的通道，$\delta^{in}(w)$ 为到达 $w$ 的通道。

---

# 7. Objective Function

$$
\min\quad
\underbrace{\sum_{l \in L}\sum_{s \in S} c_{l}\, y_{ls}}_{C_{transfer}}
+
\underbrace{\sum_{l \in L} f_{l}\, z_{l}}_{C_{lane}}
+
\underbrace{\sum_{w \in W}\sum_{s \in S} c^{exp}_{ws}\, e_{ws}}_{C_{expedite}}
+
\underbrace{\sum_{o \in O} p_{o}\, u_{o}}_{C_{delay}}
$$

---

# 8. Constraints

## 8.1 Demand

$$
0 \le u_o \le D_o \qquad \forall o \in O
$$

## 8.2 Inventory Balance

每个仓、每个 SKU：出库（本地发货 + 调出）不超过可用量（库存 + 调入 + 紧急采购）。

$$
\sum_{o \in O_{ws}} (D_o - u_o)
+ \sum_{l \in \delta^{out}(w)} y_{ls}
\le
I_{ws}
+ \sum_{l \in \delta^{in}(w)} y_{ls}
+ e_{ws}
\qquad \forall w \in W,\ s \in S
$$

## 8.3 Lane Capacity & Activation

$$
\sum_{s \in S} y_{ls} \le Cap_{l}\, z_{l}
\qquad \forall l \in L
$$

## 8.4 Expedite Capacity

$$
e_{ws} \le E_{ws}
\qquad \forall w \in W,\ s \in S
$$

（`expedite_options.csv` 中没有的 $(w,s)$ 组合，$E_{ws}=0$。）

## 8.5 VIP SLA

$$
u_o = 0 \qquad \forall o : \text{allow\_delay}(\text{prio}(o)) = \text{false}
$$

这是硬约束。如果无法满足，模型返回 `INFEASIBLE`，由 Agent 上报人工处理，**不能**让 LLM 自行编一个方案。

---

# 9. 模型规模与求解

以 10 仓 × 10 SKU × 40 通道 × 150 订单估算：

| 变量 | 数量 |
| ---- | ---: |
| $y_{ls}$ | 400 |
| $z_l$ | 40 |
| $e_{ws}$ | ≤ 100 |
| $u_o$ | 150 |

约 700 个整数变量、约 250 条约束，属于小规模 MIP（固定费用网络流），OR-Tools 秒级求解。

求解器：OR-Tools（`pywraplp` + SCIP，或 CP-SAT，Lesson 1 中选定）。

求解时间上限通过参数 `time_limit_seconds` 控制（服务化后由环境变量 `SOLVER_TIME_LIMIT` 提供）。

---

# 10. 数据设计

## 10.1 命名规范

- 文件名、列名统一使用 `snake_case`
- 主键 / 外键统一以 `_id` 结尾：`warehouse_id`、`sku_id`、`order_id`、`po_id`
- 上限统一叫 `capacity`，单位成本叫 `unit_cost`，固定成本叫 `fixed_cost`
- 日期统一使用 ISO 格式：`2026-11-05`
- 枚举值统一大写：`VIP`、`CONFIRMED`

## 10.2 数据文件

所有基础数据放在 `data/`，异常场景放在 `data/scenarios/`。

### warehouses.csv

```text
warehouse_id,warehouse_name,region
WH-SH,Shanghai,East
WH-BJ,Beijing,North
```

### skus.csv

```text
sku_id,sku_name
SKU-A,Industrial Pump
```

### inventory.csv

```text
warehouse_id,sku_id,on_hand
WH-SH,SKU-A,160
WH-BJ,SKU-A,400
```

### orders.csv

```text
order_id,sku_id,warehouse_id,quantity,due_date,priority
O001,SKU-A,WH-SH,80,2026-11-05,VIP
O002,SKU-A,WH-SH,120,2026-11-05,HIGH
```

`warehouse_id` 为订单的区域履约仓。

### priority_rules.csv

```text
priority,delay_penalty,allow_delay
VIP,100,false
HIGH,50,true
NORMAL,10,true
LOW,5,true
```

这是 **Business Rules** 的第一个载体：延期惩罚和 SLA 由规则表决定，而不是写死在代码里。

### purchase_orders.csv

```text
po_id,supplier_id,sku_id,warehouse_id,quantity,expected_arrival,status
PO-1024,SUP-01,SKU-A,WH-SH,500,2026-11-02,CONFIRMED
```

`status`：`CONFIRMED` / `DELAYED` / `CANCELLED` / `RECEIVED`。

### transfer_lanes.csv

```text
from_warehouse_id,to_warehouse_id,unit_cost,fixed_cost,capacity
WH-BJ,WH-SH,2.0,300,400
WH-HZ,WH-SH,1.0,150,200
```

### expedite_options.csv

```text
warehouse_id,sku_id,unit_cost,capacity
WH-SH,SKU-A,25.0,100
```

### scenarios/*.json

描述一次异常相对于基础数据的变化，例如：

```json
{
  "scenario_id": "supplier_delay_po1024",
  "planning_date": "2026-11-01",
  "horizon_days": 3,
  "disruption": {
    "type": "SUPPLIER_DELAY",
    "po_id": "PO-1024",
    "delay_days": 4
  }
}
```

场景文件同时用于 Demo 和 Lesson 11 的批量评估。

---

# 11. 异常如何进入模型

| 异常类型 | 对输入数据的改变 |
| -------- | ---------------- |
| `SUPPLIER_DELAY` | PO 的 `expected_arrival` 推后；若超出规划期，则不再计入 $I_{ws}$ |
| `INVENTORY_DISCREPANCY` | 修改对应 `on_hand` |
| `URGENT_ORDER` | 在 $O$ 中新增一个订单（通常为 VIP） |
| `LANE_CAPACITY_REDUCTION` | 降低对应通道的 $Cap_l$ |

示例：PO-1024（500 件 SKU-A → WH-SH）原定 11-02 到货，延期 4 天，变为 11-06，超出 11-01 起 3 天的规划期。

```text
WH-SH SKU-A 可用库存：160 + 500 = 660  →  160
WH-SH SKU-A 规划期内需求：420
潜在缺口：260
```

模型在以下选项中权衡：从 WH-BJ / WH-HZ 调拨（单位成本 + 通道固定成本）、在 WH-SH 紧急采购、延期低优先级订单。

---

# 12. Baselines

## Baseline 1 — Do Nothing

不调拨、不紧急采购。每个仓按优先级（VIP → LOW）依次用本地库存满足订单，剩余全部延期。

## Baseline 2 — Rule-Based Recovery

```text
1. 按优先级排序订单（同优先级按 due_date）
2. 优先使用本地库存
3. 不足时，从单位调拨成本最低、且有富余库存的相邻仓调拨
   （富余 = 该仓库存 - 该仓自身订单需求，不能挖空别人的需求）
4. 仍不足时，在本地紧急采购（若有选项）
5. 仍不足时，延期
```

Rule-Based Recovery 同时作为 **Solver 失败时的 Fallback Heuristic**（见第 15 节）。

## 比较指标

```text
total_cost（及 4 项成本拆分）
delayed_quantity
vip_violations
transfer_quantity / lanes_used
expedite_quantity
solve_time
```

结果只能表述为 synthetic evaluation：

> Under synthetic disruption scenarios, the optimization-based recovery policy reduced simulated recovery cost relative to rule-based baselines.

---

# 13. Validator

Validator 独立于 Solver 和 LLM，对**任何来源**的方案（Optimizer / Baseline / Fallback）执行同一套检查：

| 检查 | 内容 |
| ---- | ---- |
| Integrality | 所有数量为非负整数 |
| Demand | $0 \le u_o \le D_o$ |
| Inventory | 每个 $(w,s)$ 平衡约束成立，不出现负库存 |
| Lane | 只使用 $L$ 中存在的通道；$\sum_s y_{ls} \le Cap_l$ |
| Expedite | $e_{ws} \le E_{ws}$ |
| VIP SLA | `allow_delay = false` 的订单 $u_o = 0$ |
| Cost | 重新计算 4 项成本，与方案中报告的成本一致 |

输出：`is_valid` + 违反项列表（哪条约束、哪个对象、差多少）。

---

# 14. Solver Status

Optimizer 必须返回明确的状态：

| status | 含义 | 后续处理 |
| ------ | ---- | -------- |
| `OPTIMAL` | 找到最优解 | Validator → Human Approval |
| `FEASIBLE` | 超时但有可行解 | Validator → Human Approval（标注非最优） |
| `INFEASIBLE` | 约束无法同时满足（通常是 VIP SLA） | 上报人工 |
| `TIMEOUT` | 超时且无可行解 | Fallback Heuristic |
| `ERROR` | 输入错误或求解器异常 | Fallback Heuristic / 报错 |

禁止的处理方式：

```text
Solver timeout → LLM 编一个答案
```

---

# 15. Fallback

```text
Optimizer TIMEOUT / ERROR
        ↓
Rule-Based Recovery（第 12 节 Baseline 2）
        ↓
Validator
        ↓
Human Approval（标注 "fallback plan"）
```

重点不是 heuristic 有多好，而是：

> Optimization Service 失败时，系统仍能返回一个**经过验证的可行方案**。

---

# 16. LLM 与 Optimization 的边界

LLM 负责：

```text
发生了什么异常？（解析非结构化消息）
需要查询哪些数据？
是否需要触发 optimizer？
如何向业务人员解释方案？
```

LLM 不负责：

```text
调拨多少、从哪调？
哪些订单延期？
成本是多少？
```

这些只能来自 Optimizer / Heuristic 的输出，并经过 Validator 检查。

---

# 17. API Interface

`POST /optimize`

请求：

```json
{
  "horizon_days": 3,
  "time_limit_seconds": 10,
  "inventory": [{"warehouse_id": "WH-SH", "sku_id": "SKU-A", "available": 160}],
  "orders": [{"order_id": "O001", "sku_id": "SKU-A", "warehouse_id": "WH-SH", "quantity": 80, "priority": "VIP"}],
  "priority_rules": [{"priority": "VIP", "delay_penalty": 100, "allow_delay": false}],
  "transfer_lanes": [{"from_warehouse_id": "WH-BJ", "to_warehouse_id": "WH-SH", "unit_cost": 2.0, "fixed_cost": 300, "capacity": 400}],
  "expedite_options": [{"warehouse_id": "WH-SH", "sku_id": "SKU-A", "unit_cost": 25.0, "capacity": 100}]
}
```

注意：`inventory.available` 是已经计入规划期内 PO 到货后的可用量，由调用方（Agent / ERP）计算，Optimizer 不关心 PO。

响应：

```json
{
  "status": "OPTIMAL",
  "method": "MIP",
  "objective": 1842.0,
  "cost_breakdown": {"transfer": 480.0, "lane": 450.0, "expedite": 0.0, "delay": 912.0},
  "transfers": [{"from_warehouse_id": "WH-BJ", "to_warehouse_id": "WH-SH", "sku_id": "SKU-A", "quantity": 180}],
  "expedites": [],
  "delayed_orders": [{"order_id": "O003", "quantity": 20}],
  "solve_time_seconds": 0.42
}
```

`method`：`MIP` / `HEURISTIC`。具体字段在 Lesson 4 中用 Pydantic schema 固定下来。

---

# 18. MVP 完成标准

- [ ] 可以读取 `data/` 下全部 CSV 并做基本校验
- [ ] 可以加载 scenario 并生成模型输入
- [ ] 10 仓 × 10 SKU × ~150 订单可在 10 秒内求解
- [ ] 决策包含调拨（含通道启用）、紧急采购、延期
- [ ] VIP SLA 被强制执行，不可行时返回 `INFEASIBLE`
- [ ] 正确返回全部 5 种 Solver 状态
- [ ] Validator 可独立检查任何来源的方案
- [ ] 有 Do Nothing 与 Rule-Based 两个 baseline
- [ ] pytest 覆盖 Validator 与至少一个手算小算例
- [ ] 至少一个 supplier delay demo

---

# 19. 非目标

MVP 不考虑：车辆路径、精确运输时间、多期库存、需求预测、随机 / 鲁棒优化、生产调度、供应商选择、多目标优化。

未来扩展（Phase 2）：多期 + 调拨 lead time、Rolling Horizon（observe → optimize → execute → re-optimize）、更多异常类型。

---

# 20. Design Principle

$$
\text{LLM for Judgment} + \text{OR for Decisions} + \text{Software for Reliability}
$$

项目要证明的不是“我会调用一个大模型”，而是：

> 我能够把大模型、运筹优化和工程系统组合起来，解决一个真实的企业决策问题。
