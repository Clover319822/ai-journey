# Day 5 · 2026-10-14（周三）· 今日任务

> 核对依据：`D:\ai-journey` 的实际文件与 git log，不看口头汇报。

---

## 一、先摆事实

| 项 | 状态 |
|---|---|
| 最新 commit | `7b1757e`，停在 **2026-10-11 21:31**（Day 2） |
| Day 3（10-12）commit | **0** |
| Day 4（10-13）commit | **0** |
| 累计 commit | 11 个，全部来自 10-10、10-11 两天 |
| 今天是 | Day 5，第 1 周还剩 3 天（Day 5/6/7） |

**连着两天空白。** 第 1 周的周末产出（50 条批量改写 → Excel）现在一件没动。

已经替你做掉的一步：`sample/listings_sample.csv` 已经从 8 条扩到 **50 条**（新增 `sample/make_50.py`，跑过了，50 行 + 表头）。这一步你不用再花时间。

---

## 二、今日主题

**第 1 周：工程地基 —— 收尾冲刺**

今天不学新模块。目标只有一个：把第 1 周的周末产出提前到今天做完，明天 Day 6 才有资格碰 async/await 和 HTTP/JSON。

---

## 三、任务拆分

现在 15:30，今天实际只剩约 6 小时。按这个切：

### 第一段：还两笔旧账（15:30 – 16:00，30 分钟）

**1. 让 `output.xlsx` 能进仓库**
`.gitignore` 第 22 行的 `*.xlsx` 把验收产物挡在外面。在 `.gitignore` 最后加一行：

```
!output.xlsx
```

**2. 补 `ANTHROPIC_API_KEY`**
`.env` 里现在只有 `ANTHROPIC_MODEL`，没有 Key，所以脚本一直在静默走 DeepSeek。
第 2 周要做成本对照，今天先把 Key 补上（没有的话就跳过，继续用 DeepSeek，但要在笔记里写清楚）。

```bash
cd /d/ai-journey
.venv/Scripts/python.exe set_key.py ANTHROPIC_API_KEY sk-ant-你的key
```

### 第二段：CS50P 第 1 课手敲（16:00 – 16:45，45 分钟）

不看视频，只敲代码。就三个例子，敲完就停：

1. 写一个 `def`，接收一个标题字符串，返回它的字符数
2. 给这个函数加参数校验：输入不是字符串就 `raise ValueError`
3. 用 `try / except` 包住调用，打印错误类型

存成 `week01/day05_functions.py`，commit 一次。

### 第三段：改脚本 + 跑 50 条（16:45 – 19:30，约 3 小时）

打开 `week01/list_rewrite.py`，改三处：

**① `MATERIAL_EN["羊羔绒"]` 加上 `"Faux Fur"`**
现在是 `["Sherpa", "Fleece"]`，模型译成人造毛皮时会被误判不合格。
改成 `["Sherpa", "Fleece", "Faux Fur"]`。

**② 失败的条要重试一次**
现在第 228 行失败就直接 `continue`，那条会**悄悄消失**——50 条跑完你以为 50 条，实际可能只有 43 条。
在 `rewrite_one` 外面套一层：失败就等 2 秒再试一次，还失败才记进来，并标成 `调用失败`。

**③ 超长的标题要重跑，不要硬截断**
长度 > 80 时，再调一次模型，prompt 里追加一句："上一条超了 80 字符，请压缩到 80 字符以内，完整单词结尾，不要从单词中间切断。"
重跑最多 2 次，还超就在 Excel 里标"否"，不要手动截。

改完跑：

```bash
cd /d/ai-journey
.venv/Scripts/python.exe week01/list_rewrite.py
```

跑成功的标志：最后几行打印 `完成 50 条` 和 `三项检查全过 X/50`。

### 第四段：首次 Git 分支 + PR（19:30 – 20:30，1 小时）

**不要直接往 `main` 上推。** 走一遍真实流程：

```bash
cd /d/ai-journey
git checkout -b feat/batch-50
git add -A
git commit -m "Day 5: 50 条批量改写跑通，加材质词典、失败重试与超长重跑"
git push -u origin feat/batch-50
```

然后浏览器打开 GitHub 仓库 → 会出现黄色提示条 → 点 **Compare & pull request** → 填标题 → **Create pull request** → **Merge pull request** → 回本地：

```bash
git checkout main
git pull
```

### 第五段：写笔记 + 收工 commit（20:30 – 21:30，1 小时）

新建 `notes/day05.md`，把跑批最后打印的那几个数字抄进去：

- 供应商 / 模型
- 总耗时、平均每条耗时
- 输入/输出 token 合计（估算花费）
- 三项检查通过率 X/50
- 今天卡住的地方

然后：

```bash
git add -A && git commit -m "Day 5 收工：50 条批量改写 + 首次 PR" && git push
```

---

## 四、今日必须交付的产出物（一个）

> **GitHub 仓库 `ai-journey` 的 `main` 分支里能看到 `output.xlsx`：50 行数据，三项自检通过率 ≥ 90%，并且仓库里有一条已 merge 的 PR 记录。**

只看到本地文件不算。要能在 GitHub 网页上打开。

---

## 五、红线

- 今天不许装新包（PyPI 下载慢，会卡住）
- 今天不碰 async/await、不碰 RAG、不碰第 2 周内容
- 卡超过 4 小时就换路径，把报错整段发出来

---

晚上我会来收进度。
