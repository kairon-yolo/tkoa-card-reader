import json
import os
import re
import shutil
from tkinter import filedialog, messagebox

JSON_FILE = "merged-links-updated.json"

def load_json_with_fallback(json_file):
    """嘗試載入 JSON_FILE，若不存在則請使用者選擇並自動複製到根目錄"""
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f)

    messagebox.showwarning("找不到檔案", f"找不到 {json_file}，請選擇 JSON 檔案")

    file_path = filedialog.askopenfilename(
        title="請選擇 JSON 檔案",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )

    if not file_path:
        messagebox.showerror("錯誤", "未選擇檔案，無法繼續")
        return None

    try:
        shutil.copy(file_path, json_file)
        messagebox.showinfo("成功", f"已將檔案複製到程式根目錄：\n{json_file}")
    except Exception as e:
        messagebox.showerror("錯誤", f"複製檔案失敗：{e}")
        return None

    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


def html_to_text(html):
    """把簡單 HTML 轉成純文字"""
    if not html:
        return ""

    html = html.replace("<br>", "\n").replace("<br/>", "\n")
    html = re.sub(r"<.*?>", "", html)
    return html.strip()


def parse_move_color(html):
    """解析 <span style='color:#xxxxxx'>●●●</span>"""
    m = re.search(r"color:\s*(#[0-9a-fA-F]{6})", html)
    color = m.group(1) if m else "#ffffff"
    text = re.sub(r"<.*?>", "", html)
    return text, color
