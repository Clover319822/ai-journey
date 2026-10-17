# Day 6 · 2026-10-15（周四）· 收工核对与补救清单

> 判定依据：`D:\ai-journey` 的实际文件与 git log。不看口头汇报。

---

## 一、Day 5 核对结果：未完成

| 今日任务 | 要求 | 实际 | 判定 |
|---|---|---|---|
| `.gitignore` 加 `!output.xlsx` | 加一行 | 未改（mtime 仍是 10-10） | ✗ |
| `.env` 补 `ANTHROPIC_API_KEY` | 有 Key | 仍只有 `ANTHROPIC_MODEL` | ✗ |
| `week01/day05_functions.py` | 新建并 commit | 文件不存在 | ✗ |
| `list_rewrite.py` 加 `Faux Fur` | 改 1 行 | 57 行仍是 `["Sherpa", "Fleece"]` | ✗ |
| `list_rewrite.py` 失败重试 | 加一层重试 | 229 行仍是裸 `continue` | ✗ |
| 跑 50 条 → `output.xlsx` | 50 行 | **仍是 9 行（8 条）**，mtime 停在 10-11 21:29 | ✗ |
| 建分支 + 提 PR | `feat/batch-50` | 分支不存在，远程只有 `main` | ✗ |
| `notes/day05.md` | 新建 | 不存在 | ✗ |
| 今日 commit | ≥ 1 | **0** | ✗ |

**今天仓库里被改动的 3 个文件，全是早上自动推送代你做的**（15:29–15:30，`make_50.py` / CSV 扩到 50 条 / 这份任务清单）。你自己一个字节都没动。

**连续第 3 天空白。** Day 3（10-12）、Day 4（10-13）、Day 5（10-14）都是 0 commit。
最新 commit 停在 `7b1757e`，2026-10-11 21:31。整整 72 小时没有任何提交。

---

## 二、直说三句

1. Day 1、Day 2 你干得比大多数转行的人好——11 个 commit、API 跑通、还自己加了自检列。所以这不是能力问题。
2. 但 Day 5 的任务清单我写错了：5 个阶段、6 小时、还要学分支和 PR。给一个刚摸命令行 3 天的人排这种密度，是我的责任。
3. 明天只做一件事，做完就算赢。剩下的全部降级。

---

## 三、Day 6 只做一件事

> **让 GitHub 网页上能打开 `output.xlsx`，并且是 50 行。**

拆成 4 个动作，每个不超过 45 分钟。**做完一个 commit 一次**，今天目标是 2 个 commit。

### 动作 1：让产物能进仓库（10 分钟）

用 VS Code 打开 `D:\ai-journey\.gitignore`，在**最后一行**加：

```
!output.xlsx
```

加完在终端跑一句验证（看到 `output.xlsx` 出现就算对）：

```bash
cd /d/ai-journey && git check-ignore -v output.xlsx ; echo "退出码 $?"
```

如果什么都不打印、退出码是 1，说明白名单生效了。

### 动作 2：改一行代码（10 分钟）

`week01/list_rewrite.py` 第 57 行，把：

```python
    "羊羔绒": ["Sherpa", "Fleece"],
```

改成：

```python
    "羊羔绒": ["Sherpa", "Fleece", "Faux Fur"],
```

改完立刻 commit：

```bash
git add -A && git commit -m "Day 6: 材质词典补 Faux Fur，output.xlsx 解除忽略" && git push
```

### 动作 3：加失败重试（45 分钟，可选但强烈建议）

把 `week01/list_rewrite.py` 第 225–229 行这一整段：

```python
        try:
            new_title, tin, tout = rewrite_one(client, kind, model, row)
        except Exception as e:
            print(f"[{i}] 调用失败：{type(e).__name__}: {e}")
            continue
```

整段替换成：

```python
        new_title = tin = tout = None
        for attempt in (1, 2):
            try:
                new_title, tin, tout = rewrite_one(client, kind, model, row)
                break
            except Exception as e:
                print(f"[{i}] 第 {attempt} 次调用失败：{type(e).__name__}: {e}")
                if attempt == 1:
                    time.sleep(2)
        if new_title is None:
            print(f"[{i}] 两次都失败，这条跳过")
            continue
```

> 卡在这里超过 40 分钟就**直接跳过动作 3**，去跑动作 4。少几条不影响验收。

### 动作 4：跑 50 条 + 推上去（60 分钟）

```bash
cd /d/ai-journey
.venv/Scripts/python.exe week01/list_rewrite.py
```

跑成功的标志：最后打印 `完成 50 条` 和 `三项检查全过 X/50`。

然后：

```bash
git add -A && git commit -m "Day 6: 50 条批量改写跑通，产物入库" && git push
```

**验收**：浏览器打开 `https://github.com/Clover319822/ai-journey`，能看到 `output.xlsx`，点进去是 50 行。
看不到就不算完成——本地有文件没用。

---

## 四、今天明确不做的事

- 不做分支、不做 PR（推 `main` 就行，Day 7 再学分支）
- 不补 `notes/day05.md`、不写 `day06.md`（明天补，先把东西跑出来）
- 不碰 async/await、不碰第 2 周内容、不装任何新包
- 不修"超长标题重跑"那条——超了就在表里标"否"，Day 7 再说

---

## 五、卡住的技术点（下次带着来问）

| # | 卡点 | 一句话解释 |
|---|---|---|
| 1 | `.gitignore` 的 `!` 白名单 | `*.xlsx` 会把验收产物一起挡在外面，要在文件**末尾**再加一行 `!output.xlsx` 才能放它进来 |
| 2 | 失败重试写法 | 在 `try` 外面套 `for attempt in (1, 2)`，两次都失败才 `continue`，否则那条会静默消失、条数对不上 |
| 3 | CSV 的 BOM | 必须用 `encoding="utf-8-sig"` 读，用 `utf-8` 第一列列名会变成 `\ufeffid` |
| 4 | `.env` 静默降级 | `.env` 里只有 `ANTHROPIC_MODEL` 没有 `ANTHROPIC_API_KEY`，脚本会不报错地改用 DeepSeek。每次跑之前看一眼打印出来的"供应商"那行 |
| 5 | `git check-ignore` | 验证某个文件到底有没有被忽略，比肉眼看 `.gitignore` 准 |

---

## 六、明天晚上我来收的作业（就这两条）

1. GitHub 网页上 `output.xlsx` 是 **50 行**
2. 今天有 **≥ 2 个 commit**

一条没做到，我照实写进记录。

---

*第 1 周只剩 Day 6、Day 7 两天。周末产出（50 条批量改写 → Excel）本来该是 Day 7 交。今天把它做掉，Day 7 才有资格收尾第 1 周。*
