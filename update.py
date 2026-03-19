import os
import json
import re
from bs4 import BeautifulSoup

HTML_DIR = "avalon_pages"
JSON_FILE = "merged-links.json"


def clean_text(s):
    if not s:
        return ""
    return s.replace("\u3000", "").replace("\xa0", "").strip()


def extract_name_from_title(soup):
    title = soup.title.get_text(strip=True)
    if "《" in title and "》" in title:
        return title.split("《")[1].split("》")[0]
    return None


def extract_image_url(soup):
    """從 JSON-LD 取出卡片圖片 URL"""
    scripts = soup.find_all("script", {"type": "application/ld+json"})
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "image" in item:
                        img = item["image"]
                        if isinstance(img, dict) and "url" in img:
                            return img["url"]
            elif isinstance(data, dict) and "image" in data:
                img = data["image"]
                if isinstance(img, dict) and "url" in img:
                    return img["url"]
        except:
            continue
    return None


def extract_all_pictures(soup):
    """抓取所有 <picture> 裡的圖片，回傳 list"""
    results = []

    pictures = soup.find_all("picture")
    for pic in pictures:
        entry = {}

        # small / medium 來自 <source>
        sources = pic.find_all("source")
        for src in sources:
            url = src.get("srcset")
            if not url:
                continue
            if "t/" in url:
                entry["small"] = url
            elif "m/" in url:
                entry["medium"] = url

        # original 來自 <img>
        img = pic.find("img")
        if img and img.get("src"):
            url = img["src"]
            if url.startswith("//"):
                url = "https:" + url
            entry["original"] = url

        if entry:
            results.append(entry)

    return results


def extract_description(soup):
    """抓取表格後面的卡片說明（直到 <hr>），包含 div / p / ul / li"""
    table = soup.find("table")
    if not table:
        return "", ""

    description_html = []
    description_text = []

    for tag in table.find_all_next():

        # 到 <hr> 就停止（atwiki 的結構固定）
        if tag.name == "hr":
            break

        # 抓取所有可能的說明標籤
        if tag.name in ["div", "p", "ul", "li"]:
            html = tag.decode_contents().strip()
            text = tag.get_text("\n", strip=True)

            if html:
                description_html.append(html)
            if text:
                description_text.append(text)

    return "\n".join(description_html), "\n".join(description_text)


def parse_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    data = {}

    name = extract_name_from_title(soup)
    if not name:
        return None, {}

    # JSON-LD 主圖片
    img_url = extract_image_url(soup)
    if img_url:
        data["image_url"] = img_url

    # 所有 <picture> 圖片
    pictures = extract_all_pictures(soup)
    if pictures:
        data["images"] = pictures

    # 解析表格
    table = soup.find("table")
    if not table:
        return name, data

    tds = table.find_all("td")
    texts = [clean_text(td.get_text()) for td in tds]

    for i, text in enumerate(texts):

        if text == "属性":
            data["attribute_raw"] = clean_text(texts[i+1])

        if text == "移動色":
            data["move_color"] = tds[i+1].decode_contents().strip()

        if text == "攻撃":
            data["attack"] = clean_text(texts[i+1])

        if text == "耐久":
            data["hp"] = clean_text(texts[i+1])

        if text == "レア":
            data["rare"] = clean_text(texts[i+1])

        if text == "種族":
            data["race"] = clean_text(texts[i+1])

        if text == "能力":
            data["ability_html"] = tds[i+1].decode_contents().strip()
            data["ability"] = clean_text(tds[i+1].get_text("\n"))

    # 卡片說明
    desc_html, desc_text = extract_description(soup)
    data["description_html"] = desc_html
    data["description"] = desc_text

    return name, data


def main():
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)

    name_map = {item["name"]: item for item in items}

    updated = 0
    missing_json = 0
    missing_name = 0

    missing_json_list = []  # ← 新增：記錄找不到的卡片名稱

    for filename in os.listdir(HTML_DIR):
        if not filename.endswith(".html"):
            continue

        html_path = os.path.join(HTML_DIR, filename)
        name, parsed = parse_html(html_path)

        if not name:
            print(f"⚠  {filename} without any card name is matched")
            missing_name += 1
            continue

        if name not in name_map:
            print(f"⚠ JSON 中找不到卡片：{name}")
            missing_json += 1
            missing_json_list.append(name)  # ← 記錄
            continue

        for key, value in parsed.items():
            name_map[name][key] = value

        updated += 1
        print(f"✔  {name} - This Card info is Updated")

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print("\n==============================")
    print("🎉 Update Completed!")
    print(f"✔ Successfully updated: {updated} records")
    print(f"⚠ Cards not found related to JSON: {missing_json} records")

    if missing_json_list:
        print("The following cards (from JSON) were not found in the DB:")
        for n in missing_json_list:
            print(" -", n)

    print(f"⚠ Failed to extract card name from DB: {missing_name} records")
    print("==============================\n")


if __name__ == "__main__":
    main()
