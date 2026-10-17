# Day 7 收工核对 + Day 8 任务清单

> 生成时间：2026-10-16 21:40 ｜ Day 7（第 1 周最后一天）
> 核验依据：`D:\ai-journey` 的 git log / git status / 文件 mtime，不看口头汇报

---

## 一、今天（Day 7）逐项核对

| # | 今早要求 | 证据 | 判定 |
|---|---|---|---|
| 1 | 3 个语义化 commit | `git log` 最新仍停在 `7b1757e`（10-11 21:31） | ✗ **0 个** |
| 2 | 首次分支 + PR | `git branch -a` 只有 `main`；`git ls-remote` 远程也只有 `main` | ✗ |
| 3 | `.gitignore` 放行 demo CSV | `git check-ignore week02/data/demo_skus.csv` → 命中 `.gitignore:23:*.csv` | ✗ |
| 4 | GitHub 上能看到 temu_copilot.py | 文件仍为 `??` 未跟踪状态 | ✗ |
| 5 | 今天有实际产出 | `week02/output/上架评估卡-20261016-0949.md`（09:49 生成） | ✓（但只是重跑） |

**今天唯一的动作**：09:49 跑了一次 `temu_copilot.py --no-ai`，输出一张评估卡。
内容和 10-15 那张**逐字节相同**（只有标题时间戳不同）。之后到 21:40，12 小时无动静。

---

## 二、判定

**第 1 周内容层面：超额完成。**
`week02/temu_copilot.py` 479 行、14 个函数/类、有 CostModel 类、argparse CLI、CSV 批量、交互菜单、LLM 降级。这是第 2 周水平的东西，第 1 周就写出来了。

**第 1 周工程习惯层面：不及格。**
Day 3 / 4 / 5 / 6 / 7 连续 **5 天 0 commit**。479 行代码在硬盘上裸奔两天，没进过版本库。
GitHub 主页对外还是"11 个 commit，最后更新 6 天前"——**别人打开你的主页看到的是这个**。

四天了，问题已经不是"不会"，是"没做"。你会写 479 行脚本，不可能不会敲 `git add`。

---

## 三、Day 8（2026-10-17，第 2 周第 1 天）只做一件事

### 一件事：把已有的东西交上去。目标 3 个 commit。

**准备动作（5 分钟，做一次）**

打开文件管理器，进 `D:\ai-journey`，确认能看见 `commit.bat`。
双击它 → 黑窗口让你写一句说明 → 写完回车 → 它自动 add + commit + push。

> 这个 bat 是我刚写的，替你省掉三条命令。以后每天收工就是双击一次。

---

### Commit 1：放开 demo CSV（让 clone 的人能跑）

打开 `D:\ai-journey\.gitignore`，找到最后一行的位置，在文件末尾**追加这两行**：

```
!week02/data/*.csv
!output.xlsx
```

存盘（Ctrl+S）。

双击 `commit.bat`，说明写：
```
fix: 放行 week02 演示数据与 output.xlsx，clone 后可直接运行
```

**验证**：跑完去 https://github.com/Clover319822/ai-journey/tree/main/week02/data
能看到 `demo_skus.csv` 就算过。

---

### Commit 2：提交 temu_copilot 主程序 + 两张评估卡

双击 `commit.bat`，说明写：
```
feat: TEMU 上架评估助手，成本测算 + 报价建议 + 盈亏平衡
```

**验证**：https://github.com/Clover319822/ai-journey/tree/main/week02
能看到 `temu_copilot.py` 和一个 `output/` 目录。

---

### Commit 3：补文档（README 里写清楚它解决什么问题）

在 `D:\ai-journey` 根目录新建 `week02/README.md`，内容照抄下面这段（可以自己改）：

```markdown
# TEMU 上架评估助手

## 解决什么问题
TEMU 全托管卖家报供货价时，最怕报低了亏、报高了买手不收。
这个工具把"进货价 + 物流 + 包材 + 退货损耗"算成一张卡片，直接给出：
盈亏平衡供货价 / 建议报价 / 让价底线 / 占前台价比例。

## 业务规则从哪来
来自我 2 年 TEMU 全托管实操的核价逻辑，不是通用的成本计算器。

## 怎么跑
uv run python week02/temu_copilot.py --demo --no-ai
```

双击 `commit.bat`，说明写：
```
docs: 补充 week02 README，说明业务规则来源与运行方式
```

---

## 四、明确不做（今天别碰）

- ❌ 不学新东西。第 2 周的 Prompt Engineering 明天先不开。
- ❌ 不写新代码，temu_copilot.py 一行都不用改。
- ❌ 不做分支和 PR。今天只要 main 上有东西就行。
- ❌ 不补 `notes/day05.md`、`day06.md`、`day07.md`。欠着。
- ❌ 不碰 `week01/list_rewrite.py` 和 `output.xlsx` 的遗留问题（Faux Fur 词典、超长重跑）。
  第 1 周验收口径已改为 temu_copilot.py，那两个降级为"以后再说"。

**今天就三个双击。** 全部做完预计 20 分钟。

---

## 五、验收标准（明天晚上我照这个查）

1. GitHub `Clover319822/ai-journey` 主页显示**最后更新时间 = 2026-10-17**
2. commit 总数 ≥ 14（现在 11）
3. `week02/temu_copilot.py`、`week02/data/demo_skus.csv`、`week02/README.md` 三个文件在网页上能点开
4. 本地 `git status --short` 只剩少量未跟踪文件，不能有 479 行的 `.py` 还挂着 `??`

---

## 六、今天记下的技术卡点（下次带过来问我）

1. **`.gitignore` 的 `*.csv` 是全局忽略**，只白名单了 `!sample/*.csv`。
   所以 `week02/data/demo_skus.csv` 被挡住了，别人 clone 后 `--demo` 会报错找不到文件。
   → 这是"gitignore 白名单要写到具体路径"的典型坑，明天第 3 项会解掉。

2. **今天跑的是 `--no-ai` 模式**，评估卡上写着"（--no-ai 模式：只做了成本测算）"。
   说明 LLM 那段（标题生成 / 卖点文案 / 风险提示）**这两天一次都没真正跑过**。
   → 交上去之前最好带 AI 跑一次，确认整条链路是通的。明天有空就试一次，跑不通把报错整段发我。

3. **`.env` 里仍然只有 `ANTHROPIC_MODEL`，没有 `ANTHROPIC_API_KEY`**。
   所以脚本一直在静默降级走 DeepSeek。不是 bug，但你要知道现在烧的是 DeepSeek 的钱。

4. **479 行代码两天没进版本库**——这是流程问题不是技术问题，但风险等级最高。
   硬盘坏了、误删了、改崩了回不去。明天必须解决。

---

*一句话：内容你已经跑到第 2 周了，GitHub 主页还停在 Day 2。明天只补这 6 天的距离。*
