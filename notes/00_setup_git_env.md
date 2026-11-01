# Lesson 0 — Project Setup, Git & Dev Environment

> 本课目标：把一个想法变成可持续开发的软件项目。
> 成果：统一的课程文档、项目骨架、虚拟环境、两次规范的 commit 并推送到 GitHub。

---

## 知识点 1：Git 的四个区域

```text
工作区              暂存区              本地仓库             远程仓库
(working dir)  →   (staging area)  →  (local repo)    →   (remote / origin)
           git add            git commit           git push
```

| 区域 | 是什么 | 名字由来 |
| ---- | ------ | -------- |
| 工作区 | VS Code 里看到和编辑的文件 | 你“工作”的地方 |
| 暂存区 | 下一次 commit 要包含哪些改动的清单 | stage = 舞台，把要拍照的东西先摆上台 |
| 本地仓库 | `.git/` 目录，保存全部 commit 历史 | repository = 仓库 |
| 远程仓库 | GitHub 上的副本，默认名 `origin` | origin = 来源 |

- **commit** = 给暂存区拍一张快照并存档，每个快照有唯一编号（hash，如 `9264b53`）
- 暂存区存在的意义：**挑选**改动，把一堆修改拆成多个 commit
- **atomic commit**：一个 commit 只做一件事。本课拆成了 `docs:`（文档）和 `chore:`（骨架与环境）两个
- **Conventional Commits** 前缀：`feat` 新功能 / `fix` 修 bug / `docs` 文档 / `chore` 杂项维护

---

## 知识点 2：tracked 与 untracked

| 状态 | 含义 | 例子 |
| ---- | ---- | ---- |
| tracked + modified | 上次 commit 里有这个文件，现在内容变了 | README.md |
| untracked | Git 从未记录过这个文件 | 新建的 OPT_MODEL.md |
| ignored | 被 `.gitignore` 排除，Git 当作看不见 | `.venv/`、`.env` |

`git status -s`（短格式）的两列标记：**左列 = 暂存区，右列 = 工作区**

```text
 M file    右列 M：改了，还没 add
M  file    左列 M：已 add，等待 commit
A  file    左列 A：新文件已 add
?? file    untracked
```

- 一个目录里全是 untracked 文件时，`git status` 会**折叠**成一行显示目录名
- `git status -uall` 展开显示每个文件

---

## 知识点 3：Git 不追踪空目录

- Git 只记录**文件内容**，目录只是文件路径的一部分
- 空目录没有可记录的内容 → GitHub 上看不到，别人 clone 也拿不到
- 解决：放一个占位文件 `.gitkeep`
- `.gitkeep` 只是约定俗成的名字，**Git 并不认识它**，放任何文件都一样

---

## 知识点 4：.gitignore

```text
.env           # 忽略 .env
.env.*         # 忽略 .env.local、.env.prod 等
!.env.example  # ! = 取反：唯独不忽略 .env.example
```

检查某个文件是否被忽略：

```bash
git check-ignore -v .env .env.example   # 输出最后一条匹配的规则（包括 ! 规则）
git check-ignore .env .env.example      # 只输出真正被忽略的文件
```

⚠️ 读 `-v` 输出时要看规则**开头有没有 `!`**：有 `!` 表示**不被忽略**。

---

## 知识点 5：Shell 与终端

```text
你敲的命令
    ↓
Shell（壳）：解析命令、查找程序、启动程序
    ↓
Kernel（核）：创建进程、分配资源
```

- **kernel**（内核，果仁）：操作系统核心，管理 CPU、内存、文件
- **shell**（壳）：包在内核外面、负责和人对话的程序
- **terminal**（终端）：显示文字的窗口，本身不理解命令；里面跑的 shell 才理解

Windows 上的几种 shell：

| Shell | 提示符 | 风格 |
| ----- | ------ | ---- |
| cmd | `C:\...>` | `dir`、`where` |
| PowerShell（VS Code 默认） | `PS C:\...>` | `Get-Command` |
| Git Bash | `$` | `which`、`ls`、`cat`（Linux 风格） |
| bash（Linux 服务器） | `user@host:~$` | 同 Git Bash |

本项目统一使用 **Git Bash**，命令可以原样搬到 Linux 服务器。

### Shell 如何找到一个命令

```text
1. 是内置命令（builtin）吗？
2. 是别名 / 函数（alias / function）吗？
3. 依次在 PATH 环境变量的每个目录下找同名可执行文件
都没有 → command not found
```

**PATH 决定了你敲一个名字时，实际运行的是哪个程序。**

---

## 知识点 6：读懂提示符

```text
ty@LAPTOP-991HGVUK MINGW64 ~/Desktop/SupplyOps-Copilot (main)
$
```

| 部分 | 含义 |
| ---- | ---- |
| `ty` | 用户名 |
| `@LAPTOP-991HGVUK` | 主机名 —— 判断“我在哪台机器上”的最直接方式 |
| `MINGW64` | Minimalist GNU for Windows，让 Linux 风格工具在 Windows 上运行 |
| `~` | 家目录（home），这里是 `C:\Users\ty` |
| `(main)` | 当前 Git 分支 |
| `$` / `#` | 普通用户 / root 管理员 |
| `(.venv)` `(Ding)` | 当前激活的环境 |

---

## 知识点 7：路径与斜杠

| | Windows | Unix / Git Bash |
| - | ------- | --------------- |
| 分隔符 | `\` | `/` |
| 盘符 | `D:\software\...` | `/d/software/...`（没有盘符，一切挂在 `/` 下） |

- 历史原因：DOS 早期已把 `/` 用作命令选项前缀（`dir /w`），后来加目录时只好用 `\`
- Windows 底层两种斜杠都认，所以 venv 激活后出现 `C:\...\.venv/Scripts/python` 这种混合路径也能工作

---

## 知识点 8：命令行语法

```text
python   -m   venv   .venv
  │       │    │       │
命令     选项  选项值   参数
```

| 形式 | 名称 | 例子 |
| ---- | ---- | ---- |
| `-v` | 短选项：一个杠 + 一个字母 | `-m`、`-V`、`-s`、`-r` |
| `--version` | 长选项：两个杠 + 完整单词 | `--version`、`--help`、`--short` |

- 长选项用两个杠，是因为短选项可以合并（`ls -la` = `ls -l -a`），`-all` 会有歧义
- 不清楚任何命令的用法 → `命令 --help`

### `python -m`

- `-m` = module，**把模块当程序运行**：`python -m venv`、`python -m pip`、`python -m pytest`
- 用 `python -m pip` 而不是 `pip`：电脑上有多个 Python 时，保证 pip 和当前 python 是配套的

### `source`

- bash 内置命令：**在当前 shell 里**逐行执行脚本
- 直接运行脚本会开**子进程**，脚本对 PATH 的修改随子进程退出而消失
- 激活 venv 必须用 `source`，因为激活的本质就是修改当前 shell 的 PATH

```text
bash script.sh      → 子进程执行 → 修改消失 ✗
source script.sh    → 当前 shell 执行 → 修改保留 ✓
```

---

## 知识点 9：三种“虚拟”

共同思想：**让某个东西以为自己独占了资源，实际上是共享的。**

| 名称 | 让谁以为 | 独占了什么 | 实际上 |
| ---- | -------- | ---------- | ------ |
| 虚拟内存 | 每个进程 | 一整片连续内存 | 操作系统把虚拟地址翻译成物理地址，不够时借用硬盘（swap） |
| venv | 项目 | 一套 Python | 借用已有的解释器和标准库，只独有 site-packages |
| 虚拟机 | 一个操作系统 | 一台完整的电脑 | Hypervisor 模拟硬件，多台 VM 共享物理机 |

- 后续联系：`top` 里的 `VIRT` / `RES`（Lesson 2）；云主机通常是虚拟机；Docker 容器介于 venv 和 VM 之间（Lesson 5）

---

## 知识点 10：venv 与 conda

| | 真实安装 | venv | conda env |
| - | -------- | ---- | --------- |
| 解释器 + 标准库 | 完整一份 | **借用**底座 Python | 各自完整一份 |
| 第三方包 | 共用 | 独有 | 独有 |
| 位置 | 系统目录 | 项目内 `.venv/` | `conda/envs/<name>/` |

- `.venv/pyvenv.cfg` 里的 `home = ...` 指向底座 Python
- 本项目的底座是 conda **Ding** 环境的 Python 3.9.13 → **不要删除 Ding 环境**
- 激活的本质：修改当前 shell 的 PATH，让 `python` 先找到 `.venv` 里的那个
- 两个环境同时激活时（`(.venv) (Ding)`），后激活的排在 PATH 前面；建议先 `conda deactivate`

### 为什么 .venv 不提交到 Git

- 体积大（几百 MB）
- 不跨平台（Windows `.exe` / `.dll` 在 Linux 上无法运行）
- 包含本机绝对路径

→ 只提交清单 `requirements.txt`，任何机器照单重建。

---

## 知识点 11：依赖与 requirements.txt

- **依赖（dependency）**：包 A 需要用到包 B
- **传递依赖（transitive dependency）**：A → B → C，层层传递。例：pandas → python-dateutil → six
- 依赖是一张**网**：ortools 本身也依赖 pandas（`pip show pandas` 的 `Required-by: ortools`）
- 本课装了 3 个包，`pip list` 出现 21 个

完整列表会随**平台**和 **Python 版本**变化：

| 包 | 原因 |
| -- | ---- |
| `colorama` | 只在 Windows 上安装 |
| `tomli`、`exceptiongroup` | **backport**：给 Python < 3.11 补上新版本的内置功能 |
| `numpy 2.0.2` | 最后一个支持 Python 3.9 的系列，pip 自动选择 |

→ “我电脑上能跑、服务器上不行”时，先对比两边的 `pip list`。

### 写什么进 requirements.txt

| 方案 | 优点 | 缺点 |
| ---- | ---- | ---- |
| 只写直接依赖 | 清晰、跨平台 | 传递依赖版本可能漂移 |
| `pip freeze` 全部锁定 | 精确复现 | 混入平台特有的包，分不清谁是真正需要的 |

工业界：直接依赖文件 + 自动生成的 **lock file**（pip-tools / uv / poetry）。
本项目：只写 3 个直接依赖，并用 `==` 锁定版本。

```text
pandas==2.3.3     # 精确等于
pandas>=2.3       # 大于等于
pandas~=2.3.3     # 兼容版本：≥2.3.3 且 <2.4
```

常用命令：

```bash
python -m pip install -r requirements.txt   # -r = --requirement
pip list                                     # 已装的包
pip show pandas                              # 某个包的依赖（Requires）和被谁依赖（Required-by）
```

---

## 知识点 12：看不见的字符

用 `cat -A 文件名` 显示不可见字符：`^M` = `\r`，`$` = `\n`。

| 系统 | 换行符 | 名称 |
| ---- | ------ | ---- |
| Windows | `\r\n` | CRLF |
| Linux / macOS | `\n` | LF |

- 名字来自打字机：**C**arriage **R**eturn（打字头回到行首）+ **L**ine **F**eed（纸卷一行）
- Git 提示 `LF will be replaced by CRLF` 就是在两种格式之间自动转换
- 隐患：CRLF 的 shell 脚本在 Linux 上会运行失败（Lesson 2 处理）
- Unix 约定：**每一行都以换行符结尾，包括最后一行**；否则 `git diff` 显示 `\ No newline at end of file`
- VS Code 设置 `files.insertFinalNewline` 可以自动补齐

---

## 知识点 13：环境变量与 .env

- **环境变量**：进程启动时携带的一组“键=值”，是操作系统给进程的配置表（如 `PATH`）。叫“环境”是因为它描述的是程序**运行时所处的环境**，而不是代码本身
- 用途：传递**密钥**（API Key）和**随环境变化的配置**（求解时间上限、日志级别）
- **`.env`**：本地开发时集中存放环境变量的文件，含真实密钥，**绝不提交**
- **`.env.example`**：只有变量名、没有真实值的模板，**提交**，告诉别人需要配置哪些变量
- 格式：`KEY=value`，**等号两边不能有空格**（bash 语法）
- 文件名以 `.` 开头 = Unix 隐藏文件，`ls -a` 才能看到

---

## 踩过的坑

| 现象 | 出问题的层 | 原因 | 收获 |
| ---- | ---------- | ---- | ---- |
| `which : The term 'which' is not recognized` | Shell | 在 PowerShell 里执行了 bash 命令 | 先确认自己在哪个 shell；`CommandNotFoundException` 表示 shell 找不到这个命令，与 Python 无关 |
| 提示符前有 `(Ding)` | 环境 | VS Code 自动激活了 conda 环境 | 括号表示已激活的环境；用 `which python` 确认实际用的是哪个 |
| 以为 `.env.example` 被忽略了 | 读输出 | 没注意 `check-ignore -v` 输出中的 `!` | 输出要逐字符读懂，不能只看“有输出” |
| 第一个 commit 的说明带着引号 `"docs: ..."` | Git | 引号被当成了说明内容的一部分 | 说明里的引号只用于在 shell 中包住带空格的文本，不应出现在最终说明里 |

---

## 命令速查

```bash
# Git
git status / git status -s / git status -uall
git add <文件> / git add .
git diff --staged --stat
git commit -m "type: message"
git log --oneline
git push
git check-ignore -v <文件>

# 环境
which python
python --version
python -m venv .venv
source .venv/Scripts/activate      # 在项目根目录执行；Linux 上是 .venv/bin/activate
deactivate                          # 退出 venv（激活脚本临时定义的 shell 函数）
conda deactivate                    # 退出 conda 环境
# VS Code：Ctrl+Shift+P → Python: Select Interpreter → 选 .venv，新终端自动激活
python -m pip install -r requirements.txt
pip list / pip show <包>

# 文件
touch <文件>                        # 创建空文件
cat -A <文件>                       # 显示不可见字符
ls -a                               # 显示隐藏文件
```

---

## 留到后面的问题

- PATH 和环境变量的完整机制、子进程继承 → Lesson 2
- 服务器上的 Python 版本、pip list 与本地的差异 → Lesson 2
- CRLF 对 shell 脚本的影响 → Lesson 2
- Docker 如何解决 venv 解决不了的问题 → Lesson 5
- 分支、PR、合并 → Lesson 0 最后一步
