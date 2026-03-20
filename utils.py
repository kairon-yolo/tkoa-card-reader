import json
import os
import re
import shutil
from tkinter import filedialog, messagebox

JSON_FILE = "merged-links-updated.json"

def load_json_with_fallback(json_file):
    """
    Try to load JSON_FILE.  
    If it does not exist, ask the user to select a JSON file and automatically copy it to the program root.
    """
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
    """
    Convert simple HTML into plain text.
    Supports <br> and removes all other tags.
    """
    if not html:
        return ""

    html = html.replace("<br>", "\n").replace("<br/>", "\n")
    html = re.sub(r"<.*?>", "", html)
    return html.strip()


def parse_move_color(html):
    """
    Parse HTML like:
        <span style='color:#xxxxxx'>●●●</span>
    Returns (text, color)
    """
    m = re.search(r"color:\s*(#[0-9a-fA-F]{6})", html)
    color = m.group(1) if m else "#ffffff"
    text = re.sub(r"<.*?>", "", html)
    return text, color
