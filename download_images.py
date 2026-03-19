import os
import re
import requests
from bs4 import BeautifulSoup

HTML_DIR = "avalon_pages"
IMG_DIR = "avalon_images"

os.makedirs(IMG_DIR, exist_ok=True)

def download(url, path):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            print("✔ 下載成功:", path)
        else:
            print("✘ 下載失敗:", url, r.status_code)
    except Exception as e:
        print("⚠ 錯誤:", url, e)

for filename in os.listdir(HTML_DIR):
    if not filename.endswith(".html"):
        continue

    filepath = os.path.join(HTML_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    pictures = soup.find_all("picture")

    for pic in pictures:
        img = pic.find("img")
        if not img:
            continue

        src = img.get("src")
        if not src:
            continue

        # 補上 https:
        if src.startswith("//"):
            src = "https:" + src

        # 取出檔名
        filename = src.split("/")[-1]
        save_path = os.path.join(IMG_DIR, filename)

        # 避免重複下載
        if os.path.exists(save_path):
            print("略過 (已存在):", filename)
            continue

        download(src, save_path)
