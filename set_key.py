"""
一键写入 API Key，生成 .env 文件。

用法（推荐，一条命令）：
    .venv\\Scripts\\python.exe set_key.py sk-你的DeepSeek密钥

或者不带参数运行，它会问你：
    .venv\\Scripts\\python.exe set_key.py

为什么要有这个脚本：
手动用记事本建 .env 有几个坑 —— .env 没有文件扩展名，双击会弹"你要用什么打开"；
记事本保存时还可能给它加上 .txt 后缀变成 .env.txt，导致脚本完全读不到。
这个文件帮你绕开全部这些。

注意：.env 已经在 .gitignore 里，不会被提交。密钥永远不要进仓库。
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXAMPLE = ROOT / ".env.example"
ENV_FILE = ROOT / ".env"

# .env 里要保留的默认配置
DEFAULT_LINES = [
    "DEEPSEEK_MODEL=deepseek-chat",
    "# ANTHROPIC_API_KEY=  （以后办了 Anthropic 再取消注释并填写）",
    "# ANTHROPIC_MODEL=claude-sonnet-5-5",
]


def looks_like_real_key(key: str) -> bool:
    """粗筛一眼，防止把占位符或者复制漏的残片写进去。"""
    return key.startswith("sk-") and len(key) >= 20 and "xxxxx" not in key


def main() -> None:
    # 优先从命令行参数拿，没有就交互式问
    if len(sys.argv) > 1:
        key = sys.argv[1].strip()
    else:
        print("去 platform.deepseek.com → API Keys 复制你的密钥")
        key = input("粘贴到这里，然后回车：").strip()

    if not looks_like_real_key(key):
        print("\n这个 Key 看着不对。")
        print("  DeepSeek 的密钥一般以 sk- 开头，长度 30 位以上。")
        print("  常见情况：复制漏了几位、复制成了占位符 sk-xxxxx、或者前后带了空格。")
        sys.exit(1)

    # 从模板读，没有模板就用默认配置
    if EXAMPLE.exists():
        lines = EXAMPLE.read_text(encoding="utf-8").splitlines()
    else:
        lines = DEFAULT_LINES

    # 逐行处理：去掉占位行和模板里的使用说明，其余配置保留
    out, written = [], False
    for line in lines:
        stripped = line.strip()
        # 模板顶部的说明文字，写进真正的 .env 里会显得莫名其妙
        if stripped.startswith("# 复制这个文件为"):
            continue
        # 任何还带着占位符的行都跳过（ANTHROPIC_API_KEY=sk-ant-xxxxx 之类）
        if "xxxxx" in stripped:
            if stripped.startswith("DEEPSEEK_API_KEY") and not written:
                out.append(f"DEEPSEEK_API_KEY={key}")
                written = True
            continue
        if stripped.startswith("DEEPSEEK_API_KEY"):
            if not written:
                out.append(f"DEEPSEEK_API_KEY={key}")
                written = True
            continue
        out.append(line)

    if not written:
        out.append(f"DEEPSEEK_API_KEY={key}")

    ENV_FILE.write_text("\n".join(out) + "\n", encoding="utf-8")

    masked = key[:6] + "*" * 8 + key[-4:]
    print(f"\n已写入 {ENV_FILE}")
    print(f"  DEEPSEEK_API_KEY={masked}")

    # 安全检查：确认 .env 确实被忽略了
    import subprocess

    result = subprocess.run(
        ["git", "check-ignore", "-q", str(ENV_FILE)],
        cwd=ROOT,
        capture_output=True,
    )
    if result.returncode == 0:
        print("  安全检查通过：.env 已被 .gitignore 忽略，不会进仓库")
    else:
        print("  ⚠️ 警告：.env 没有被忽略！先别提交，检查 .gitignore")

    print("\n下一步：")
    print("  .venv\\Scripts\\python.exe week01\\hello_llm.py")


if __name__ == "__main__":
    main()
