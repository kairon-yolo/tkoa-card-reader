import os
import time
import random
import re
import json
from bs4 import BeautifulSoup

# -----------------------------
#  PART 1: Selenium 下载 atwiki
# -----------------------------
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

START = 32
END = 1056

SAVE_DIR = "avalon_pages"
os.makedirs(SAVE_DIR, exist_ok=True)

CHROME_PROFILE = r"C:\Users\User\AppData\Local\Google\Chrome\AvalonProfile"

options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={CHROME_PROFILE}")
options.add_argument("--profile-directory=Default")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def human_delay():
    time.sleep(random.uniform(2.0, 4.0))

def human_scroll(driver):
    height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(2):
        pos = random.randint(0, height)
        driver.execute_script(f"window.scrollTo(0, {pos});")
        time.sleep(random.uniform(0.5, 1.5))

print("=== STEP 1: Downloading atwiki pages ===")

for page_id in range(START, END + 1):
    save_path = os.path.join(SAVE_DIR, f"page_{page_id}.html")

    if os.path.exists(save_path):
        print(f"⏭ 已存在，跳過 page_{page_id}.html")
        continue

    url = f"https://w.atwiki.jp/avalononline-wiki/pages/{page_id}.html"
    print(f"正在下載: {url}")

    driver.get(url)
    human_delay()
    human_scroll(driver)

    html = driver.page_source

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✔ 已下載 page_{page_id}.html")
    human_delay()

driver.quit()

# -----------------------------
#  PART 2: 解析卡片资料
# -----------------------------

print("\n=== STEP 2: Parsing card data ===")

cards = []

def parse_card(html):
    soup = BeautifulSoup(html, "html.parser")

    # 卡名（页面标题）
    title = soup.select_one("#wikibody h2")
    if not title:
        return None

    name_jp = title.text.strip()

    # 过滤非卡片页面
    if len(name_jp) > 20:
        return None

    # 属性
    attribute = None
    attr_map = {
        "黄属性": "yellow",
        "青属性": "blue",
        "赤属性": "red",
        "緑属性": "green",
        "無属性": "none"
    }
    for jp, en in attr_map.items():
        if jp in html:
            attribute = en

    # 稀有度
    rarity = None
    m = re.search(r"レア度.*?([A-Z]+)", html)
    if m:
        rarity = m.group(1)

    # COST
    cost = None
    m = re.search(r"コスト.*?(\d+)", html)
    if m:
        cost = int(m.group(1))

    # 说明
    description = None
    desc = soup.find("div", id="wikibody")
    if desc:
        description = desc.text.strip()

    # 图片
    img = soup.select_one("#wikibody img")
    image_url = img["src"] if img else None

    return {
        "id": None,
        "name_jp": name_jp,
        "name_en": None,
        "series": None,
        "series_name": None,
        "attribute": attribute,
        "rarity": rarity,
        "type": None,
        "cost": cost,
        "description": description,
        "image_url": image_url
    }

for filename in os.listdir(SAVE_DIR):
    if not filename.endswith(".html"):
        continue

    path = os.path.join(SAVE_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    card = parse_card(html)
    if card:
        print("✔ 解析卡片:", card["name_jp"])
        cards.append(card)

with open("avalon_cards.json", "w", encoding="utf-8") as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

print("\n=== 完成！共解析卡片数量:", len(cards))
print("輸出檔案: avalon_cards.json")
