# SupplyOps Engineering Course State

> Single source of truth for course progress.
> Course outline: `STUDY_PLAN.md`. OR model & data spec: `OPT_MODEL.md`.

## Current Stage

**Lesson 0 — Project Setup, Git & Dev Environment** (IN PROGRESS)

Next: **Lesson 1 — Local OR Engine**

---

## Progress Overview

| Lesson | Topic                                | Status      |
| ------ | ------------------------------------ | ----------- |
| 0      | Project Setup, Git & Dev Environment | IN PROGRESS |
| 1      | Local OR Engine                      | NOT STARTED |
| 2      | Program, Process, Linux & SSH        | NOT STARTED |
| 3      | Networking & HTTP                    | NOT STARTED |
| 4      | FastAPI Optimization Service         | NOT STARTED |
| 5      | Docker                               | NOT STARTED |
| 6      | Mock ERP & Docker Compose            | NOT STARTED |
| 7      | LLM API & Structured Output          | NOT STARTED |
| 8      | Tool Calling & Agent Loop            | NOT STARTED |
| 9      | End-to-End Workflow & Human Approval | NOT STARTED |
| 10     | Reliability & Observability          | NOT STARTED |
| 11     | Evaluation, Deployment & Demo        | NOT STARTED |
| Bonus  | Kubernetes                           | NOT STARTED |

Implementation status:

```text
Git repository          : DONE (GitHub remote connected)
Dev environment         : TODO
Local OR engine         : TODO
Linux deployment        : TODO
Optimization service    : TODO
Docker                  : TODO
Mock ERP                : TODO
LLM integration         : TODO
Agent loop / workflow   : TODO
Reliability             : TODO
Evaluation & deployment : TODO
```

---

## Lesson 0 — Tasks

- [X] Create local project directory
- [X] Initialize Git repository
- [X] Add README.md, COURSE_STATE.md, .gitignore
- [X] Make first Git commit
- [X] Connect remote GitHub repository
- [X] Unify README / STUDY_PLAN / COURSE_STATE / OPT_MODEL
- [X] Create directory structure (incl. `services/optimizer_api`, `services/erp`)
- [x] Add `.gitkeep` so empty directories are tracked by Git
- [x] Python version decision: keep 3.9.13 (works; avoid upgrade risk)
- [x] Create `.venv`, add `requirements.txt`
- [x] Add `.env.example`
- [x] Commit and push all documents
- [ ] First branch → PR → merge cycle
- [x] Write `notes/00_setup_git_env.md`

Completion check: explain what `git add` / `git commit` / `git push` each change.

---

## Knowledge Tracking

### Background (already strong)

- Operations Research modeling (MIP, network flow)
- Data processing / analysis in Python

### Learning

- Git project organization
- Local vs remote development workflow

### Not Yet Covered

- Python packaging, virtual environments, pytest
- Linux processes, permissions, SSH
- Networking, HTTP
- FastAPI
- Docker, Docker Compose
- LLM API, structured output
- Tool calling, agent loop, workflow vs agent
- Reliability, observability
- Agent evaluation
- Kubernetes basics

---

## Engineering Vocabulary

| Term                       | Understanding                                      | Status      |
| -------------------------- | -------------------------------------------------- | ----------- |
| Git repository             | Version-controlled project directory               | Learning    |
| Staging area               | Snapshot being prepared for the next commit        | Not covered |
| Branch / PR                | Isolated line of work / request to merge it        | Not covered |
| Virtual environment        | Isolated Python interpreter + packages per project | Not covered |
| Program                    | Code stored on disk                                | Not covered |
| Process                    | Running instance of a program                      | Not covered |
| Environment variable       | Key-value config passed to a process               | Not covered |
| SSH                        | Encrypted remote shell protocol                    | Not covered |
| IP / Port                  | Machine address / process endpoint on that machine | Not covered |
| HTTP                       | Request-response protocol on top of TCP            | Not covered |
| API                        | Interface between software systems                 | Not covered |
| Container                  | Isolated application runtime                       | Not covered |
| Structured output          | LLM output constrained to a schema                 | Not covered |
| Tool calling               | LLM requests a function call; program executes it  | Not covered |
| Agent loop                 | Repeated LLM → tool → result cycle until done    | Not covered |
| Timeout / Retry / Fallback | Bound waiting / reattempt / backup strategy        | Not covered |

---

## Environment

### Local

```text
OS      : Windows 11
Editor  : VS Code
Git     : 2.51.1
Python  : 3.9.13  (kept on purpose; code must stay 3.9-compatible)
Docker  : not installed (needed by Lesson 5)
```

### Remote Server

```text
Name      : 思睿 (research group server)
SSH alias : myserver   (host details live only in ~/.ssh/config, never in this repo)
To check in Lesson 2: OS, Python version, Docker availability / permission, open ports
```

### LLM

```text
Provider : 并行科技 MaaS (DeepSeek / Qwen / GLM / ERNIE / Doubao / MiniMax)
Budget   : ~1000 RMB credit — track token cost per call
Config   : MAAS_API_KEY / MAAS_BASE_URL / MAAS_MODEL via .env (never committed)
To check in Lesson 3/7: OpenAI-compatible endpoint, which models support tool calling
```

---

## Next Action

1. Finish the remaining Lesson 0 tasks above.
2. Start **Lesson 1 — Local OR Engine** on branch `lesson-1-or-engine`.

---

## Learning Rules

1. Concepts are explained before implementation.
2. Every lesson connects directly to SupplyOps.
3. Exercises stay small and focused.
4. Debugging emphasizes diagnosis over handing out answers.
5. Production concepts are introduced only when the project needs them.
6. OR modeling can be brief; systems and LLM topics are covered in depth.
7. The tutor does not write all the code during learning.
8. No secrets (API keys, server addresses, private keys) are ever committed.

---

## Last Updated

2026-10-31 — Course documents unified; Lesson 0 in progress.
