import os
import time
import random
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

MERGED_FILE = "merged.json"
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
    time.sleep(random.uniform(1.5, 3.0))

def human_scroll(driver):
    height = driver.execute_script("return document.body.scrollHeight")
    pos = random.randint(0, height)
    driver.execute_script(f"window.scrollTo(0, {pos});")
    time.sleep(random.uniform(0.5, 1.0))

# -----------------------------
# 讀取 merged.json
# -----------------------------
with open(MERGED_FILE, "r", encoding="utf-8") as f:
    merged = json.load(f)

print(f"=== STEP 1: 讀取 merged.json，共 {len(merged)} 筆 ===")

# -----------------------------
# Selenium 下載每個 URL
# -----------------------------
print("\n=== STEP 2: Selenium 下載卡片頁面 ===")

for item in merged:
    url = item.get("url")
    name = item.get("name")

    if not url:
        print(f"⚠ 無 URL，跳過：{name}")
        continue

    page_id = url.split("/")[-1].replace(".html", "")
    save_path = os.path.join(SAVE_DIR, f"page_{page_id}.html")

    if os.path.exists(save_path):
        print(f"⏭ 已存在，跳過 {name} ({page_id})")
        continue

    print(f"正在下載: {name} → {url}")

    try:
        driver.get(url)
        human_delay()
        human_scroll(driver)

        html = driver.page_source

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✔ 已下載 page_{page_id}.html")

    except Exception as e:
        print(f"❌ 下載失敗 {name}: {e}")

    human_delay()
driver.quit()
