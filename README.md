
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

- 10 warehouses
- 10 SKUs
- 20–30 customer orders
- Several purchase orders
- Synthetic business data

### Exception scenarios

The MVP will initially support:

1. Supplier shipment delay
2. Inventory discrepancy
3. Urgent high-priority customer order

### Optimization decisions

The optimization model may determine:

- Order-to-warehouse allocation
- Inter-warehouse inventory transfers
- Delayed quantities
- Emergency procurement quantities

Example objective:

\[
\min
(
C_{\text{shipping}}
+
C_{\text{transfer}}
+
C_{\text{expedite}}
+
C_{\text{late}}
)
\]

subject to inventory, transportation capacity, demand, and service-level constraints.

---

## 5. Technology Stack

The planned stack includes:

### Core

- Python
- Pandas
- OR-Tools
- SQLite

### Service Layer

- FastAPI
- HTTP / REST APIs
- JSON

### AI

- LLM API / MaaS
- Tool Calling
- Structured Output

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

The planned learning path is:

```text
Python Program
      ↓
Linux Process
      ↓
Networking
      ↓
HTTP / API
      ↓
FastAPI Service
      ↓
Docker Container
      ↓
LLM Tool Calling
      ↓
Agent Workflow
      ↓
Reliability
      ↓
Deployment
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

### Production Reliability

- timeout
- retry
- fallback
- logging
- health check
- rollback

---

## 8. Development Roadmap

### Stage 0 — Project Setup

- [ ] Initialize Git repository
- [ ] Create project structure
- [ ] Prepare development environment

### Stage 1 — Local Optimizer

- [ ] Build synthetic supply-chain data
- [ ] Implement optimization model
- [ ] Validate optimization results

### Stage 2 — Optimization Service

- [ ] Build FastAPI service
- [ ] Implement `/optimize`
- [ ] Implement `/health`

### Stage 3 — Linux & Networking

- [ ] Run service on Linux server
- [ ] Access service remotely
- [ ] Understand process, IP, and port behavior

### Stage 4 — Docker

- [ ] Create Dockerfile
- [ ] Containerize optimization service
- [ ] Configure port mapping and environment variables

### Stage 5 — LLM Agent

- [ ] Parse supply-chain exception messages
- [ ] Implement tool calling
- [ ] Connect Agent to business data
- [ ] Connect Agent to optimization service

### Stage 6 — Reliability

- [ ] Timeout
- [ ] Retry
- [ ] Solver fallback
- [ ] Logging
- [ ] Validation
- [ ] Human approval

### Stage 7 — Final Demo

- [ ] End-to-end disruption scenario
- [ ] Evaluation cases
- [ ] Architecture diagram
- [ ] Demo video
- [ ] Final documentation

---

## 9. Project Structure

Planned repository structure:

```text
SupplyOps-Copilot/
│
├── README.md
├── COURSE_STATE.md
├── .gitignore
│
├── notes/
│   ├── 01_linux.md
│   ├── 02_network.md
│   ├── 03_api.md
│   └── 04_docker.md
│
├── data/
│
├── optimizer/
│
├── api/
│
├── agent/
│
├── tests/
│
└── docker/
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

**Stage 0 — Project Setup**

The business problem and high-level architecture have been defined.

Next step:

> Initialize the repository and begin building the first local optimization program.
