# Lesson 1 — Local OR Engine

> 本课目标：把一个优化模型做成**可以被别的程序可靠调用的软件组件**。
> 成果：`optimizer/` 包（数据模型、loader、MIP、两种启发式、validator、CLI）+ 12 个 pytest 测试，
> 一条命令对比三种方法并输出 JSON。
> 优化模型本身见 `OPT_MODEL.md`，本笔记只记工程部分。

---

## 知识点 1：用 dataclass 定义接口

```text
CSV ──data_loader──▶ Problem ──solve / do_nothing / rule_based──▶ Solution ──validator / cli──▶ JSON
```

- `Problem` / `Solution` 是各模块之间**唯一**的约定。solver 内部用 OR-Tools 还是 Gurobi，外面看不到
- 三种方法签名相同：`Problem -> Solution`，所以 CLI 可以放进一个字典循环调用，加第四种方法只需加一行
- `@dataclass(frozen=True)`：创建后不能修改，避免某个函数悄悄改掉别人还在用的数据
- 修改 frozen 对象 → `dataclasses.replace(obj, 字段=新值)`，返回一个**新对象**
- `@property`（如 `CostBreakdown.total`）是计算出来的，**不是字段**，`asdict` 不会包含它

---

## 知识点 2：错误是返回值还是异常

| 层 | 失败时 | 原因 |
| -- | ------ | ---- |
| `solve()` | **从不抛异常**，返回 `Solution(status=ERROR/INFEASIBLE/TIMEOUT)` | 无解、超时是**正常业务结果**，调用方必须处理 |
| `data_loader` | 抛 `DataValidationError` | 输入坏了，后续一切都没有意义 |
| `cli.main()` | 捕获**预期的**输入错误 → 返回退出码 3 | 给人和程序一个清楚的信号 |
| 代码 bug | **不捕获**，带 traceback 崩溃（退出码 1） | 吞掉 bug 会得到“安静地出错”的程序，最难排查 |

- `_STATUS_MAP`：把 OR-Tools 的状态码翻译成我们自己的 5 种 `SolveStatus`，不认识的一律 `ERROR`。第三方库的细节被隔离在这一张表里
- 只捕获你**预料到、并且知道怎么解释**的异常；不要写 `except Exception` 吞掉一切
- `try` 包的范围越小越好，否则可能误吞后面代码的 bug
- 一次检查收集**所有**问题再统一报告（`validate_tables`），比“报一个改一个”友好

---

## 知识点 3：独立的 validator

- validator **只依赖 `Problem`**，不 import solver 和 heuristic，所有指标自己重新计算
- 原因：和被检查对象共享代码的检查器，也会共享它的 bug
- 以后 LLM 修改过的方案、fallback 方案，都用同一个 validator 把关（Lesson 8–9）

---

## 知识点 4：数值细节

| 问题 | 例子 | 做法 |
| ---- | ---- | ---- |
| 二进制浮点误差 | `0.1 + 0.2 = 0.30000000000000004`；成本显示 `1811.8000000000002` | 计算时保持精度；比较用容差（`pytest.approx`、`COST_TOLERANCE`）；**只在输出层 round** |
| MIP 整数变量不是精确整数 | `79.9999999` | 用 `round()`，不能用 `int()`（截断 → 79） |
| 计时 | | 用 `time.perf_counter()`（单调、高精度），不用 `time.time()`（会被系统校时调整） |
| 真正的钱 | 财务系统 | `decimal.Decimal` 或以“分”为单位的整数 |

---

## 知识点 5：模块与脚本、`sys.path`

`sys.path` = Python 执行 `import` 时依次搜索的目录列表。

| 启动方式 | `sys.path[0]` | `import optimizer` | `__name__` |
| -------- | ------------- | ------------------ | ---------- |
| `python optimizer/cli.py`（脚本） | `optimizer/` 目录 | ❌ | `"__main__"` |
| `python -m optimizer.cli`（模块） | 当前目录（项目根） | ✅ | `"__main__"` |
| `import optimizer.cli`（被导入） | — | — | `"optimizer.cli"` |
| `python -m pytest` | 当前目录 | ✅ | |
| `pytest`（启动器程序） | `.venv/Scripts/` | ❌ → 需要 `pytest.ini` 里 `pythonpath = .` | |

- `if __name__ == "__main__":` = 只有被直接启动时才运行，被 import（比如被 pytest 导入）时只定义函数
- `python -c "代码"`：直接运行一段代码字符串，适合快速实验
- **不依赖运行环境的偶然状态**：路径用 `Path(__file__).resolve().parent` 定位；配置写进文件而不是靠“记得这样运行”

---

## 知识点 6：pytest

| 概念 | 含义 |
| ---- | ---- |
| 发现规则 | `tests/` 下 `test_*.py` 文件里的 `test_*` 函数 |
| `assert` | 失败时 pytest 会展开显示两边的实际值 |
| `pytest.approx` | 浮点数比较 |
| fixture | 测试函数**按参数名**声明需要什么，pytest 自动创建并注入（依赖注入） |
| `conftest.py` | 放共享 fixture，同目录及子目录的测试自动可见，不用 import |
| `monkeypatch` | 测试期间临时替换函数/属性（如让 `Solver.Solve` 直接返回 `NOT_SOLVED`），测试结束自动恢复 |
| `capsys` | 捕获测试期间的 stdout / stderr：`capsys.readouterr().out / .err` |
| `pytest.ini` | `testpaths`、`pythonpath`、`filterwarnings` 等项目级配置 |

- **单元测试**：测一个零件（solver、validator）；**集成测试**：测零件组装起来的整条链路（CLI）
- 每个测试只对自己负责的那一层下断言：CLI 测试检查“3 种方法、MIP 为 OPTIMAL 且通过校验”，不检查具体成本
- 不好造的情况（超时、后端缺失）用 monkeypatch 模拟，不必真的等 10 秒
- 测试之间相互隔离：用 `replace` 造新对象，不修改共享 fixture

---

## 知识点 7：命令行程序（CLI）的四个要素

CLI = Command-Line Interface，给人在终端里使用的入口（对比 GUI、API）。

### 1. 参数：argparse

- **argv**（argument vector）：shell 把命令按空格切成的字符串列表，Python 里是 `sys.argv`
- argparse 把它解析成带名字、带类型的 `Namespace`，并自动生成 `--help`

| 写法 | 作用 |
| ---- | ---- |
| `prog="python -m optimizer.cli"` | 帮助和报错信息里程序的名字（默认是 `cli.py`，照抄会跑不起来） |
| `required=True` | 缺参数 → 打印用法，退出码 2 |
| `type=Path` | 字符串自动转换成 `Path`（Windows 上是 `WindowsPath`，Linux 上是 `PosixPath`） |
| `--data-dir` | 属性名自动变为 `args.data_dir` |

- `main(argv=None)`：传 `None` 时读 `sys.argv[1:]`，传列表时用这个列表 → **测试可以直接调用 `main([...])`**
- `main()` 返回整数，`raise SystemExit(main())` 才真正退出 → 测试里 `assert main(...) == 3`，进程不会中途退出

### 2. 输出：JSON 序列化

- **序列化**：把内存里的对象拍平成一串文本/字节，才能写进文件、管道、网络；反过来叫反序列化
- JSON 只有 6 种类型：对象、数组、字符串、数字、`true/false`、`null`
- `json.dumps(asdict(solution))` → `TypeError: Object of type SolveStatus is not JSON serializable`：Enum、`Path` 都不是 JSON 类型
- 做法：写 `solution_to_dict()` **显式定义输出格式**，而不是把内部 dataclass 原样倒出去
- 输出格式是一份**契约**：Lesson 4 它是 HTTP 响应，Lesson 8 它是 agent 读到的工具结果。内部改字段名不应该影响下游
- `args.scenario.as_posix()`：任何系统都输出 `/`；`str(Path)` 在 Windows 上是 `data\\scenarios\\...`
- `json.dumps(..., indent=2, ensure_ascii=False)`：缩进便于阅读；中文不转义成 `\uXXXX`

### 3. stdout 与 stderr

| fd | 名字 | 放什么 | 读者 |
| -- | ---- | ------ | ---- |
| 0 | stdin | 输入 | |
| 1 | stdout | 程序的**产品**（JSON 结果） | 下一个程序、文件 |
| 2 | stderr | 给人看的**诊断信息**（错误、警告、进度、日志） | 终端前的人 |

- **fd = file descriptor（文件描述符）**：操作系统给每个打开的输入/输出通道的编号
- 程序只管往 1 号、2 号口写，不知道另一端连的是屏幕、文件还是另一个程序
- 分两个口的原因：`|` 和 `>` 只接走 stdout，错误信息不会混进数据，也不会被管道吞掉
- `print(..., file=sys.stderr)` 写 stderr
- 缓冲：stdout 重定向时先攒一批再写（效率）；stderr 尽快写出（崩溃前的最后几行不会丢）

### 4. 退出码

| 码 | 含义 | 谁产生 |
| -- | ---- | ------ |
| 0 | 成功 | `return EXIT_OK` |
| 1 | 未捕获异常（bug） | Python 解释器 |
| 2 | 参数用法错 | argparse（Unix 惯例） |
| 3 | 输入数据错（文件不存在、JSON 损坏、CSV 校验失败） | 本项目自定义 |

- `echo $?` 读上一条命令的退出码
- shell 脚本、Docker、CI 只看退出码判断成败，不读你打印了什么
- 不要混淆：`[Errno 2]` 是操作系统的**错误号**（`ENOENT`，文件不存在），不是退出码

---

## 知识点 8：重定向与管道

| 写法 | 含义 |
| ---- | ---- |
| `cmd > f` | stdout 写进文件（覆盖） |
| `cmd >> f` | stdout 追加到文件 |
| `cmd 2> f` | stderr 写进文件 |
| `cmd > f 2>&1` | stderr 也接到 stdout 指向的地方 |
| `cmd < f` | stdin 从文件读 |
| `cmd1 \| cmd2` | **管道**：cmd1 的 stdout 接到 cmd2 的 stdin，两个进程同时运行 |

- **跨进程只能传字节**：每个进程的内存相互隔离，前一个进程的 list 对象不可能直接交给后一个进程
- 接收方拿到的永远是 `str`；类型靠双方**约定格式**（JSON）+ 反序列化还原，得到的是内容相同的**新对象**
- `print(['a', True, None])` 输出的是 Python 写法，不是 JSON（单引号、`True`、`None`）→ `json.loads` 会失败；必须用 `json.dumps`
- `echo 文字`：把参数原样输出；`cat 文件`：输出文件内容（concatenate，可连接多个文件）
- ⚠️ Windows PowerShell 5.1 的 `>` 默认写 UTF-16，Python 按 UTF-8 读会出错 → 管道和重定向统一在 Git Bash 里做

---

## 知识点 9：Git —— amend、哈希链、upstream、PR

### `git commit --amend`

- 把暂存区合并进**最近一次** commit。实际是**新建**一个 commit 替换旧的，哈希会变（`6e3698a` → `17b27fe`）
- commit 哈希 = 对（代码快照 + 提交信息 + 作者/时间 + **父 commit 哈希**）计算得出
- 改了某个 commit → 它的哈希变 → 后面所有 commit 记录的父哈希都变 → 整条链被改写
- **铁律：只 amend 还没 push 的 commit**，否则本地和远程分歧，只能强推

### push 与 upstream

- `git push -u origin <分支>`：`-u` = `--set-upstream`，把本地分支和远程分支关联，以后直接 `git push` / `git pull`
- `git branch -vv`：分支后面有 `[origin/...]` 说明已关联

### Pull Request

- 请求维护者把 compare 分支**拉进** base 分支（从接收方角度命名，所以叫 pull）
- 团队里是代码审查和 CI 的地方；个人项目里是把一课作为一个完整单元合并，并留下说明
- PR 创建后继续往分支 push，新 commit **自动**出现在同一个 PR 里

### atomic commit

- 1.6 拆成两个：`test: add project root to pythonpath...`（修启动环境）和 `feat: add CLI...`（新功能）
- 两件不相关的事分开提交，`git log` 易读，也能单独 `git revert`

---

## 知识点 10：代理、localhost、端口（预告 Lesson 3）

- `~/.gitconfig` 里的 `http.proxy http://127.0.0.1:7890`：Git 的 HTTPS 请求先交给本机 7890 端口的代理程序转发
- **proxy（代理）**：替你转发请求的中间人
- **127.0.0.1 / localhost**：本机回环地址，数据不离开这台电脑
- **端口**：同一台机器上区分不同程序的编号；443 = HTTPS 标准端口；7890 = Clash 类代理软件常用端口
- `Failed to connect to github.com port 443 via 127.0.0.1` = 连本机代理都没连上 → 代理软件没开

---

## 踩过的坑

| 现象 | 出问题的层 | 原因 | 收获 |
| ---- | ---------- | ---- | ---- |
| `TypeError: Object of type SolveStatus is not JSON serializable` | 序列化 | JSON 不认识 Enum | 显式定义输出格式，`.value` 转字符串；traceback 先看最后一行 + 出错的库 |
| JSON 里出现 `data\\scenarios\\...` | 跨平台 | Windows 路径分隔符 + JSON 的反斜杠转义 | 输出路径用 `as_posix()` |
| 成本显示 `1811.8000000000002` | 数值 | 二进制浮点误差 | 只在输出层 round |
| `pytest` 报 `ModuleNotFoundError: No module named 'optimizer'`，`python -m pytest` 却正常 | 启动方式 / `sys.path` | `pytest` 启动器不把当前目录加入 `sys.path` | `pytest.ini` 加 `pythonpath = .` |
| `git push` 后 `branch -vv` 没有 `[origin/...]` | 网络 | 全局配置了本机代理，但代理软件没开 | 先看报错属于哪一层；push 后用 `branch -vv` 确认 |
| 改动已 commit 才发现漏了一处 | Git | | 未 push 时用 `git commit --amend --no-edit` |

---

## 命令速查

```bash
# 运行
python -m optimizer.cli --scenario data/scenarios/supplier_delay_po1024.json
python -m optimizer.cli --help
python -m optimizer.cli --scenario ... > report.json        # 结果存文件
python -m optimizer.cli --scenario ... | python -c "import json, sys; ..."   # 交给另一个程序
echo "exit=$?"                                              # 上一条命令的退出码

# 测试
pytest -v          # 详细
pytest -q          # 简要

# 实验
python -c "print(0.1 + 0.2)"
cmd | wc -c        # 统计管道收到多少字节

# Git
git commit --amend --no-edit           # 修改最近一次（未 push 的）commit
git push -u origin <分支>              # 首次 push 并关联上游
git branch -vv                         # 查看分支与上游的关联
git log --oneline main..<分支>         # 分支比 main 多哪些 commit
git config --show-origin --get-regexp proxy   # 代理配置来自哪个文件
```

---

## 留到后面的问题

- 场景 JSON 缺字段抛 `KeyError`、未知 disruption 类型抛 `NotImplementedError`，CLI 目前会以退出码 1 崩溃 → 应在 `load_scenario` / `apply_disruption` 里改为抛 `DataValidationError`
- 进程、内存隔离、`nohup ... > out.json 2> err.log &`、PID → Lesson 2
- 端口、localhost、代理、HTTPS → Lesson 3
- CLI 的 JSON 输出变成 HTTP API 响应 → Lesson 4
- 用 Docker 消除“我电脑上能跑”的环境差异（包括 `sys.path`、编码、路径分隔符）→ Lesson 5
