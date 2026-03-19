import os
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
            return True
        return False
    except:
        return False


def run(callback=None):
    """callback(progress, total)"""
    files = [f for f in os.listdir(HTML_DIR) if f.endswith(".html")]
    total = len(files)
    count = 0

    for filename in files:
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

            if src.startswith("//"):
                src = "https:" + src

            filename = src.split("/")[-1]
            save_path = os.path.join(IMG_DIR, filename)

            if not os.path.exists(save_path):
                download(src, save_path)

        count += 1
        if callback:
            callback(count, total)
