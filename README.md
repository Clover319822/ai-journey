# ai-journey

> 我做过 7 年连锁餐饮门店管理，2 年跨境电商，现在做 AI 落地——
> 我比纯工程师更懂业务现场，比业务方更懂怎么把 AI 落进流程。

31 岁，全日制大专，零编程基础。从 **2026-10-10** 起，用 8 周（约 450 小时）从零转行 AI，
目标岗位是 **FDE（Forward Deployed Engineer，前置部署工程师）**。

这是一个全程公开的学习与作品仓库。所有 commit 都是真实进度，不做补录。

---

## 为什么敢押这个方向

全中国能写 Agent 的人很多，能在餐厅闭餐后跟店长聊明白他到底需要什么的人很少。
我的差异化不在"学会 AI"，而在 **AI × 餐饮/零售运营** 这个交叉点上。

| 我有的 | 我要补的 |
|---|---|
| 7 年门店全盘运营、排班与人力成本、订货与库存 | 工程能力：Python / Git / API / 系统集成 |
| 高压现场决策、客诉升级、跨部门对齐 KPI | 模型能力：Prompt / RAG / Agent / Eval |
| 2 年 TEMU 选品、核价、备货、平台合规 | 交付能力：Docker / 部署 / 可观测性 |

---

## 8 周路线

| 周 | 主题 | 周末产出 |
|---|---|---|
| W1 | 工程地基：Python + Git + HTTP/API | 批量改写 50 条 TEMU listing 的脚本 |
| W2 | LLM 核心：Prompt / 结构化输出 / Tool Use | Listing 生成器 + 违规词检测（严格 JSON） |
| W3 | RAG：Embedding / Chunking / Chroma | **【作品 A】餐饮运营知识库 RAG** |
| W4 | Agent：手写 ReAct → LangGraph → MCP | 作品 A 升级为可执行 Agent |
| W5 | 工程化与评估：Eval / Langfuse / Docker / 上线 | 作品 A 部署到公网 |
| W6 | **【作品 B】餐饮门店运营 Agent**（杀手锏） | 排班 / 订货 / 客诉 / 值班日报 |
| W7 | **【作品 C】跨境电商运营 Agent** | 选品 / Listing 多语言 / 备货提醒 + demo 视频 |
| W8 | 包装与投递 | 3 个仓库 README + 技术文章 + 开始投递 |

技术栈：Python · Anthropic Claude (+ DeepSeek 对照) · LangGraph · Chroma · Streamlit · MCP · Langfuse · Docker

---

## 铁律

- **每天必须有 commit**，两个月后要有 150+ 绿点
- **每周必须有可运行的东西**，不接受"看了课"
- 卡超过 4 小时就换路径，不死磕
- 所有作品必须有 eval 数据，不能只说自己"效果不错"

---

## 进度

| 日期 | 状态 |
|---|---|
| 2026-10-10 (Day 1) | 环境全通：GitHub + SSH + Python/uv + 4 个 commit；**跑通第一个真实大模型调用**（DeepSeek 改写 TEMU listing，147/17 token） |
