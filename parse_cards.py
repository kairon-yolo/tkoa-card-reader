import os
import json
import requests
from bs4 import BeautifulSoup

HTML_DIR = "avalon_pages"
IMG_DIR = "avalon_images"
JSON_DIR = "avalon_json"

os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)

def download_image(url, save_path):
    if os.path.exists(save_path):
        return
    r = requests.get(url)
    if r.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(r.content)
        print("✔ 下載圖片:", save_path)
    else:
        print("✘ 圖片下載失敗:", url)

def parse_card(html):
    soup = BeautifulSoup(html, "html.parser")

    # -----------------------------
    # ① 取得卡片名稱：data-pagename（最準確）
    # -----------------------------
    card_title = None
    tagedit = soup.find("div", id="atwiki-page-tagedit")
    if tagedit and tagedit.has_attr("data-pagename"):
        card_title = tagedit["data-pagename"].strip()

    # -----------------------------
    # ② 若 data-pagename 沒有 → fallback 到麵包屑 title
    # -----------------------------
    if not card_title:
        breadcrumb = soup.find_all("a")
        if breadcrumb:
            last_a = breadcrumb[-1]
            if last_a.has_attr("title"):
                raw_title = last_a["title"]
                card_title = raw_title.split("(")[0].strip()

    # -----------------------------
    # ③ 取得圖片
    # -----------------------------
    pictures = soup.find_all("picture")
    images = []
    for pic in pictures:
        img = pic.find("img")
        if img:
            src = img.get("src")
            if src.startswith("//"):
                src = "https:" + src
            images.append(src)

    # -----------------------------
    # ④ 解析所有 atwiki_tr_xxx
    # -----------------------------
    trs = soup.find_all("tr", class_=lambda c: c and c.startswith("atwiki_tr_"))

    data = {}

    for tr in trs:
        tds = tr.find_all("td")

        clean_tds = []
        for td in tds:
            text = td.get_text(" ", strip=True)
            if text != "":
                clean_tds.append(text)

        if len(clean_tds) < 2:
            continue

        if len(clean_tds) % 2 == 1:
            clean_tds = clean_tds[:-1]

        for i in range(0, len(clean_tds), 2):
            key = clean_tds[i]
            value = clean_tds[i+1]
            data[key] = value

    # -----------------------------
    # ⑤ 加入卡片名稱
    # -----------------------------
    if card_title:
        data["card_title"] = card_title

    return images, data

# -----------------------------
# ⑥ 主程式：解析所有 HTML
# -----------------------------
for filename in os.listdir(HTML_DIR):
    if not filename.endswith(".html"):
        continue

    filepath = os.path.join(HTML_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    result = parse_card(html)
    if not result:
        print("⚠ 無法解析:", filename)
        continue

    images, data = result

    # 下載圖片
    local_images = []
    for url in images:
        img_name = url.split("/")[-1]
        save_path = os.path.join(IMG_DIR, img_name)
        download_image(url, save_path)
        local_images.append(img_name)

    # 寫入 JSON
    card_id = filename.replace(".html", "")
    json_path = os.path.join(JSON_DIR, f"{card_id}.json")

    data["images"] = local_images

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✔ 生成 JSON:", json_path)
