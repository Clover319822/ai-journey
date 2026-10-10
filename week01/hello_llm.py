"""
第 1 周 · 第一个真实的大模型调用

任务：把一条 TEMU 抱枕套的中文原标题，改写成符合平台习惯的英文 listing 标题。

为什么选这个而不是官方的 "Hello World"：
这是第 1 周周末作业（批量改写 50 条 listing）的最小可运行版本。
跑通它，等于同时完成了"学会调 API"和"作品 C 的第一行代码"。

用法：
    cp .env.example .env      # 然后填入你的 Key
    uv run python week01/hello_llm.py

脚本会自动检测你配了哪个 Key：有 ANTHROPIC_API_KEY 就走 Claude，
否则有 DEEPSEEK_API_KEY 就走 DeepSeek。两个都配的话优先 Claude。
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# 从仓库根目录读 .env（这样在任意子目录下运行都能找到）
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# ---------------------------------------------------------------- 任务数据

# 真实场景：TEMU 全托管，家居日用品类目，抱枕套
ORIGINAL_TITLE = "新款简约现代抱枕套 客厅沙发靠垫套 45x45cm 不含芯"

REQUIREMENTS = """
请把上面这条中文商品标题改写成英文电商 listing 标题，要求：
1. 长度控制在 80 字符以内（TEMU 标题有字数限制）
2. 必须包含核心品类词、尺寸、数量、适用场景
3. 不要堆砌同义词，不要全大写，不要用感叹号
4. 符合英文母语买家的搜索习惯（他们不会搜 "simple modern"，会搜具体材质和用途）

只输出改写后的标题，不要任何解释。
""".strip()

# ---------------------------------------------------------------- 价格表

# 单位：美元 / 每百万 token。2026-10 官方标价，以 Anthropic 官网为准
ANTHROPIC_PRICE = {
    "claude-opus-5-5": (4.0, 20.0),
    "claude-sonnet-5-5": (2.0, 10.0),
    "claude-haiku-5-5": (0.10, 0.50),
}


def call_anthropic() -> None:
    import anthropic

    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print(f"供应商 : Anthropic")
    print(f"模型   : {model}")

    resp = client.messages.create(
        model=model,
        max_tokens=256,
        system="你是一个跨境电商 listing 优化专家，熟悉 TEMU 平台规则。",
        messages=[
            {"role": "user", "content": f"{ORIGINAL_TITLE}\n\n{REQUIREMENTS}"}
        ],
    )

    print(f"\n原标题 : {ORIGINAL_TITLE}")
    print(f"改写后 : {resp.content[0].text.strip()}")
    print(f"\n输入 token: {resp.usage.input_tokens}")
    print(f"输出 token: {resp.usage.output_tokens}")

    if model in ANTHROPIC_PRICE:
        pin, pout = ANTHROPIC_PRICE[model]
        cost = (
            resp.usage.input_tokens * pin + resp.usage.output_tokens * pout
        ) / 1_000_000
        print(f"本次花费 : ${cost:.6f}（约 ¥{cost * 7.2:.4f}）")
    else:
        print(f"本次花费 : 模型 {model} 未在价格表中，请查官网")


def call_deepseek() -> None:
    import openai

    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    # DeepSeek 兼容 OpenAI 的接口协议，所以直接用 openai 这个库，只改 base_url
    client = openai.OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com",
    )

    print(f"供应商 : DeepSeek")
    print(f"模型   : {model}")

    resp = client.chat.completions.create(
        model=model,
        max_tokens=256,
        messages=[
            {"role": "system", "content": "你是一个跨境电商 listing 优化专家，熟悉 TEMU 平台规则。"},
            {"role": "user", "content": f"{ORIGINAL_TITLE}\n\n{REQUIREMENTS}"},
        ],
    )

    print(f"\n原标题 : {ORIGINAL_TITLE}")
    print(f"改写后 : {resp.choices[0].message.content.strip()}")
    print(f"\n输入 token: {resp.usage.prompt_tokens}")
    print(f"输出 token: {resp.usage.completion_tokens}")
    print("本次花费 : DeepSeek 按人民币计价且有时段优惠，请查 platform.deepseek.com 账单")


def main() -> None:
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_deepseek = bool(os.getenv("DEEPSEEK_API_KEY"))

    if not has_anthropic and not has_deepseek:
        print("没有找到任何 API Key。")
        print("  1. 复制 .env.example 为 .env")
        print("  2. 填入 ANTHROPIC_API_KEY 或 DEEPSEEK_API_KEY")
        print("  3. 重新运行")
        sys.exit(1)

    try:
        if has_anthropic:
            call_anthropic()
        else:
            call_deepseek()
    except Exception as e:
        print(f"\n调用失败：{type(e).__name__}: {e}")
        print("\n常见原因：")
        print("  - Key 填错了，或者带了多余空格")
        print("  - Anthropic 需要绑卡且有额度，光注册不够")
        print("  - 网络抽风，重跑一次试试")
        print("  - 模型名不对，去官网确认一下可用的 model id")
        sys.exit(1)


if __name__ == "__main__":
    main()
