# SupplyOps Engineering Course Plan

> 本文件是课程大纲。当前进度以 `COURSE_STATE.md` 为准，OR 模型与数据规范以 `OPT_MODEL.md` 为准。

## 0. 课程总目标

通过构建一个完整的 **AI + Operations Research 企业决策系统**，学习两类能力：

1. **系统与工程基础**：Git、Linux、网络、HTTP / API、Docker、可靠性
2. **大模型落地**：LLM API、结构化输出、Tool Calling、Agent Loop、Human-in-the-Loop、评估

最终项目：**SupplyOps Copilot** —— 一个处理供应链异常的智能决策系统。

```text
供应商延期 / 库存异常 / VIP 插单
                ↓
         LLM 理解异常
                ↓
        查询企业业务数据
                ↓
       判断是否需要重新优化
                ↓
          OR 优化模型
                ↓
            Validator
                ↓
          Human Approval
                ↓
          模拟执行 / 更新
```

学习者背景：熟悉 OR 建模与数据处理。因此 OR 部分压缩为一课，重点放在**工程化**与**大模型落地**。

系统按三个阶段长出来：

```text
Part A  本地 OR 项目          数据 + 模型 + 输出（Lesson 0–1）
          ↓
Part B  搬到 Linux，变成服务  Linux → 网络 → API → Docker → ERP（Lesson 2–6）
          ↓
Part C  接入 LLM，变成 Agent  LLM → Tool Calling → 闭环 → 可靠性 → 评估（Lesson 7–11）
```

每个概念都在项目需要它的时候引入。

---

# 1. 最终系统结构

```text
                    ┌─────────────────────┐
                    │   MaaS LLM（并行）   │
                    └──────────┬──────────┘
                               │ HTTPS
                               ▼
                    ┌─────────────────────┐
                    │   SupplyOps Agent   │
                    └──────────┬──────────┘
                               │ HTTP
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
        Mock ERP         Optimization       Business Rules
         Service            Service       (priority_rules)
         (SQLite)              │
             │                 ▼
             │             OR-Tools
             └────────┬────────┘
                      ▼
                  Validator
                      ▼
                Human Approval
                      ▼
               Execute / Update
```

课程结束时要求做到：

```text
Correct + Explainable + Callable + Testable + Deployable
```

---

# 2. 运行环境

| 角色 | 环境 |
| ---- | ---- |
| 本地开发 | Windows + VS Code + Git + Python 3.9.13 |
| Linux 服务器 | 课题组服务器“思睿”，SSH 别名 `myserver` |
| LLM | 并行科技 MaaS 平台（DeepSeek / Qwen / GLM / ERNIE / Doubao / MiniMax），额度约 1000 元 |
| 代码托管 | GitHub |

安全约定：

- API Key 只放在环境变量 / `.env`（已被 `.gitignore` 忽略），不进 Git
- 服务器 IP、用户名、私钥路径不写进仓库任何文件，文档中只使用别名 `myserver`

---

# 3. 课程结构

| Lesson | 主题 | 主要成果 | 预计 |
| ------ | ---- | -------- | ---: |
| 0 | 项目、Git 与开发环境 | 仓库、虚拟环境、Git 工作流 | 2h |
| 1 | 本地 OR Engine | 数据 + 模型 + Validator + Baseline + 测试 | 4h |
| 2 | 程序、进程、Linux 与 SSH | optimizer 在 `myserver` 上运行 | 3h |
| 3 | 网络与 HTTP | 理解远程通信；第一次用 curl 调用 LLM | 3h |
| 4 | FastAPI Optimization Service | `POST /optimize`、`GET /health` | 3h |
| 5 | Docker | 容器化 Optimization Service | 3h |
| 6 | Mock ERP & Docker Compose | 两个服务协同运行 | 3h |
| 7 | LLM API 与结构化输出 | 供应商消息 → 结构化事件 | 3h |
| 8 | Tool Calling 与 Agent Loop | 手写 Agent Loop，接入 ERP / Optimizer | 4h |
| 9 | End-to-End Workflow | 异常 → 决策 → 审批 → 执行 闭环 | 3h |
| 10 | Reliability & Observability | timeout / retry / fallback / tracing | 3h |
| 11 | Evaluation, Deployment & Demo | 评估、部署、文档、Demo | 4h |
| Bonus | Kubernetes | 听懂企业 K8s 基础对话 | — |

预计总投入：约 38 小时。

## 贯穿全课程的实践

- **Git 分支工作流**：从 Lesson 1 开始，每课一个分支 `lesson-N-<topic>`，完成后提 PR 并合并到 `main`。中途专门练习一次冲突解决和 rebase。
- **测试**：从 Lesson 1 开始用 pytest，之后每课新增的模块都配测试。
- **笔记**：每课在 `notes/` 下记录一份笔记（概念 + 命令 + 踩过的坑）。

---

# Part A — 本地 OR 项目

# Lesson 0 — Project Setup, Git & Dev Environment

## 核心问题

> 一个想法如何变成一个可持续开发的软件项目？

## 本节学习

- Git：repository、working directory、staging area、commit、branch、local / remote、clone、push、pull、`.gitignore`
- 为什么 Git 不追踪空目录（`.gitkeep`）
- Python 解释器与虚拟环境：`venv`、`pip`、`requirements.txt`
- 为什么不能把密钥提交到 Git

## 本节实现

- 统一 README / STUDY_PLAN / COURSE_STATE / OPT_MODEL 四份文档
- 建立目录结构（见第 6 节），用 `.gitkeep` 让空目录进入 Git
- 使用现有 Python 3.9.13，创建 `.venv`，建立 `requirements.txt`
- 提交并推送到 GitHub
- 第一次体验分支工作流：在分支上修改，提 PR，合并

## 完成标准

能够解释 `git add`、`git commit`、`git push` 分别改变了哪里的状态（working directory / staging area / local repo / remote repo）。

---

# Lesson 1 — Local OR Engine

## 核心问题

> 如何把一个 OR 模型写成**可被其他程序调用、可测试**的软件模块，而不是一个只能自己跑的脚本？

OR 建模本身不是本课重点（模型已在 `OPT_MODEL.md` 定义）。本课重点是工程化。

## 本节学习

- Python 包与模块结构：`optimizer/` 作为一个包，`__init__.py`、相对导入
- 数据加载与校验：CSV → 类型化的数据结构（`dataclass` 或 Pydantic）
- 纯函数接口设计：`solve(problem) -> Solution`，不在函数里读文件、不打印
- 求解状态的显式建模（`OPTIMAL / FEASIBLE / INFEASIBLE / TIMEOUT / ERROR`）
- pytest：测试函数、fixture、手算小算例
- 命令行入口：`python -m optimizer.cli --scenario ...`

## 本节实现

```text
data/
  generate_data.py          # 生成 10 仓 × 10 SKU 合成数据（固定随机种子）
  *.csv                     # 见 OPT_MODEL.md 第 10 节
  scenarios/*.json

optimizer/
  models.py                 # 数据结构（输入 / 输出）
  data_loader.py            # 读 CSV + scenario → 模型输入
  solver.py                 # OR-Tools MIP 模型
  heuristic.py              # Do Nothing 与 Rule-Based（兼作 fallback）
  validator.py              # 独立校验任意方案
  cli.py                    # 命令行入口，输出 JSON

tests/
  test_validator.py
  test_solver.py            # 手算小算例 + VIP 不可行算例
```

## 本节最终成果

```text
python -m optimizer.cli --scenario data/scenarios/supplier_delay_po1024.json
```

输出三种方法（Do Nothing / Rule-Based / MIP）的方案对比，且全部通过 Validator。

此时还没有 API、Agent、Docker：这是一个纯粹、可独立运行、可测试的 OR Engine。

---

# Part B — 从本地程序到网络服务

# Lesson 2 — Program, Process, Linux & SSH

## 核心问题

> 本地写好的程序，到了服务器上是怎么运行的？

## 本节学习

- program vs process、PID、foreground / background
- 用户、文件权限（`chmod`，以及为什么 SSH 私钥权限必须是 600）
- 环境变量、`PATH`、`which`
- SSH：公钥认证、`~/.ssh/config` 与主机别名
- 让进程在断开 SSH 后继续运行：`nohup` / `tmux`

常用命令：

```text
pwd ls cd cp mv rm cat less grep which env export
ps top htop kill chmod ssh scp tmux
```

## 本节实现

```text
本地 push → GitHub → ssh myserver → git clone → 创建 venv → 运行 optimizer
```

- 在服务器上运行 `python -m optimizer.cli`，观察 PID、CPU、内存
- 构造一个长时间求解（调大规模或去掉时间限制），用 `ps` / `kill` 停止
- 用环境变量 `SOLVER_TIME_LIMIT` 控制求解时间

## 本节最终成果

同一套代码在 Windows 和 `myserver` 上都能运行，并通过 Git 同步。

---

# Lesson 3 — Networking & HTTP Fundamentals

## 核心问题

> 如果 Agent 和 Optimizer 不在同一个程序、甚至不在同一台机器上，它们怎么通信？

## 本节学习

- 网络：IP、port、localhost、`127.0.0.1` vs `0.0.0.0`、bind / listen、TCP、DNS、防火墙 / 安全组
- SSH 端口转发（`ssh -L`）：服务器端口不对外开放时如何访问
- HTTP：request / response、method、headers、body、JSON、status code
- HTTPS 与 TLS（只需理解“加密的 HTTP”）

## 本节实验

1. 在 `myserver` 上 `python -m http.server 8000`，分别绑定 `127.0.0.1` 与 `0.0.0.0`
2. 用 `ss -lntp` 查看监听状态，从服务器内、本地分别 `curl`
3. 用 `ssh -L 8000:localhost:8000 myserver` 从本地访问
4. **第一次调用 LLM**：用 `curl` 直接向 MaaS 平台发送一个 chat completion 请求，观察 URL、`Authorization` header、JSON body、status code、返回的 token 用量

第 4 个实验的意义：LLM API 不是魔法，它就是一个 HTTPS POST 请求。Part C 的所有 LLM 调用都建立在这个认识之上。

## 本节重点：Debug 思维

```text
程序在运行吗？ → 端口在监听吗？ → 绑定了哪个地址？ → 网络可达吗？ → 防火墙放行吗？
```

---

# Lesson 4 — FastAPI Optimization Service

## 核心问题

> 如何把 `solve(problem)` 变成任何程序都能调用的服务？

## 本节学习

- API、REST、endpoint
- request / response schema（Pydantic）、序列化、输入校验
- HTTP status code 的语义：`200`、`400`/`422`、`500`、`503`
- uvicorn：ASGI server、`--host`、`--port`、`--workers`
- 自动生成的 OpenAPI 文档（`/docs`）

## 本节实现

```text
services/optimizer_api/
  main.py          # FastAPI app
  schemas.py       # 请求 / 响应 schema（与 OPT_MODEL.md 第 17 节一致）
tests/
  test_optimizer_api.py   # FastAPI TestClient
```

- `GET /health` → `{"status": "ok"}`
- `POST /optimize` → 调用 `optimizer/`，返回方案
- 错误处理：非法输入 → 422；`INFEASIBLE` → 200 + status 字段；求解器异常 → 500

## 本节最终成果

在 `myserver` 上运行服务，本地通过 SSH 端口转发调用 `POST /optimize`。

---

# Lesson 5 — Docker & Runtime Environment

## 核心问题

> 为什么同一套代码换一台机器就可能运行失败？

## 本节学习

- image、container、layer、Dockerfile、build context
- container filesystem vs host filesystem、volume
- port mapping（`-p 8000:8000`）
- 通过环境变量注入配置
- `docker ps / logs / exec / stop / rm`

## 本节实现

```text
docker/optimizer_api.Dockerfile
```

- 构建 `supplyops-optimizer` image，在本地与 `myserver` 上运行
- 配置改为环境变量：`PORT`、`LOG_LEVEL`、`SOLVER_TIME_LIMIT`

注意：课题组服务器可能没有 Docker 权限，需在开课前确认；否则先在本地 Docker Desktop 完成。

---

# Lesson 6 — Mock ERP Service & Docker Compose

## 核心问题

> Agent 为什么不能直接读 CSV？企业里的数据从哪里来？

## 本节学习

- system of record、ERP、CRUD、state、transaction
- 读接口 vs 写接口：为什么写操作要更谨慎
- SQLite 基础
- Docker Compose：多服务、服务名即 DNS、容器间网络

## 本节实现

```text
services/erp/
  main.py
  db.py            # SQLite，启动时从 data/*.csv 初始化
```

读接口：

```text
GET /warehouses
GET /inventory?warehouse_id=&sku_id=
GET /orders?warehouse_id=&sku_id=&due_before=
GET /purchase-orders/{po_id}
GET /transfer-lanes
GET /expedite-options
GET /priority-rules
```

写接口：

```text
POST /plans                  # 提交恢复方案，状态 PENDING
POST /plans/{plan_id}/approve
POST /plans/{plan_id}/reject
POST /plans/{plan_id}/execute   # 仅 APPROVED 可执行，更新库存与订单
```

方案状态：`PENDING → APPROVED / REJECTED → EXECUTED`

```text
docker/compose.yml           # erp + optimizer_api
```

## 本节最终成果

两个独立服务通过 Compose 一键启动，彼此通过服务名访问。

---

# Part C — 接入 LLM，变成 Agent

# Lesson 7 — LLM API & Structured Output

## 核心问题

> 如何让 LLM 的输出变成程序可以信任和使用的数据？

## 本节学习

- MaaS、OpenAI 兼容接口、`base_url` / `api_key` / `model`
- messages、system prompt、temperature
- token、上下文窗口、成本计算（额度有限，每次调用记录 token）
- 结构化输出：JSON mode / JSON schema，Pydantic 校验，校验失败后的重试
- **不可信输入**：供应商邮件是外部输入，可能包含 prompt injection

## 本节实现

```text
agent/
  llm_client.py     # 封装 MaaS 调用，读环境变量 MAAS_API_KEY / MAAS_BASE_URL / MAAS_MODEL
  event_parser.py   # 供应商消息 → DisruptionEvent
  schemas.py
tests/
  test_event_parser.py
data/eval/messages.jsonl    # 10–20 条带标注的供应商消息（含 1–2 条注入样例）
```

输入：

```text
PO-1024 containing 500 units of SKU-A will arrive four days late due to a production issue.
```

输出：

```json
{"event_type": "SUPPLIER_DELAY", "po_id": "PO-1024", "sku_id": "SKU-A", "quantity": 500, "delay_days": 4}
```

## 本节实验

- 在 2–3 个模型（如 DeepSeek / Qwen / GLM）上跑同一组消息，比较准确率、延迟、成本
- 确认所选模型支持 tool calling，作为 Lesson 8 的主模型

---

# Lesson 8 — Tool Calling & Agent Loop

## 核心问题

> LLM 如何“使用工具”？Agent 和普通程序的区别到底在哪里？

## 本节学习

- tool calling 协议：tool schema → `tool_calls` → 执行 → `tool` message → 继续
- **手写 Agent Loop**（不使用框架），理解每一轮发生了什么
- 工具设计：粒度、参数、返回值大小、把错误作为 tool result 返回而不是抛异常
- 循环控制：最大步数、终止条件
- **Workflow vs Agent**：哪些步骤应该写死，哪些交给 LLM 判断

## 本节实现

```text
agent/
  tools.py          # 包装 ERP / Optimizer HTTP 接口
  loop.py           # Agent Loop
```

工具：

```text
get_purchase_order(po_id)
get_inventory(warehouse_id, sku_id)
get_open_orders(warehouse_id, sku_id, due_before)
assess_shortage(...)        # 确定性计算，判断是否需要优化
run_optimizer(scenario)     # 调用 Optimization Service
```

## 本节关键原则

```text
LLM：理解、判断、选择工具、解释结果
OR ：数学计算、约束满足、优化决策
```

LLM 给出的任何数字都必须来自工具返回值。

## 本节最终成果

Agent 能够：理解供应商异常 → 查询 ERP → 发现潜在缺口 → 调用 Optimization Service → 用业务语言解释方案。

---

# Lesson 9 — End-to-End Workflow & Human Approval

## 核心问题

> 如何把独立组件组合成一个**可控**的业务系统？

## 本节学习

- 状态机：用确定性流程控制整体，只在需要判断的节点使用 LLM / Agent Loop
- Human-in-the-Loop：审批是流程中的一个状态，而不是一句 prompt
- 审计：谁、在什么时候、批准了什么方案

## 本节实现

```text
agent/workflow.py
```

```text
RECEIVED → PARSED → INVESTIGATED → OPTIMIZED → VALIDATED → AWAITING_APPROVAL
         → APPROVED → EXECUTED
         → REJECTED
任意步骤失败 → ESCALATED（人工处理）
```

1. 收到供应商消息
2. LLM 解析事件（Lesson 7）
3. Agent Loop 调查影响（Lesson 8，限制步数）
4. 若无缺口 → 结束并说明原因
5. 调用 Optimization Service
6. Validator 检查（不通过 → ESCALATED）
7. Agent 生成业务解释
8. Human Approval（CLI：Approve / Reject）
9. 调用 ERP 执行方案并记录

## 本节最终成果

第一次实现完整闭环：Exception → Decision → Approval → Action。

---

# Lesson 10 — Reliability & Observability

## 核心问题

> 如果 Solver、LLM 或 API 出问题，系统应该怎么办？出问题后怎么知道发生了什么？

## 本节学习

- timeout、retry、exponential backoff、fallback、graceful degradation
- 幂等性：为什么 `execute` 不能被重试两次
- 结构化日志、request ID、跨服务传递 request ID
- Agent tracing：每次 LLM 调用、每次工具调用的输入 / 输出 / 耗时 / token

## 本节实现

| 故障 | 处理 |
| ---- | ---- |
| Solver timeout / error | Rule-Based heuristic → Validator |
| LLM 调用失败 / 返回非法 JSON | retry → 备用模型 → ESCALATED |
| ERP 500 / 连接失败 / 超时 | retry with backoff → ESCALATED |
| Agent 超出最大步数 | ESCALATED |

日志字段：

```text
request_id  step  tool  status  latency_ms  error  fallback  tokens  cost
```

## 本节实验

故意制造 Solver Timeout、LLM Failure、ERP Failure 三种故障，观察并记录系统行为。

---

# Lesson 11 — Evaluation, Deployment & Demo

## 核心问题

> 怎样证明这个项目不仅“能跑”，而且是一个可信的工程作品？

## Deployment

在 `myserver` 上用 Docker Compose 统一启动 ERP、Optimization Service、Agent。

## Evaluation

构造 20–30 个 synthetic disruption scenarios（Supplier Delay / Inventory Discrepancy / VIP Urgent Order），分两层评估：

**OR 层**：Do Nothing vs Rule-Based vs Optimization

```text
recovery cost / delayed quantity / VIP violations / feasibility / solve time
```

**Agent 层**

```text
event parsing accuracy      解析是否正确
tool trajectory             是否调用了必要的工具、有无多余调用
end-to-end success          是否到达正确的终态
injection resistance        注入样例是否被识别 / 无害化
fallback usage              fallback 被触发的比例
cost per case               每个案例的 token 成本
```

只能称为 synthetic evaluation，不能声称是真实企业 ROI。

## Final Demo

- Demo 1：Supplier Delay → Optimizer → Valid Plan → Approve → Execute
- Demo 2：Solver Timeout → Fallback → Valid Feasible Plan

## GitHub 最终需要有

```text
README / Architecture Diagram / Business Problem / Optimization Model
API Documentation / Demo / Evaluation Results / Failure Handling / Quick Start
```

---

# Bonus Lesson — Kubernetes

目标不是部署生产 K8s，而是能听懂企业里的基础 K8s 对话。

- 概念：Pod、Deployment、Service、Replica、Namespace、ConfigMap、Secret
- 命令：`kubectl get pods`、`kubectl logs`、`kubectl describe pod`
- 映射：多个 Optimizer Pod 由一个 Service 提供统一入口

---

# 4. 明确不做的内容

```text
Multi-Agent / RAG / LoRA / RL / Agent 框架（LangChain 等，可在课程结束后对比）
Demand Forecasting / VRP / 复杂生产调度
真实 SAP 集成 / 真实企业数据库
Kafka / Redis / Service Mesh / 复杂 Kubernetes
```

---

# 5. 每节课统一教学格式

1. **Why** —— 为什么这个东西存在？
2. **Concepts** —— 本节核心概念
3. **SupplyOps Mapping** —— 在系统中对应哪里
4. **Implementation** —— 今天具体实现什么（文件、模块、接口）
5. **Experiment** —— 一个小实验
6. **Debug** —— 至少一种故障及诊断过程
7. **Check** —— 3–5 个问题检查理解
8. **Update State** —— 更新 `COURSE_STATE.md`，写 `notes/`，提交 PR

---

# 6. 目录结构

```text
SupplyOps-Copilot/
├── README.md
├── STUDY_PLAN.md            # 课程大纲
├── COURSE_STATE.md          # 课程进度（唯一进度来源）
├── OPT_MODEL.md             # OR 模型与数据规范
├── requirements.txt
├── .gitignore
├── .env.example             # 环境变量模板（不含真实密钥）
│
├── data/                    # 合成数据 CSV + 生成脚本
│   ├── scenarios/           # 异常场景
│   └── eval/                # LLM / Agent 评估数据
├── optimizer/               # OR Engine（纯 Python 包，不依赖 HTTP）
├── services/
│   ├── optimizer_api/       # Optimization Service（FastAPI）
│   └── erp/                 # Mock ERP Service（FastAPI + SQLite）
├── agent/                   # LLM client、Agent Loop、Workflow
├── tests/
├── docker/                  # Dockerfile、compose.yml
└── notes/                   # 每课学习笔记
```

分层原则：`optimizer/` 不知道 HTTP 的存在；`services/` 只做协议转换；`agent/` 只通过 HTTP 访问 `services/`。

---

# 7. AI Tutor 指令

使用 Claude Code、Cursor 或 ChatGPT 辅导时，先让 AI 阅读：

```text
README.md
STUDY_PLAN.md
COURSE_STATE.md
OPT_MODEL.md
```

然后使用：

> 请根据 `COURSE_STATE.md` 判断当前进度，并按照 `STUDY_PLAN.md` 教我下一课。
>
> 每节课开始时先解释为什么要学习这一部分、核心概念是什么、它在 SupplyOps 系统中的位置是什么。
>
> 然后明确告诉我这一课最终要实现哪些文件、模块、接口或功能。
>
> 学习阶段不要直接替我完成全部代码。OR 建模部分我比较熟悉，可以讲得简略；系统和 LLM 部分需要讲透。
>
> 如果出现错误，优先带我定位属于 Application、Linux、Network、API、Docker、LLM 还是 Optimization 层。
>
> 每节课结束后帮助我更新 `COURSE_STATE.md`。
>
> 不要擅自增加课程范围之外的大型功能。

---

# 8. 最终学习成果

课程结束后，能够独立理解并解释：

```text
业务问题 → 业务数据 → OR 模型 → Python Optimizer → FastAPI → HTTP / Network
→ Docker → Linux Server → LLM API → Tool Calling → Agent Loop → Workflow
→ Validation → Human Approval → Reliability → Evaluation → Deployment
```

目标角色：能够把 **Business Problem + LLM + Optimization + Software Engineering** 组合成完整解决方案的

> **Optimization Engineer / AI Engineer / Forward Deployed Engineer**
