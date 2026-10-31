
# SupplyOps Engineering Course State

## Current Stage

**Lesson 0 — Project Setup**

Current objective:

> Build the project foundation and prepare the local development workflow before starting engineering lessons.

---

## Project Goal

Build a small but complete production-oriented **AI + Operations Research decision system** for supply-chain exception recovery.

Target workflow:

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

The project should simultaneously demonstrate:

- Operations Research modeling and optimization
- AI / Agent engineering
- API and service design
- Linux and deployment fundamentals
- Reliability engineering
- Business-oriented system thinking

---

## Current Architecture

Planned architecture:

```text
Local Windows Development Environment
        │
        │ Git / SSH
        ▼
Linux Server
        │
        ├── Optimization Service
        │       └── OR-Tools
        │
        ├── Mock ERP / Business Data
        │
        └── SupplyOps Agent
                │
                ▼
             MaaS LLM
```

Current implementation status:

```text
Git repository        : TODO
Local optimizer       : TODO
Linux environment     : TODO
FastAPI               : TODO
Docker                : TODO
LLM integration       : TODO
Agent                 : TODO
Reliability mechanisms: TODO
Final deployment      : TODO
```

---

# Course Roadmap

## Lesson 0 — Project Setup

Status: **IN PROGRESS**

Topics:

- Git repository
- Project structure
- README
- COURSE_STATE
- `.gitignore`
- Local development environment

Tasks:

- [ ] Create local project directory
- [ ] Initialize Git repository
- [ ] Add README.md
- [ ] Add COURSE_STATE.md
- [ ] Add .gitignore
- [ ] Create initial project folders
- [ ] Make first Git commit
- [ ] Connect remote Git repository

---

## Lesson 1 — Program, Process, Server and SSH

Status: **NOT STARTED**

Topics:

- program vs process
- process ID (PID)
- foreground process
- background process
- server
- host
- local machine vs remote machine
- SSH
- environment variables
- PATH

Hands-on goals:

- Run a Python program locally
- SSH into Linux
- Run the same program remotely
- Inspect the running process
- Stop and restart the process

Commands expected:

```bash
pwd
ls
cd
which
env
export
ps
top
htop
kill
ssh
```

---

## Lesson 2 — Networking Fundamentals

Status: **NOT STARTED**

Topics:

- IP address
- port
- localhost
- 127.0.0.1
- 0.0.0.0
- TCP
- DNS
- client / server
- bind
- listen

Hands-on goals:

- Start a simple network service
- Inspect listening ports
- Access a Linux service from another machine
- Diagnose a connectivity failure

Commands expected:

```bash
curl
ping
ss
ip
```

---

## Lesson 3 — HTTP and APIs

Status: **NOT STARTED**

Topics:

- HTTP
- request
- response
- endpoint
- GET
- POST
- JSON
- HTTP status codes
- REST API

Hands-on goals:

- Build the first FastAPI service
- Create `/health`
- Create `/optimize`
- Call the API using curl and Python

---

## Lesson 4 — Docker

Status: **NOT STARTED**

Topics:

- image
- container
- Dockerfile
- host
- container filesystem
- port mapping
- environment variables
- volume

Hands-on goals:

- Containerize the optimization API
- Build Docker image
- Run container
- Access containerized service from host

---

## Lesson 5 — LLM API and Tool Calling

Status: **NOT STARTED**

Topics:

- MaaS
- LLM API
- structured output
- tool calling
- Agent loop
- tool execution
- state

Hands-on goals:

- Call an LLM through API
- Parse a supplier disruption message
- Implement business tools
- Let the LLM call optimization tools

---

## Lesson 6 — Reliability Engineering

Status: **NOT STARTED**

Topics:

- timeout
- retry
- fallback
- exponential backoff
- logging
- request ID
- validation
- graceful degradation

Hands-on goals:

- Force solver timeout
- Implement heuristic fallback
- Simulate LLM API failure
- Add structured logs
- Add validation before execution

---

## Lesson 7 — Deployment and Final Demo

Status: **NOT STARTED**

Topics:

- service deployment
- health checks
- Docker Compose
- service-to-service communication
- configuration
- basic production architecture

Hands-on goals:

- Deploy complete SupplyOps system
- Run end-to-end supply disruption scenario
- Demonstrate failure handling
- Prepare final GitHub documentation

---

# Knowledge Tracking

## Comfortable

Currently none.

---

## Learning

- Git project organization
- Local vs remote development workflow

---

## Not Yet Covered

- Linux process management
- Networking
- HTTP
- FastAPI
- Docker
- LLM tool calling
- Agent workflow
- Reliability
- Deployment
- Kubernetes basics

---

# Engineering Vocabulary

| Term           | Understanding                          | Status      |
| -------------- | -------------------------------------- | ----------- |
| Git repository | Version-controlled project directory   | Learning    |
| Program        | Code stored on disk                    | Not covered |
| Process        | Running instance of a program          | Not covered |
| Server         | Machine or program providing a service | Not covered |
| Host           | Machine running processes/containers   | Not covered |
| SSH            | Remote shell protocol                  | Not covered |
| IP             | Network address                        | Not covered |
| Port           | Network endpoint number                | Not covered |
| API            | Interface between software systems     | Not covered |
| Container      | Isolated application runtime           | Not covered |
| Timeout        | Maximum waiting time                   | Not covered |
| Retry          | Reattempt after failure                | Not covered |
| Fallback       | Backup strategy after failure          | Not covered |

---

# Current Environment

## Local

Operating system:

```text
Windows
```

Development tools:

```text
VS Code
Git
Python
```

Exact versions:

```text
TODO
```

---

## Remote Server

Status:

```text
To be configured / confirmed
```

Expected environment:

```text
Linux
Python
Git
Docker
```

---

# Current Task

Complete **Lesson 0 — Project Setup**.

Target repository structure:

```text
SupplyOps-Copilot/
│
├── README.md
├── COURSE_STATE.md
├── .gitignore
│
├── notes/
├── data/
├── optimizer/
├── api/
├── agent/
├── tests/
└── docker/
```

---

# Next Action

1. Initialize Git locally.
2. Create repository structure.
3. Make the first commit.
4. Push to a remote Git repository.
5. Start **Lesson 1 — Program, Process, Server and SSH**.

---

# Learning Rules

During this course:

1. Concepts should be explained before implementation.
2. Each lesson should connect directly to the SupplyOps project.
3. Hands-on exercises should remain small and focused.
4. Debugging should emphasize diagnosis rather than immediately giving the answer.
5. Production concepts should be introduced only when the project needs them.
6. Avoid unnecessary complexity such as multi-agent systems or Kubernetes during the MVP.
7. `COURSE_STATE.md` is the source of truth for course progress.

---

## Last Updated

2026-10-31

Current status:

> Project initialization.
