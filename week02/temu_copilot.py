#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第 2 周提前开工 · TEMU 全托管卖家 AI 工作流 v1
================================================

一句话：给一个商品，输出一张「上架评估卡」——
  左边是钱（代码算，准）：落地成本、盈亏平衡供货价、建议报价、让价底线
  右边是活（模型写，快）：退货风险点、英文标题候选、核心卖点、属性建议、报不报

为什么先做这个模块：
TEMU 全托管卖家的时间主要花在选品和核价上——买手丢来一个品，
你要在几分钟内判断"这个价报不报出去"。报高了选不上，报低了亏钱。
这张卡就是把拍脑袋变成：先算账，再让 AI 补它擅长的判断。

设计原则（也是第 2 周的核心认知）：
  算钱用代码，写字用模型。
  LLM 做算术不可靠，价格算错一环就是真金白银的亏损，
  所以所有数字都由 Python 算，模型只负责定性判断和文案。

用法：
    uv run python week02/temu_copilot.py --demo            # 跑内置演示数据（8 个抱枕套 SKU）
    uv run python week02/temu_copilot.py --batch 文件.csv  # 批量评估你自己的品
    uv run python week02/temu_copilot.py --one "亚麻抱枕套" --cost 7.8 --material 亚麻 --size 48x48cm
    uv run python week02/temu_copilot.py --demo --no-ai    # 只算钱，不调模型（API 挂了也能用）
    不带参数直接跑 = 弹菜单，跟着提示走

CSV 表头（列名要对，顺序无所谓）：
    name,category,cost,weight_g,size,material,front_price,note
    cost 必填（进货成本，元/件），其他列可空。
    front_price 是 TEMU 前台同款售价（美元），填了会多算一条"供货价占前台价比例"。

成本模型参数在下面 CostModel 类里，按你后台的真实数据改：
    退货损耗率 / 国内段物流 / 包材人工 / 目标加价率 —— 这四个数决定测算准不准。
    默认值是抱枕套类目的估计值，别当成真理。

密钥和 week01 用同一套：仓库根目录 .env，
有 ANTHROPIC_API_KEY 走 Claude，否则有 DEEPSEEK_API_KEY 走 DeepSeek。
"""

import argparse
import csv
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# 往上两级才是仓库根目录 D:\ai-journey，这样在任意目录下跑都能找到 .env
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

HERE = Path(__file__).resolve().parent
DEMO_CSV = HERE / "data" / "demo_skus.csv"
OUT_DIR = HERE / "output"

FX_RATE = 7.2  # 美元→人民币粗算用。要精确就自己查当日汇率，改这一行


# ---------------------------------------------------------------- 数据模型


@dataclass
class CostModel:
    """全托管模式下的单件成本模型。

    先建立一个概念：全托管你赚的是「供货价」，不是「售价」。
    货进 TEMU 仓之后，定价、物流、售后都是平台的，买家付多少钱跟你无关。
    你要算的只有一件事：这个供货价，扣完成本还赚不赚。
    所以模型里所有价格都是「你从平台拿到的结算价」，不是前台零售价。

    四个参数按「元/件」或比例填，改这里全局生效。
    """

    first_mile: float = 2.5      # 国内段物流：你的仓 → TEMU 仓
    packing: float = 1.0         # 包材 + 贴单 + 人工
    return_rate: float = 0.08    # 预估退货损耗率：退回来的货基本报废，等于白备一件
    target_markup: float = 0.15  # 目标加价率：建议报价 = 盈亏平衡价 × (1 + 这个数)
    floor_buffer: float = 0.02   # 让价底线在盈亏平衡价上加的缓冲，抗运费波动


@dataclass
class Product:
    """一个待评估的商品。cost 是唯一必填项，其他没有就留空。"""

    name: str
    category: str = "家居日用"
    cost: float = 0.0
    weight_g: int = 0
    size: str = ""
    material: str = ""
    front_price: float | None = None   # TEMU 前台同款价（美元），可空
    note: str = ""


# ---------------------------------------------------------------- 基础工具


def get_key(name: str) -> str | None:
    """读 API Key，把 .env.example 里的占位符当成"没配"（和 week01 一个套路）。"""
    value = (os.getenv(name) or "").strip()
    if not value or "xxxxx" in value:
        return None
    return value


def get_client() -> tuple[object, str, str]:
    """返回 (客户端, 供应商名, 模型名)。优先 Claude，没有就用 DeepSeek。"""
    if get_key("ANTHROPIC_API_KEY"):
        import anthropic

        client = anthropic.Anthropic(api_key=get_key("ANTHROPIC_API_KEY"))
        return client, "anthropic", os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")

    if get_key("DEEPSEEK_API_KEY"):
        import openai

        # DeepSeek 兼容 OpenAI 的接口协议，所以直接用 openai 这个库，只改 base_url
        client = openai.OpenAI(
            api_key=get_key("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
        return client, "deepseek", os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    print("没有找到任何 API Key。检查仓库根目录的 .env 文件。")
    sys.exit(1)


def to_float(value) -> float:
    """脏数据转数字：空字符串、乱码一律变 0.0，不让它把程序搞崩。"""
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return 0.0


# ---------------------------------------------------------------- 算钱（纯代码）


def calc(p: Product, m: CostModel) -> dict:
    """成本测算。纯算术，不调模型——定价错一环就是真亏，必须可复现。

    退货率 8% 的意思是：每卖出去 1 件，平均要白备 0.08 件的货
    （退回来的基本报废）。所以每件真实成本 = 落地成本 × (1 + 退货率)，
    这个数就是盈亏平衡供货价。
    """
    landed = p.cost + m.first_mile + m.packing
    breakeven = landed * (1 + m.return_rate)
    suggested = breakeven * (1 + m.target_markup)
    floor = breakeven * (1 + m.floor_buffer)

    econ = {
        "landed": round(landed, 2),
        "breakeven": round(breakeven, 2),
        "suggested": round(suggested, 2),
        "floor": round(floor, 2),
        "profit": round(suggested - breakeven, 2),
    }

    if p.front_price:
        front_cny = p.front_price * FX_RATE
        econ["front_cny"] = round(front_cny, 2)
        econ["front_ratio"] = round(suggested / front_cny, 3)

    return econ


# ---------------------------------------------------------------- 写字（模型）


def build_prompt(p: Product, econ: dict, m: CostModel) -> str:
    """把商品信息 + 已算好的账，拼成一段给模型看的话。"""
    front = f"${p.front_price}" if p.front_price else "未提供"
    return f"""你是 TEMU 全托管模式的卖家运营顾问，熟悉家居日用类目。
根据下面的商品信息和成本测算，输出一张「上架评估卡」。

硬规则：
1. 只基于给定信息判断，信息不足就写「需人工确认」，禁止编造数据。
2. 退货风险放最前面：尺寸误差、色差、材质与描述不符、做工是家居类退货主因。
3. 标题按 TEMU 前台语言（英文）写：材质/品类 + 核心属性 + 规格或场景，不超过 80 字符，不用 best / No.1 这类违禁词。
4. 每条建议都要具体到能直接执行，不写「注意质量」这种空话。

【商品信息】
品名：{p.name}
类目：{p.category}
进货成本：{p.cost} 元/件
克重：{p.weight_g or "未提供"}
尺寸：{p.size or "未提供"}
材质：{p.material or "未提供"}
前台同款价：{front}
备注：{p.note or "无"}

【成本测算（Python 已算好，直接引用，不要自己重算）】
落地成本：{econ["landed"]} 元/件
盈亏平衡供货价：{econ["breakeven"]} 元（低于此价每卖一件亏一件）
建议报价：{econ["suggested"]} 元（含 {m.target_markup:.0%} 目标加价）
让价底线：{econ["floor"]} 元

【输出格式】Markdown，严格按以下小节输出，不要有多余内容：
**结论**：一句话——按测算这个价报不报得出去，依据是什么
**退货风险点**：最多 3 条，格式「风险 → 规避动作」
**标题候选**：3 个英文标题，每行一个
**核心卖点**：3 条，每条不超过 25 字（中文）
**属性与详情建议**：2 条，写清楚详情页/属性里必须写明白什么
**下一步**：Go / 优化后再上 / 放弃，三选一，加一句理由"""


def ask_llm(client, kind: str, model: str, prompt: str, retries: int = 2) -> tuple[str, int, int]:
    """调一次模型，失败自动重试。返回 (文本, 输入token, 输出token)。

    第 2 周周末作业要求「带重试与容错」，这就是雏形：
    网络抽风重试两次，还不行就把测算结果先交出去，AI 部分标注失败原因，
    不让一个商品的错误把整批 evaluation 拖死。
    """
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            if kind == "anthropic":
                resp = client.messages.create(
                    model=model,
                    max_tokens=900,
                    temperature=0.4,
                    system="你是 TEMU 全托管卖家运营顾问。",
                    messages=[{"role": "user", "content": prompt}],
                )
                text = resp.content[0].text.strip()
                return text, resp.usage.input_tokens, resp.usage.output_tokens

            resp = client.chat.completions.create(
                model=model,
                max_tokens=900,
                temperature=0.4,
                messages=[
                    {"role": "system", "content": "你是 TEMU 全托管卖家运营顾问。"},
                    {"role": "user", "content": prompt},
                ],
            )
            text = resp.choices[0].message.content.strip()
            return text, resp.usage.prompt_tokens, resp.usage.completion_tokens
        except Exception as e:
            last_err = e
            print(f"    第 {attempt} 次调用失败：{type(e).__name__}: {e}")
            time.sleep(2)

    return f"（AI 评估生成失败：{last_err}。测算结果不受影响，可重跑或手动补充。）", 0, 0


# ---------------------------------------------------------------- 输出


def render_card(p: Product, econ: dict, ai_text: str, m: CostModel) -> str:
    """一张评估卡 = 测算区（代码保证准）+ AI 区（模型写判断）。"""
    lines = [
        f"## 上架评估卡：{p.name}",
        "",
        f"- 类目：{p.category}｜材质：{p.material or '—'}｜尺寸：{p.size or '—'}｜克重：{p.weight_g or '—'}g",
        f"- 落地成本 ¥{econ['landed']} = 进货 ¥{p.cost} + 国内物流 ¥{m.first_mile} + 包材人工 ¥{m.packing}",
        f"- 盈亏平衡供货价 **¥{econ['breakeven']}**（低于此价每卖一件亏一件）",
        f"- 建议报价 **¥{econ['suggested']}**（加价 {m.target_markup:.0%}，单件毛利 ¥{econ['profit']}）",
        f"- 让价底线 ¥{econ['floor']}（和买手谈判时最后守住的价）",
    ]
    if p.front_price:
        lines.append(
            f"- 前台同款价 ${p.front_price} ≈ ¥{econ['front_cny']}，"
            f"建议供货价占前台价 {econ['front_ratio'] * 100:.0f}%"
            f"（平台留 {100 - econ['front_ratio'] * 100:.0f}%，仅供参照，以买手核价为准）"
        )
    lines += ["", "---", "", ai_text, ""]
    return "\n".join(lines)


# ---------------------------------------------------------------- 主流程


def load_products(csv_path: Path) -> list[Product]:
    """读 CSV 转成 Product 列表。utf-8-sig 是老规矩：防 BOM 把列名啃掉（week01 踩过）。"""
    products = []
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("name") or "").strip()
            if not name:
                continue
            products.append(Product(
                name=name,
                category=(row.get("category") or "家居日用").strip(),
                cost=to_float(row.get("cost")),
                weight_g=int(to_float(row.get("weight_g"))),
                size=(row.get("size") or "").strip(),
                material=(row.get("material") or "").strip(),
                front_price=to_float(row.get("front_price")) or None,
                note=(row.get("note") or "").strip(),
            ))
    return products


def run_batch(client, kind: str, model: str, products: list[Product],
              m: CostModel, use_ai: bool = True) -> None:
    """批量评估：逐个算钱 → 调模型 → 汇总成一个 markdown 文件。"""
    cards = []
    total_in = 0
    total_out = 0
    start = time.time()

    print(f"成本模型：国内物流 ¥{m.first_mile}｜包材人工 ¥{m.packing}｜"
          f"退货损耗 {m.return_rate:.0%}｜目标加价 {m.target_markup:.0%}")
    print(f"AI 评估：{'开（' + kind + ' / ' + model + '）' if use_ai else '关'}")
    print(f"待评估：{len(products)} 个 SKU")
    print("=" * 72)

    for i, p in enumerate(products, 1):
        if p.cost <= 0:
            print(f"[{i}] {p.name}：没填成本，跳过（CSV 里 cost 是必填列）\n")
            continue

        econ = calc(p, m)

        if use_ai:
            print(f"[{i}] {p.name}：账算完了，AI 评估中...")
            ai_text, tin, tout = ask_llm(client, kind, model, build_prompt(p, econ, m))
            total_in += tin
            total_out += tout
        else:
            ai_text = "（--no-ai 模式：只做了成本测算）"

        card = render_card(p, econ, ai_text, m)
        cards.append(card)
        print(card)
        print("-" * 72)

    if not cards:
        print("一条都没跑出来。检查 CSV：name 和 cost 两列必须有值。")
        return

    OUT_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M")
    out_file = OUT_DIR / f"上架评估卡-{ts}.md"
    header = [
        f"# TEMU 上架评估卡（{ts}）",
        "",
        f"成本模型：国内物流 ¥{m.first_mile}｜包材人工 ¥{m.packing}｜"
        f"退货损耗 {m.return_rate:.0%}｜目标加价 {m.target_markup:.0%}",
        "",
    ]
    out_file.write_text("\n".join(header + cards), encoding="utf-8")

    elapsed = time.time() - start
    print("=" * 72)
    print(f"完成 {len(cards)} 个 SKU，总耗时 {elapsed:.1f} 秒")
    if use_ai:
        print(f"输入 token 合计：{total_in}｜输出 token 合计：{total_out}")
    print(f"结果已导出：{out_file}")
    print("\n下一步：把 CostModel 里四个参数改成你后台的真实数字，")
    print("再跑 --batch 你的真实 SKU 表，那才是能拿去决策的东西。")


# ---------------------------------------------------------------- 交互


def ask_single_product() -> Product:
    """手动输入一个商品。成本会循环问到填为止——没成本算不了钱。"""
    print("\n单个商品评估（不知道的直接回车跳过）")
    name = input("品名：").strip() or "未命名商品"
    cost = 0.0
    while cost <= 0:
        cost = to_float(input("进货成本（元/件，必填）："))
        if cost <= 0:
            print("没填成本算不了钱，给个数，比如 7.8")
    return Product(
        name=name,
        category=input("类目（回车=家居日用）：").strip() or "家居日用",
        cost=cost,
        material=input("材质：").strip(),
        size=input("尺寸：").strip(),
        front_price=to_float(input("前台同款价（美元，可空）：")) or None,
        note=input("备注：").strip(),
    )


def interactive_menu() -> list[Product]:
    """不带参数运行时弹出的菜单。Windows 拖文件进来的路径带引号，顺手剥掉。"""
    print("=" * 60)
    print("TEMU Copilot v1 —— 上架评估卡")
    print("  1. 跑演示数据（8 个抱枕套，成本为假设值）")
    print("  2. 批量评估 CSV 文件")
    print("  3. 手动评估单个商品")
    print("  0. 退出")
    print("=" * 60)
    choice = input("选哪个：").strip()

    if choice == "1":
        if not DEMO_CSV.exists():
            print(f"找不到演示数据：{DEMO_CSV}")
            return []
        print("\n※ 演示数据：成本与前台价都是假设值，仅用于看效果\n")
        return load_products(DEMO_CSV)

    if choice == "2":
        raw = input("CSV 文件路径（可以直接把文件拖进来）：").strip().strip('"')
        path = Path(raw)
        if not path.exists():
            print(f"找不到文件：{path}")
            return []
        return load_products(path)

    if choice == "3":
        return [ask_single_product()]

    return []


# ---------------------------------------------------------------- 入口


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TEMU 全托管卖家 AI 工作流 v1：上架评估卡"
    )
    parser.add_argument("--demo", action="store_true", help="跑内置演示数据")
    parser.add_argument("--batch", metavar="CSV", help="批量评估 CSV 文件")
    parser.add_argument("--one", metavar="品名", help="评估单个商品")
    parser.add_argument("--cost", type=float, default=0, help="进货成本（元/件）")
    parser.add_argument("--material", default="", help="材质")
    parser.add_argument("--size", default="", help="尺寸")
    parser.add_argument("--front", type=float, default=0, help="TEMU 前台同款价（美元）")
    parser.add_argument("--no-ai", action="store_true", help="只算钱，不调模型")
    args = parser.parse_args()

    if args.demo:
        if not DEMO_CSV.exists():
            print(f"找不到演示数据：{DEMO_CSV}")
            sys.exit(1)
        print("※ 演示数据：成本与前台价都是假设值，仅用于看效果\n")
        products = load_products(DEMO_CSV)
    elif args.batch:
        path = Path(args.batch)
        if not path.exists():
            print(f"找不到文件：{path}")
            sys.exit(1)
        products = load_products(path)
    elif args.one:
        if args.cost <= 0:
            print("评估单个商品必须给进货成本，例如：--cost 7.8")
            sys.exit(1)
        products = [Product(
            name=args.one,
            cost=args.cost,
            material=args.material,
            size=args.size,
            front_price=args.front or None,
        )]
    else:
        products = interactive_menu()
        if not products:
            return

    if not products:
        print("一个商品都没读到，检查 CSV 的 name 列。")
        sys.exit(1)

    use_ai = not args.no_ai
    client = kind = model = None
    if use_ai:
        client, kind, model = get_client()

    run_batch(client, kind, model, products, CostModel(), use_ai=use_ai)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已取消。")
    except Exception as e:
        print(f"\n跑挂了：{type(e).__name__}: {e}")
        print("\n把这个报错整段复制给我，别自己查，省时间。")
        sys.exit(1)
