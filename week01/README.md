# 第 1 周 · 工程地基

**目标**：能写代码、能提交、能调通任意 HTTP API。

## 本周清单

- [x] Git / GitHub 打通（Day 1）
- [x] 装好 Python 环境与 uv
- [ ] Python 基础：数据类型、控制流、函数、文件读写、异常处理
- [ ] `requests` 库：能自己发 HTTP 请求
- [ ] HTTP / REST / JSON 概念
- [ ] `async/await` 概念（先懂是什么，不要求写）
- [ ] 注册 Anthropic / DeepSeek API

## 周末产出

**一个脚本：批量调大模型 API 改写 50 条 TEMU listing 标题，输出到 Excel。**

已经铺好的东西：

| 文件 | 用途 |
|---|---|
| `week01/hello_llm.py` | 单条改写，最小可运行版本（Day 1 已跑通冒烟测试） |
| `../sample/listings_sample.csv` | 8 条真实格式的抱枕套标题样本，周末脚本直接读它扩展 |
| `../.env.example` | Key 配置模板，复制成 `.env` 后填 |

周末要做的就是把 `hello_llm.py` 从"改 1 条"扩展到"改 50 条 + 写进 Excel"。

## 踩坑记录

见 `../notes/day01.md`。

## 常用命令

```bash
# 装依赖（PyPI 很慢，长安装放后台跑）
uv pip install --python .venv/Scripts/python.exe <包名>

# 运行脚本
.venv\Scripts\python.exe week01/hello_llm.py

# 提交
git add -A && git commit -m "..." && git push
```
