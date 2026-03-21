import json
import re

INPUT_FILE = "all-cards-number.txt"
CARDS_JSON = "all-cards-number.json"
MERGED_FILE = "merged-links.json"
OUTPUT_FILE = "merged-links-updated.json"
MISSING_FILE = "missing-cards.txt"
CARDS_DB_FILE = "cards-db-base.json"   # ← 新增：你的 cards-db-base.json

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

    # -------------------------------
    # 讀取 cards-db-base.json（新增）
    # -------------------------------
    with open(CARDS_DB_FILE, "r", encoding="utf-8") as f:
        cards_db = json.load(f)

    # 建立 name → card_data 的查表
    db_map = {entry["name"]: entry for entry in cards_db}

    print(f"cards-db-base.json 讀取完成，共 {len(cards_db)} 筆資料")

    # 读取 merged-links.json
    with open(MERGED_FILE, "r", encoding="utf-8") as f:
        merged = json.load(f)

    updated_count = 0
    missing_cards = []

    # merged-links.json 是 list
    for entry in merged:
        name = entry.get("name")

        # 先更新卡號
        if name in number_map:
            entry["number"] = number_map[name]
        else:
            entry["number"] = "No Card Number/ アヴァロンの鍵 Online Cards"
            missing_cards.append(name)

        # 再更新 cards-db-base.json 的資料（新增）
        if name in db_map:
            entry.update(db_map[name])  # 合併所有欄位
            updated_count += 1

    # 输出更新后的 merged-links-updated.json
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=4)

    # 输出找不到的卡名清单
    with open(MISSING_FILE, "w", encoding="utf-8") as f:
        for name in missing_cards:
            f.write(name + "\n")

    print(f"合併完成！成功更新 {updated_count} 张卡片 → {OUTPUT_FILE}")
    print(f"找不到卡号的卡共 {len(missing_cards)} 个 → {MISSING_FILE}")

if __name__ == "__main__":
    main()
