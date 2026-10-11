# Day 2 · 2026-10-11（周日）· 补救清单

> **22:58 更新**：Key 拿到并充值，22:47 跑通第一次真实调用。最大卡点清了。
> 仍缺 `list_rewrite.py` 和 `output.xlsx`。明天目标：**8 条批量跑完，补上验收物。**

---

## 〇、22:47 的真实调用结果

```
供应商 : DeepSeek
模型   : deepseek-chat
原标题 : 新款简约现代抱枕套 客厅沙发靠垫套 45x45cm 不含芯
改写后 : Modern Throw Pillow Cover 45x45cm for Couch Sofa Living Room
输入 token: 147 / 输出 token: 17
```

**这是今天唯一真正值钱的产出。** 不是代码，是你写的复盘：

- `Throw Pillow Cover` 比 `Cushion Cover` 北美搜索量高
- 没写"不含芯"（Insert Not Included）会显著增加退货纠纷

这两句只有做过 2 年 TEMU 的人才写得出来。**培训班教不出来，这就是你的护城河。**
第 7 周作品 C 的 README 里，把这两句原样放进去。

---

## 一、Day 1 交付核对（截至 22:58）

| 项 | 要求 | 实际 | 判定 |
|---|---|---|---|
| commit 数 | ≥ 4 | 7 个，全部已 push | 过 |
| 环境 | Python / uv / Git 装好 | 装好，还踩出 4 个坑 | 过 |
| 笔记 | `notes/day01.md` | 质量很高，4 个坑 + 一次输出复盘 | 过 |
| 示例数据 | 5 条 TEMU 标题 | `sample/listings_sample.csv` 8 条 | 过 |
| **API 真实调用** | 调通一次 | **22:47 跑通，DeepSeek deepseek-chat** | **过** |
| **`list_rewrite.py`** | 能跑的批量改写脚本 | **文件不存在** | **没过** |
| **`output.xlsx`** | 改写结果导出 | **文件不存在** | **没过** |
| CS50P 第 0 课 | 看完 + 手敲 | 没做 | 没过 |

**一句话**：白天耗在环境上，晚上把最关键的一关拿下了。欠账从「没跟 AI 说过话」缩到「只说了 1 句，该说 8 句」。

---

## 二、今天三件事（按顺序，别跳）

### 第 1 件：写 `list_rewrite.py`，8 条批量跑（上午）

**关键修正 —— 你复盘说"没写材质、没写数量"，根因不在 prompt，在输入。**

你只喂了 `title_cn` 一列。但 `listings_sample.csv` 里还有 `size` 和 `material` 两列，
你压根没传给模型。**模型不知道材质是涤麻还是羊羔绒，它怎么写得出来？**

所以明天这样改：

- 新建 `week01/list_rewrite.py`
- 读 CSV 时把 **三列一起读出来**：`title_cn` + `size` + `material`
- 拼进 prompt，例如：`标题：xxx / 材质：羊羔绒 / 尺寸：50x50cm`
- prompt 里再加明确要求：
  - 材质必须出现（用英文面料词：Linen / Cotton Linen / Sherpa / Oxford Cloth）
  - 不含芯必须翻成 `Insert Not Included`（你自己的复盘第 4 条）
  - 品类词用 `Throw Pillow Cover`，不要用 `Cushion Cover`
- **循环**调 8 次，逐条打印 `原标题 → 新标题`

先别追求完美。**跑通 8 条 > 精调 1 条。**

顺手补 CS50P 第 0 课（函数 + 字符串），**每个例子手敲一遍**，正好用来写这个脚本。

### 第 2 件：装 openpyxl，跑通 8 条，导出 Excel（下午）

```bash
.venv\Scripts\python.exe -m pip install openpyxl
```

8 条结果写进 `output.xlsx`，列：原标题 / 材质 / 尺寸 / 改写后标题。
然后在 `notes/day02.md` 里写：

1. 8 条一共花了多少钱、多少 token
2. 平均每条耗时
3. 加了 size/material 之后，输出比昨晚那条好在哪（**这条是 eval 的雏形，第 5 周要用**）

最后 push。

### 第 3 件：算账 + 复盘 + push（晚上 2h）

1. `notes/day02.md` 补三件事：
   - 8 条一共花了多少 token、多少钱、平均每条耗时
   - 加了 size/material 之后，输出比昨晚那条好在哪（**这是 eval 的雏形，第 5 周要拿来用**）
   - 哪几条改得烂，为什么（后面做 prompt 优化要用）
2. `git add . && git commit -m "..." && git push`（**用 noreply 邮箱提交**）
3. 收工前把 `output.xlsx` 打开看一眼，确认 8 行都在

---

## 三、今日验收（还是一条，过不了就是没完成）

> `week01/list_rewrite.py` 能跑，喂它 `listings_sample.csv` 的 8 条（含 size + material），
> 吐出一个 `output.xlsx`，屏幕上不报错，`notes/day02.md` 里写着花了多少 token。

**Day 1 和 Day 2 的账一起还。** 明天晚上我按这条验收。

---

## 四、今天卡住的技术点（下次直接带过来问）

这些是你今天踩过的，已经记在 `notes/day01.md` 里。明天遇到相关的问题，
**直接把报错信息整段粘过来**，别自己闷头查：

1. ~~**API Key 完全没配**~~ —— **22:32 已写入 `.env`，22:47 跑通。此项关闭。**
2. **GitHub 网页间歇性超时** —— 不是封死，重试即可。改 hosts / 镜像站全部无效，别再试了。
3. **`git rebase --root --exec` 会删掉整个 `.git`** —— 这台机器上永远别用。要改历史作者用 `git filter-repo`。
4. **开启邮箱隐私后 push 被拒** —— 必须用 noreply 邮箱提交。
5. **git 配置三级覆盖** —— 查生效值用不带 `--global` 的 `git config user.email`。
6. **PATH 里第一个 python 不是你的** —— 装包一律用 `E:/Python/python.exe -m pip install` 或 `.venv\Scripts\python.exe`。

---

## 五、一句提醒

第 1 周还剩 5 天，周末作业是「批量改 50 条 listing」。
明天的 8 条跑通，周末的 50 条就是把 `8` 换成 `50`，一行的事。

**今晚别熬了。** 你已经连着干了 13 个小时，从装环境到第一次真实调用。
8 周是长跑，不是一口气。今晚睡，明早起来第一件事就是那 8 条。
