# SupplyOps Copilot

An engineering practice project for building a production-oriented **AI + Operations Research decision system**.

The project focuses on a realistic supply-chain problem:

> When supplier delays, inventory shortages, or urgent customer orders disrupt the original fulfillment plan, the system detects the exception, retrieves relevant business data, generates an optimization-based recovery plan, validates the result, and asks for human approval before execution.

This repository is also used as a hands-on learning project for software engineering, AI agents, and production deployment.

---

## 1. Project Goal

The goal is to build a small but complete **exception-to-action decision workflow**:

```text
Supply Chain Exception
        ↓
LLM Event Understanding
        ↓
Business Data Retrieval
        ↓
Optimization Solver
        ↓
Solution Validation
        ↓
Human Approval
        ↓
Execution / Update
```

The project intentionally combines two complementary capabilities:

- **AI / Agent Engineering**

  - Understand unstructured business events
  - Call external tools and APIs
  - Coordinate multi-step workflows
  - Handle failures and uncertainty
- **Operations Research**

  - Inventory allocation
  - Warehouse transfer
  - Order fulfillment
  - Cost and service-level trade-offs
  - Re-optimization after disruptions

---

## 2. Business Scenario

Consider a company operating multiple warehouses and serving multiple customer orders.

A supplier suddenly sends a message such as:

> PO-1024 containing 500 units of SKU-A will be delayed by four days due to a production issue.

The delay may cause future inventory shortages.

The system should answer questions such as:

- Which customer orders will be affected?
- Which warehouses still have available inventory?
- Should inventory be transferred between warehouses?
- Should some orders be delayed?
- Should emergency procurement be used?
- What is the lowest-cost feasible recovery plan?
- Which actions require human approval?

The goal is not merely to generate a recommendation using an LLM.

The system should produce a **feasible and verifiable decision**.

---

## 3. System Architecture

The target architecture is:

```text
                    ┌─────────────────┐
                    │   MaaS / LLM    │
                    └────────┬────────┘
                             │
                             │ API
                             ▼
                    ┌─────────────────┐
                    │ SupplyOps Agent │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       Business Data    OR Optimizer     Policies
       / Mock ERP       / OR-Tools       / Rules
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                       Validator
                             │
                             ▼
                     Human Approval
                             │
                             ▼
                     Execute / Update
```

A key design principle is:

> **LLM handles interpretation and orchestration; optimization handles decision calculation.**

The LLM should not invent inventory numbers or directly calculate complex allocation decisions.

Instead, it should call tools that retrieve real system state and invoke deterministic optimization models.

---

## 4. Initial MVP Scope

The first version will deliberately remain small.

### Data scale

- 10 regional warehouses
- 10 SKUs
- ~150 customer orders within the planning horizon
- ~30–40 inter-warehouse transfer lanes
- 20–30 inbound purchase orders
- Synthetic business data

### Exception scenarios

The MVP will initially support:

1. Supplier shipment delay
2. Inventory discrepancy
3. Urgent high-priority customer order

### Optimization decisions

Each order is fulfilled by its regional warehouse; cross-region supply happens only through inter-warehouse transfers. The model (a small fixed-charge network-flow MIP) determines:

- Inter-warehouse transfers and which lanes to activate
- Emergency procurement quantities
- Delayed quantities per order

Objective:

$$
\min \; C_{\text{transfer}} + C_{\text{lane}} + C_{\text{expedite}} + C_{\text{delay}}
$$

subject to inventory balance, shared lane capacity, expedite capacity, and VIP service-level constraints.

See [OPT_MODEL.md](OPT_MODEL.md) for the full formulation and data specification.

---

## 5. Technology Stack

The planned stack includes:

### Core

- Python 3.9
- Pandas
- OR-Tools
- SQLite
- pytest

### Service Layer

- FastAPI
- Pydantic
- HTTP / REST APIs
- JSON

### AI

- LLM API / MaaS (OpenAI-compatible; DeepSeek / Qwen / GLM)
- Structured Output
- Tool Calling
- Hand-written agent loop (no agent framework)

### Engineering

- Linux
- SSH
- Git
- Docker
- Docker Compose
- Logging
- Health Checks
- Timeout
- Retry
- Fallback

Kubernetes may be explored later for learning purposes, but it is **not required for the MVP**.

---

## 6. Reliability Design

The system should not assume that every component always succeeds.

Examples:

### Solver failure

```text
Optimization Solver
        ↓ timeout
Retry
        ↓ failure
Heuristic Fallback
        ↓
Feasible Recovery Plan
```

### LLM failure

```text
Primary Model
      ↓ failure
Retry
      ↓
Fallback Model
```

### Execution safety

```text
Agent Recommendation
        ↓
Optimization
        ↓
Validation
        ↓
Human Approval
        ↓
Execution
```

Potential future mechanisms include:

- request IDs
- structured logs
- rollback
- audit logs
- health checks
- input validation

---

## 7. Learning Objectives

This repository is also a practical engineering course.

Instead of learning infrastructure concepts independently, each concept will be introduced when the project needs it.

The planned learning path (details in [STUDY_PLAN.md](STUDY_PLAN.md)):

```text
Part A  Local OR engine         data + model + validator + tests
          ↓
Part B  From program to service Linux → networking → HTTP/API → Docker → Mock ERP
          ↓
Part C  From service to agent   LLM API → tool calling → workflow → reliability → evaluation
```

Topics include:

### Linux

- process
- PID
- environment variables
- filesystem
- permissions
- SSH

### Networking

- IP
- port
- localhost
- `127.0.0.1`
- `0.0.0.0`
- DNS
- TCP
- HTTP

### APIs

- endpoint
- request
- response
- GET / POST
- JSON
- status codes

### Docker

- image
- container
- Dockerfile
- port mapping
- volume
- environment variables

### LLM & Agents

- structured output and schema validation
- tool calling and the agent loop
- workflow vs. agent
- human-in-the-loop approval
- prompt injection from untrusted input
- agent evaluation

### Production Reliability

- timeout
- retry
- fallback
- logging
- tracing
- health check
- rollback

---

## 8. Development Roadmap

Lesson numbers follow [STUDY_PLAN.md](STUDY_PLAN.md). Detailed progress is tracked in [COURSE_STATE.md](COURSE_STATE.md).

### Part A — Local OR Engine

- [X] L0 Initialize Git repository and project structure
- [ ] L0 Prepare development environment (Python 3.9, venv)
- [ ] L1 Build synthetic supply-chain data (10 warehouses × 10 SKUs)
- [ ] L1 Implement optimization model, baselines, and validator
- [ ] L1 Unit tests with pytest

### Part B — From Program to Service

- [ ] L2 Run the optimizer on a Linux server over SSH
- [ ] L3 Understand IP, ports, and HTTP; call an LLM API with curl
- [ ] L4 FastAPI optimization service (`/health`, `/optimize`)
- [ ] L5 Containerize the optimization service with Docker
- [ ] L6 Mock ERP service (SQLite) + Docker Compose

### Part C — From Service to Agent

- [ ] L7 Parse supplier messages into structured events
- [ ] L8 Tool calling and a hand-written agent loop
- [ ] L9 End-to-end workflow with human approval
- [ ] L10 Timeout, retry, fallback, logging, tracing
- [ ] L11 Evaluation, deployment, and final demo

---

## 9. Project Structure

```text
SupplyOps-Copilot/
├── README.md
├── STUDY_PLAN.md            # course outline
├── COURSE_STATE.md          # course progress
├── OPT_MODEL.md             # optimization model & data spec
├── requirements.txt
├── .env.example
│
├── data/                    # synthetic CSV data + generator
│   ├── scenarios/           # disruption scenarios
│   └── eval/                # LLM / agent evaluation data
├── optimizer/               # OR engine (pure Python, no HTTP)
├── services/
│   ├── optimizer_api/       # Optimization Service (FastAPI)
│   └── erp/                 # Mock ERP Service (FastAPI + SQLite)
├── agent/                   # LLM client, agent loop, workflow
├── tests/
├── docker/                  # Dockerfiles, compose.yml
└── notes/                   # per-lesson study notes
```

---

## 10. Project Philosophy

This project is intentionally designed around several principles.

### Business problem first

Start from a realistic enterprise workflow rather than building an Agent for its own sake.

### Optimization where correctness matters

Use mathematical optimization for constrained decision-making instead of asking the LLM to calculate decisions directly.

### LLM where judgment is required

Use language models for interpretation, orchestration, and interaction with unstructured information.

### Human control for important actions

Recommendations should be validated before execution.

### Reliability over demo complexity

A simple system with validation, timeout, fallback, and logging is more valuable than a complex multi-agent demo that only works under ideal conditions.

### Learn by building

Every engineering concept introduced in this project should solve a concrete problem in the system.

---

## Current Status

**Lesson 0 — Project Setup, Git & Dev Environment**

The business problem, optimization model, and course plan have been defined.

Next step:

> Finish the development environment setup, then build the local OR engine (Lesson 1).
