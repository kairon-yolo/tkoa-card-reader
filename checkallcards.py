import json

# 读取 cards-db.json
with open("cards-db.json", "r", encoding="utf-8") as f:
    cards_db = json.load(f)

# 读取 all-cards-raw-name.txt
with open("all-cards-raw-name.txt", "r", encoding="utf-8") as f:
    raw_names = f.read().splitlines()

# 去掉《》符号
raw_names_clean = {name.strip("《》") for name in raw_names if name.strip()}

# 从 cards-db.json 抓出 name 字段
db_names = {card["name"] for card in cards_db}

# 找出 db 里有，但 raw 里没有的
missing = sorted(db_names - raw_names_clean)

# 输出结果
print("=== 以下卡名在 all-cards-raw-name.txt 中缺失 ===")
for name in missing:
    print(name)

print(f"\n共缺少 {len(missing)} 张卡。")
