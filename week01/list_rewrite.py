"""
第 1 周 · Day 2 —— 批量 listing 改写脚本

昨天（Day 1）只改了 1 条。今天改 8 条，并把结果导出成 Excel。

和昨天的 hello_llm.py 比，今天多了三件事：
  1. 从 CSV 文件里读数据（昨天是写在代码里的一个字符串）
  2. 循环调用 8 次（昨天只调 1 次）
  3. 把结果写进 output.xlsx（昨天只打印在屏幕上）
  4. 顺手检查每条结果合不合格（材质有没有翻译？长度超没超？）—— 这是第 5 周 eval 的雏形

为什么昨天那条输出缺材质、缺数量：
  不是 prompt 的锅。是 CSV 里的 size 和 material 两列压根没喂给模型。
  模型不知道这条是"涤麻"还是"羊羔绒"，它怎么写得出来？
  今天把三列一起喂进去。

运行：
    uv run python week01/list_rewrite.py
"""

import csv
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# 这两个往上两级才是仓库根目录 D:\ai-journey
# 这样不管你在哪个目录下运行脚本，都能找到 .env 和 sample 文件夹
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

CSV_FILE = ROOT / "sample" / "listings_sample.csv"
OUT_FILE = ROOT / "output.xlsx"


def get_key(name: str) -> str | None:
    """读 API Key。把 .env.example 里的占位符当成"没配"，避免拿假 Key 去调接口。"""
    value = (os.getenv(name) or "").strip()
    if not value or "xxxxx" in value:
        return None
    return value


# ---------------------------------------------------------------- 提示词

# system prompt = 给模型定身份。可以类比成上岗前跟新员工说"你是干这行的"
SYSTEM_PROMPT = (
    "你是一个跨境电商 listing 优化专家，熟悉 TEMU 平台的标题规范和北美买家的搜索习惯。"
)

# 中文材质 -> 买家真正会搜的英文面料词。模型如果译错成别的词，就算不合格。
MATERIAL_EN = {
    "涤麻": ["Linen", "Polyester"],
    "棉麻": ["Cotton Linen", "Cotton", "Linen"],
    "羊羔绒": ["Sherpa", "Fleece"],
    "牛津布": ["Oxford"],
    "水晶绒": ["Velvet", "Flannel", "Plush"],
    "提花布": ["Jacquard"],
    "亚麻": ["Linen"],
}


def build_prompt(row: dict) -> str:
    """把一行 CSV 数据拼成一段给模型看的话。

    row 就是 CSV 里的一行，长这样：
        {"id": "1", "category": "抱枕套", "title_cn": "新款简约...",
         "size": "45x45cm", "material": "涤麻"}
    """
    return f"""请把下面这条中文商品标题，改写成英文电商 listing 标题。

原标题：{row["title_cn"]}
材质：{row["material"]}
尺寸：{row["size"]}

要求：
1. 长度不超过 80 个字符
2. 必须包含品类词，用 "Throw Pillow Cover"（不要写成 Cushion Cover）
3. 必须把上面的材质翻成英文面料词，买家要能搜到
4. 必须包含尺寸 {row["size"]}
5. 标题里没写含芯的就补上 "Insert Not Included"，避免买家误会产生退货纠纷
6. 不要堆砌重复词，不要全大写，不要用感叹号

只输出改写后的标题，不要解释，不要加引号。""".strip()


# ---------------------------------------------------------------- 调用模型


def rewrite_one(client, kind: str, model: str, row: dict) -> tuple[str, int, int]:
    """调一次模型，返回 (改写后的标题, 输入token, 输出token)。

    kind 是 "anthropic" 或 "deepseek"，因为这两家的 SDK 写法不一样。
    """
    prompt = build_prompt(row)

    if kind == "anthropic":
        resp = client.messages.create(
            model=model,
            max_tokens=256,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text.strip()
        return text, resp.usage.input_tokens, resp.usage.output_tokens

    # DeepSeek 兼容 OpenAI 的接口协议，所以用 openai 这个库，只改 base_url
    resp = client.chat.completions.create(
        model=model,
        max_tokens=256,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    text = resp.choices[0].message.content.strip()
    return text, resp.usage.prompt_tokens, resp.usage.completion_tokens


# ---------------------------------------------------------------- 检查


def title_length_ok(text: str) -> bool:
    return len(text) <= 80


def material_ok(text: str, material_cn: str) -> bool:
    """检查中文材质有没有被翻成对应的英文面料词。"""
    lower = text.lower()
    for word in MATERIAL_EN.get(material_cn, []):
        if word.lower() in lower:
            return True
    return False


def category_ok(text: str) -> bool:
    return "pillow cover" in text.lower()


# ---------------------------------------------------------------- 导出 Excel


def save_excel(rows: list[dict]) -> None:
    """把结果写进 output.xlsx。第一次听说 openpyxl 没关系，照抄就行。"""
    from openpyxl import Workbook
    from openpyxl.styles import Font

    wb = Workbook()
    ws = wb.active
    ws.title = "改写结果"

    header = ["编号", "原标题", "材质", "尺寸", "改写后标题", "字符数", "材质OK", "品类词OK", "长度OK"]
    ws.append(header)

    # 表头加粗，好看一点
    for cell in ws[1]:
        cell.font = Font(bold=True)

    for r in rows:
        ws.append([
            r["id"], r["title_cn"], r["material"], r["size"],
            r["new_title"], len(r["new_title"]),
            "是" if r["ok_material"] else "否",
            "是" if r["ok_category"] else "否",
            "是" if r["ok_length"] else "否",
        ])

    # 列宽调一下，不然内容挤在一起
    ws.column_dimensions["B"].width = 45
    ws.column_dimensions["E"].width = 70
    ws.column_dimensions["F"].width = 8

    wb.save(OUT_FILE)


# ---------------------------------------------------------------- 主流程


def main() -> None:
    if not CSV_FILE.exists():
        print(f"找不到数据文件：{CSV_FILE}")
        sys.exit(1)

    has_anthropic = bool(get_key("ANTHROPIC_API_KEY"))
    has_deepseek = bool(get_key("DEEPSEEK_API_KEY"))
    if not has_anthropic and not has_deepseek:
        print("没有找到任何 API Key。检查仓库根目录的 .env 文件。")
        sys.exit(1)

    if has_anthropic:
        import anthropic

        kind = "anthropic"
        model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
        client = anthropic.Anthropic(api_key=get_key("ANTHROPIC_API_KEY"))
    else:
        import openai

        kind = "deepseek"
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        client = openai.OpenAI(
            api_key=get_key("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )

    # utf-8-sig 而不是 utf-8：CSV 文件开头藏了一个肉眼看不见的 BOM 标记，
    # 用 utf-8 读会把第一列的列名变成 "\ufeffid"，然后就取不到 id 了。
    with open(CSV_FILE, encoding="utf-8-sig", newline="") as f:
        data_rows = list(csv.DictReader(f))

    print(f"供应商 : {kind}")
    print(f"模型   : {model}")
    print(f"待改写 : {len(data_rows)} 条")
    print("=" * 70)

    results = []
    total_in = 0
    total_out = 0
    start = time.time()

    for i, row in enumerate(data_rows, 1):
        t0 = time.time()
        try:
            new_title, tin, tout = rewrite_one(client, kind, model, row)
        except Exception as e:
            print(f"[{i}] 调用失败：{type(e).__name__}: {e}")
            continue

        elapsed = time.time() - t0
        total_in += tin
        total_out += tout

        ok_material = material_ok(new_title, row["material"])
        ok_category = category_ok(new_title)
        ok_length = title_length_ok(new_title)

        print(f"[{i}] 原标题 : {row['title_cn']}")
        print(f"    材质/尺寸 : {row['material']} / {row['size']}")
        print(f"    改写后 : {new_title}")
        print(
            f"    检查   : 材质{'✓' if ok_material else '✗'} "
            f"品类词{'✓' if ok_category else '✗'} "
            f"长度{'✓' if ok_length else '✗'}({len(new_title)}) "
            f"| {elapsed:.1f}s"
        )
        print("-" * 70)

        results.append({
            "id": row["id"],
            "title_cn": row["title_cn"],
            "material": row["material"],
            "size": row["size"],
            "new_title": new_title,
            "ok_material": ok_material,
            "ok_category": ok_category,
            "ok_length": ok_length,
            "elapsed": elapsed,
        })

    if not results:
        print("一条都没跑成功，先别往下走，把报错整段发我。")
        sys.exit(1)

    save_excel(results)

    elapsed_all = time.time() - start
    n = len(results)
    pass_all = sum(1 for r in results if r["ok_material"] and r["ok_category"] and r["ok_length"])

    print("=" * 70)
    print(f"完成 {n} 条，总耗时 {elapsed_all:.1f} 秒，平均每条 {elapsed_all / n:.1f} 秒")
    print(f"输入 token 合计 : {total_in}")
    print(f"输出 token 合计 : {total_out}")
    print(f"三项检查全过   : {pass_all}/{n} 条")
    print(f"结果已导出     : {OUT_FILE}")
    print("\n把上面这几个数字抄进 notes/day02.md，那就是今天的复盘。")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n跑挂了：{type(e).__name__}: {e}")
        print("\n把这个报错整段复制给我，别自己查，省时间。")
        sys.exit(1)
