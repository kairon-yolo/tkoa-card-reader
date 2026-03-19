import json

LINKS_FILE = "links.json"
CARDS_FILE = "all-cards-number.json"
OUTPUT = "merged-links.json"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    links = load_json(LINKS_FILE)
    cards = load_json(CARDS_FILE)

    # 先把 cards 轉成 dict，方便查找
    card_map = {item["name"]: item for item in cards}

    merged = []

    for link in links:
        name = link["name"]

        base = {
            "name": name,
            "url": link.get("url"),
            "series": None,
            "attribute": None
        }

        if name in card_map:
            base["series"] = card_map[name].get("series")
            base["attribute"] = card_map[name].get("attribute")

        merged.append(base)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"Merged {len(merged)} items → {OUTPUT}")
