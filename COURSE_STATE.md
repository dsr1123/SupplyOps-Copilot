# SupplyOps Engineering Course State

> Single source of truth for course progress.
> Course outline: `STUDY_PLAN.md`. OR model & data spec: `OPT_MODEL.md`.

## Current Stage

**Lesson 1 — Local OR Engine** (IN PROGRESS, branch `lesson-1-or-engine`)

Next: **Lesson 2 — Program, Process, Linux & SSH**

---

## Progress Overview

| Lesson | Topic                                | Status      |
| ------ | ------------------------------------ | ----------- |
| 0      | Project Setup, Git & Dev Environment | DONE        |
| 1      | Local OR Engine                      | IN PROGRESS |
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
Dev environment         : DONE (.venv, requirements.txt, pytest.ini)
Local OR engine         : IN PROGRESS
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
- [x] First branch → PR → merge cycle (done together with Lesson 1)
- [x] Write `notes/00_setup_git_env.md`

Completion check: explain what `git add` / `git commit` / `git push` each change.

---

## Lesson 1 — Tasks

- [x] 1.1 Branch `lesson-1-or-engine`; package skeleton; `optimizer/models.py`
- [x] 1.2 `data/generate_data.py` + CSV data + scenarios; `optimizer/data_loader.py`
- [x] 1.3 `optimizer/solver.py` (OR-Tools MIP, 5 solver statuses)
- [x] 1.4 `optimizer/heuristic.py` (Do Nothing, Rule-Based) + `optimizer/validator.py`
- [x] 1.5 pytest: 10 tests (models, solver statuses incl. monkeypatched TIMEOUT/ERROR, validator); `pytest.ini`
- [ ] 1.6 `optimizer/cli.py`: compare 3 methods on a scenario, JSON output
- [ ] PR → merge into `main`
- [ ] Write `notes/01_or_engine.md`

Baseline result (scenario `supplier_delay_po1024`):

| Method     | Total cost | Delayed qty | VIP violations | Valid |
| ---------- | ---------: | ----------: | -------------: | ----- |
| Do Nothing |     6000.0 |         380 |              1 | No    |
| Rule-Based |     1811.8 |           0 |              0 | Yes   |
| MIP        |     1431.3 |           0 |              0 | Yes   |

Key engineering ideas covered in Lesson 1:

- `Problem` / `Solution` dataclasses as the interface; solver internals never leak out
- `solve()` never raises: failures are returned as `SolveStatus` values (`_STATUS_MAP` isolates OR-Tools codes)
- Validator recomputes everything independently (shares no code with solver/heuristic)
- `round()` not `int()` for MIP values; `time.perf_counter()` for durations; float compare with tolerance
- OR-Tools `pywraplp` vs gurobipy API mapping
- Module vs script, `python -m` / `-c`, `sys.path`, `if __name__ == "__main__"`
- pytest: discovery, reading failure reports, `pytest.approx`, fixtures, `conftest.py`,
  `dataclasses.replace`, `monkeypatch`, test isolation, `pytest.ini` warning filters

---

## Knowledge Tracking

### Background (already strong)

- Operations Research modeling (MIP, network flow)
- Data processing / analysis in Python

### Learning

- Git project organization (Conventional Commits: `feat:` / `test:` / `docs:` / `chore:`)
- Local vs remote development workflow
- Python packages & modules, `python -m`, `sys.path`
- pytest (fixtures, conftest, monkeypatch)
- OR-Tools `pywraplp` (coming from gurobipy)

### Not Yet Covered

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
| Virtual environment        | Isolated Python interpreter + packages per project | Learning    |
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
| Module / script            | File imported for its functions / file run directly | Learning   |
| `python -m` / `-c`         | Run a module by name / run a code string           | Learning    |
| Unit test / regression     | Automated check of one unit / old feature broken by new change | Learning |
| Fixture                    | Test setup injected by parameter name (dependency injection) | Learning |
| Mock / stub / monkeypatch  | Fake replacing a real dependency during a test     | Learning    |
| Floating point error       | Binary floats can't represent 0.1 exactly; compare with tolerance | Learning |
| Timeout / Retry / Fallback | Bound waiting / reattempt / backup strategy        | Not covered |

---

## Environment

### Local

```text
OS      : Windows 11
Editor  : VS Code
Git     : 2.51.1
Python  : 3.9 (.venv reports 3.9.23; system note said 3.9.13 — verify which interpreter created .venv)
Shell   : Git Bash (MINGW64) in VS Code; activate with `source .venv/Scripts/activate`
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

1. Commit 1.5: `git add pytest.ini tests/` → `git commit -m "test: ..."`
2. **1.6 `optimizer/cli.py`**: run Do Nothing / Rule-Based / MIP on a scenario, validate each, print JSON.
3. PR `lesson-1-or-engine` → `main`; write `notes/01_or_engine.md`.

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

2026-11-04 — Lesson 1.1–1.5 done (loader, MIP solver, baselines, validator, pytest suite); next 1.6 CLI.