import json
import os
import re
import shutil
from tkinter import filedialog, messagebox

JSON_FILE = "merged-links-updated.json"

def load_json_with_fallback(json_file):
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f)

    messagebox.showwarning("File Not Found", f"{json_file} was not found. Please select a JSON file.")

    file_path = filedialog.askopenfilename(
        title="Select a JSON File",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )

    if not file_path:
        messagebox.showerror("Error", "No file selected. Cannot continue.")
        return None

    try:
        shutil.copy(file_path, json_file)
        messagebox.showinfo("Success", f"The file has been copied to the program directory:\n{json_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to copy file: {e}")
        return None

    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


def html_to_text(html):
    if not html:
        return ""

    html = html.replace("<br>", "\n").replace("<br/>", "\n")
    html = re.sub(r"<.*?>", "", html)
    return html.strip()

def parse_move_color(html):

    pattern = r'<span style="color:\s*(#[0-9A-Fa-f]{6})\s*;">(.*?)</span>'
    matches = re.findall(pattern, html)

    parts = []

    if matches:
        for color, text in matches:
            clean_text = re.sub(r'<!--.*?-->', '', text).strip()
            if clean_text:
                parts.append((clean_text, color))
        return parts

    clean_text = re.sub(r'<!--.*?-->', '', html).strip()
    if clean_text:
        default_color = "#000000"
        return [(clean_text, default_color)]

    return []
