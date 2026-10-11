# Day 2 · 2026-10-11

## 今天完成

- CS50P 第 0 课核心概念理解：字符串、`print()`/`input()` 区别、函数定义与调用
- 在 VS Code 中跑通第一个 Python 函数 `test.py`：输入中文标题，返回字符长度
- 跑通 `week01/list_rewrite.py`：批量改写 8 条 TEMU 抱枕套 listing，输出到 `output.xlsx`
- 建立 `docs/` 目录，把学习计划固化到仓库内

## 关键产出

- `test.py`：第一个函数练习
- `week01/list_rewrite.py`：批量改写 + 质量检查 + Excel 导出
- `docs/Day02-任务清单.md`、`docs/Day02-手把手步骤-白话版.md`
- `requirements.txt` 增加 `openpyxl`

## 运行数据

- 供应商：DeepSeek `deepseek-chat`
- 8 条 listing，总耗时 5.7 秒，平均每条 0.7 秒
- 输入 token：1558 / 输出 token：158
- 三项检查全过：6/8 条

## 不过的那 2 条（第一个 badcase）

1. **第 3 条（羊羔绒 / 50x50cm）**
   - 输出：`Faux Fur Throw Pillow Cover 50x50cm Winter Warm Sofa Cushion Case with Zipper Insert Not Included`
   - 长度 97，超 80 字符限制
   - 材质词 `Faux Fur` 不在检查词表里，但 `Faux Fur` 其实是合理译法，说明检查规则需要放宽

2. **第 5 条（水晶绒 / 35x35cm）**
   - 输出：`Kids Cartoon Throw Pillow Cover 35x35cm Crystal Velvet Animal Insert Not Included`
   - 长度 81，只超 1 个字符
   - 边界情况，prompt 需要更强的长度约束

## 今天踩的坑

- VS Code 必须先"打开文件夹"才能识别 `.venv` 和项目配置
- `.py` / `.json` / `.md` 文件类型要分清，不要把 Python 代码写进 settings.json
- 新建文件后必须 `Ctrl+S` 保存再运行

## 明天

- 把 6/8 改成 8/8：优化 prompt 长度约束、放宽材质检查规则
- CS50P 第 1 课：条件判断、循环
