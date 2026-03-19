import json
import re

INPUT_FILE = "all-cards-number.txt"
CARDS_JSON = "all-cards-number.json"
MERGED_FILE = "merged-links.json"
OUTPUT_FILE = "merged-links-updated.json"

# -------------------------------
# 解析卡号＋卡名
# -------------------------------
def parse_line(line):
    line = line.strip()
    if not line:
        return None

    # 支援：001 / N31 / EX08 / Leg01 / W40 等
    match = re.match(r"^([A-Za-z]*\d+)\s+(.+)$", line)
    if not match:
        return None

    card_number = match.group(1)
    card_name = match.group(2)

    return {
        "number": card_number,
        "name": card_name
    }

# -------------------------------
# 主程序
# -------------------------------
def main():
    cards = []

    # 读取 all-cards-number.txt
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parsed = parse_line(line)
            if parsed:
                cards.append(parsed)

    # 输出 all-cards-number.json
    with open(CARDS_JSON, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=4)

    print(f"卡号解析完成，共 {len(cards)} 张卡片 → {CARDS_JSON}")

    # 建立 name → number 的查表
    number_map = {card["name"]: card["number"] for card in cards}

    # 读取 merged-links.json
    with open(MERGED_FILE, "r", encoding="utf-8") as f:
        merged = json.load(f)

    updated_count = 0

    # merged-links.json 是 list
    for entry in merged:
        name = entry.get("name")
        if name in number_map:
            entry["number"] = number_map[name]
            updated_count += 1

    # 输出更新后的 merged-links-updated.json
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=4)

    print(f"合并完成！成功更新 {updated_count} 张卡片 → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
