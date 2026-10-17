"""把 sample/listings_sample.csv 从 8 条扩到 50 条。

为什么单独写这个脚本：
  手敲 42 行 CSV 是纯体力活，还容易漏逗号。让脚本生成，你只负责跑一条命令。
  生成出来的 42 条是"不同材质 × 不同尺寸 × 不同卖点"的排列组合，
  正好用来测第 5 周要做的事：同一套 prompt 在不同输入上稳不稳。

运行：
    .venv\\Scripts\\python.exe sample\\make_50.py
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_FILE = ROOT / "sample" / "listings_sample.csv"

# 只用脚本里 MATERIAL_EN 已经认得的材质，否则自检一律判"材质不过"
MATERIALS = ["涤麻", "棉麻", "羊羔绒", "牛津布", "水晶绒", "提花布", "亚麻"]
SIZES = ["45x45cm", "30x50cm", "40x40cm", "50x50cm", "60x60cm", "35x35cm"]

# 卖点词 × 风格词，交叉组合出不同的中文原标题
FEATURES = [
    "新款简约现代",
    "北欧ins风",
    "轻奢高级感",
    "田园小清新",
    "美式乡村",
    "日式侘寂",
    "复古民族风",
    "意式极简",
    "法式浪漫",
    "圣诞节限定",
]
STYLES = [
    "沙发靠垫套 客厅卧室装饰",
    "抱枕套 不含芯 家居软装",
    "腰枕套 护腰靠垫 办公室可用",
    "方枕套 车载床头两用",
    "长枕套 沙发靠背装饰",
]


def build_rows(start_id: int, count: int) -> list[dict]:
    rows = []
    for i in range(count):
        material = MATERIALS[i % len(MATERIALS)]
        size = SIZES[(i // len(MATERIALS)) % len(SIZES)]
        feature = FEATURES[i % len(FEATURES)]
        style = STYLES[(i // len(STYLES)) % len(STYLES)]
        rows.append({
            "id": str(start_id + i),
            "category": "抱枕套",
            "title_cn": f"{feature}{material}{style}",
            "size": size,
            "material": material,
        })
    return rows


def main() -> None:
    with open(CSV_FILE, encoding="utf-8-sig", newline="") as f:
        existing = list(csv.DictReader(f))

    if len(existing) >= 50:
        print(f"CSV 已经有 {len(existing)} 条了，不用再生成。")
        return

    need = 50 - len(existing)
    new_rows = build_rows(len(existing) + 1, need)

    with open(CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "category", "title_cn", "size", "material"])
        writer.writeheader()
        writer.writerows(existing)
        writer.writerows(new_rows)

    print(f"原来 {len(existing)} 条 + 新增 {need} 条 = 50 条")
    print(f"文件：{CSV_FILE}")
    print("下一步：跑 week01/list_rewrite.py")


if __name__ == "__main__":
    main()
