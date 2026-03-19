import os
import json
from bs4 import BeautifulSoup

HTML_DIR = "avalon_pages"
JSON_FILE = "merged-links.json"


def extract_name_from_title(soup):
    """從 <title>《アライクパ》 - ... 抓出卡片名稱"""
    title = soup.title.get_text(strip=True)
    if "《" in title and "》" in title:
        return title.split("《")[1].split("》")[0]
    return None


def parse_html(file_path):
    """解析 Avalon 卡片 HTML，回傳字典資料"""
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    data = {}

    # 取得卡片名稱
    name = extract_name_from_title(soup)
    if not name:
        return None, {}

    # 找第一個 table（卡片資訊）
    table = soup.find("table")
    if not table:
        return name, {}

    tds = table.find_all("td")

    # 用 index 方式解析
    for i, td in enumerate(tds):
        text = td.get_text(strip=True)

        # 属性
        if text == "属性":
            data["attribute_raw"] = tds[i+1].get_text(strip=True)

        # 移動色（●●●）
        if text == "移動色":
            data["move_color"] = tds[i+1].decode_contents().strip()

        # 攻撃
        if text == "攻撃":
            data["attack"] = tds[i+1].get_text(strip=True)

        # 耐久
        if text == "耐久":
            data["hp"] = tds[i+1].get_text(strip=True)

        # レア
        if text == "レア":
            data["rare"] = tds[i+1].get_text(strip=True)

        # 種族
        if text == "種族":
            data["race"] = tds[i+1].get_text(strip=True)

        # 能力（保留 HTML）
        if text == "能力":
            data["ability_html"] = tds[i+1].decode_contents().strip()
            data["ability"] = tds[i+1].get_text("\n", strip=True)

    return name, data


def main():
    # 讀取 JSON
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)

    name_map = {item["name"]: item for item in items}

    updated = 0
    missing_json = 0
    missing_name = 0

    # 掃描 HTML
    for filename in os.listdir(HTML_DIR):
        if not filename.endswith(".html"):
            continue

        html_path = os.path.join(HTML_DIR, filename)
        name, parsed = parse_html(html_path)

        if not name:
            print(f"⚠ 無法從 {filename} 取得卡片名稱")
            missing_name += 1
            continue

        if name not in name_map:
            print(f"⚠ JSON 中找不到卡片：{name}")
            missing_json += 1
            continue

        # 更新 JSON
        for key, value in parsed.items():
            name_map[name][key] = value

        updated += 1
        print(f"✔ 已更新 {name}")

    # 寫回 JSON
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print("\n==============================")
    print(f"🎉 更新完成！")
    print(f"✔ 成功更新：{updated} 筆")
    print(f"⚠ 找不到 JSON 卡片：{missing_json} 筆")
    print(f"⚠ 無法解析名稱：{missing_name} 筆")
    print("==============================\n")


if __name__ == "__main__":
    main()
