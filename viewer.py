import json
import os
import tkinter as tk
from tkinter import ttk
from urllib.parse import urlparse
from PIL import Image, ImageTk
import requests
from io import BytesIO
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import re
from tkinter import filedialog, messagebox
import shutil

JSON_FILE = "merged-links-updated.json"

def load_json_with_fallback(json_file):
    first_load = False

    # 如果檔案已存在 → 直接載入
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f), first_load

    # 找不到 → 要求使用者選檔
    messagebox.showwarning("找不到檔案", f"找不到 {json_file}，請選擇 JSON 檔案")

    file_path = filedialog.askopenfilename(
        title="請選擇 JSON 檔案",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )

    if not file_path:
        messagebox.showerror("錯誤", "未選擇檔案，無法繼續")
        return None, first_load

    # 複製到根目錄
    shutil.copy(file_path, json_file)
    first_load = True

    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f), first_load




def html_to_text(html):
    """把簡單 HTML 轉成純文字"""
    if not html:
        return ""

    html = html.replace("<br>", "\n").replace("<br/>", "\n")
    html = re.sub(r"<.*?>", "", html)  # 移除所有 HTML tag
    return html.strip()


def parse_move_color(html):
    """解析 <span style='color:#xxxxxx'>●●●</span>"""
    # 抓顏色
    m = re.search(r"color:\s*(#[0-9a-fA-F]{6})", html)
    color = m.group(1) if m else "#ffffff"

    # 抓文字（●●●）
    text = re.sub(r"<.*?>", "", html)

    return text, color


class CardViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("tkoa Card Collector App")
        self.root.geometry("1260x620")
        self.root.state("zoomed")

        # 先載入 JSON
        self.cards, first_load = load_json_with_fallback(JSON_FILE)
        if self.cards is None:
            return

        # 如果是第一次載入 → 提示並關閉 App
        if first_load:
            messagebox.showinfo("完成", "資料已載入，請重新啟動 App")
            self.root.destroy()
            return

        tb.Style("litera")

        # grid 佈局
        root.grid_columnconfigure(0, weight=0)
        root.grid_columnconfigure(1, weight=0)
        root.grid_columnconfigure(2, weight=1)
        root.grid_rowconfigure(0, weight=1)


        # ============================
        # 左欄（固定寬度）
        # ============================
        left_frame = ttk.Frame(root, width=250)
        left_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
        left_frame.grid_propagate(False)

        # ============================
        # 中間欄（固定寬度 400px）
        # ============================
        center_frame = ttk.Frame(root, width=400)
        center_frame.grid(row=0, column=1, sticky="ns", padx=10, pady=10)
        center_frame.grid_propagate(False)

        # ============================
        # 右欄（可伸縮）
        # ============================
        right_frame = ttk.Frame(root)
        right_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        right_frame.grid_columnconfigure(0, weight=1)

        # ============================
        # 左欄內容
        # ============================
        ttk.Label(left_frame, text="Search Card Name", font=("Arial", 12, "bold")).pack()
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_list)
        ttk.Entry(left_frame, textvariable=self.search_var, width=12,font=("Arial", 12, "bold")).pack(pady=5)

        ttk.Label(left_frame, text="Attribute Filtering", font=("Arial", 11, "bold")).pack(pady=5)
        self.attr_var = tk.StringVar(value="全部")
        attrs = ["全部", "黄属性", "赤属性", "青属性", "緑属性"]
        ttk.OptionMenu(left_frame, self.attr_var, "全部", *attrs, command=lambda _: self.update_list()).pack()

        ttk.Label(left_frame, text="Ethnicity Filtering", font=("Arial", 11, "bold")).pack(pady=5)
        self.race_var = tk.StringVar(value="全部")
        races = ["全部"] + sorted({c.get("race", "") for c in self.cards})
        ttk.OptionMenu(left_frame, self.race_var, "全部", *races, command=lambda _: self.update_list()).pack()

        # 卡片列表
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill="y", pady=10)

        self.listbox = tk.Listbox(list_frame, width=25, height=40)
        self.listbox.pack(side="left", fill="y")
        self.listbox.bind("<<ListboxSelect>>", self.show_card)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # ============================
        # 中間欄內容（圖片區）
        # ============================
        self.image_label = ttk.Label(
            center_frame,
            text="（無圖片）",
            anchor="center",
            width=360,
            background="#FFFFFF",
            foreground="white",
            font=("Arial", 20, "bold")
        )
        self.image_label.pack(pady=10, ipady=200)  # 固定高度

        self.image_buttons_frame = ttk.Frame(center_frame)
        self.image_buttons_frame.pack()

        # ============================
        # 右欄內容（文字區）
        # ============================
  # ============================
        # 右欄內容（文字區）
        # ============================

        # Title
        self.title_label = ttk.Label(right_frame, text="", font=("Arial", 22, "bold"))
        self.title_label.pack(pady=10, anchor="w")

        # Attribute
        self.attr_label = ttk.Label(right_frame, text="", font=("Arial", 14, "bold"))
        self.attr_label.pack(anchor="w")

        # ----------------------------
        # Info 區塊（含 scrollbar）
        # ----------------------------
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill="x", pady=5)

        ttk.Label(info_frame, text="Info", font=("Arial", 14, "bold")).pack(anchor="w")

        info_scroll = ttk.Scrollbar(info_frame, orient="vertical")
        info_scroll.pack(side="right", fill="y")

        self.info_text = tk.Text(
            info_frame,
            wrap="word",
            height=4,
            font=("Arial", 12, "bold"),
            yscrollcommand=info_scroll.set
        )
        self.info_text.pack(fill="x")

        info_scroll.config(command=self.info_text.yview)

        # ----------------------------
        # Ability 區塊（含 scrollbar）
        # ----------------------------
        ability_frame = ttk.Frame(right_frame)
        ability_frame.pack(fill="x", pady=5)

        ttk.Label(ability_frame, text="Ability", font=("Arial", 14, "bold")).pack(anchor="w")

        ability_scroll = ttk.Scrollbar(ability_frame, orient="vertical")
        ability_scroll.pack(side="right", fill="y")

        self.ability_text = tk.Text(
            ability_frame,
            wrap="word",
            height=4,
            font=("Arial", 12, "bold"),
            yscrollcommand=ability_scroll.set
        )
        self.ability_text.pack(fill="x")

        ability_scroll.config(command=self.ability_text.yview)

        # ----------------------------
        # Description 區塊（含 scrollbar）
        # ----------------------------
        desc_frame = ttk.Frame(right_frame)
        desc_frame.pack(fill="both", expand=True, pady=5)

        ttk.Label(desc_frame, text="Description", font=("Arial", 14, "bold")).pack(anchor="w")

        desc_scroll = ttk.Scrollbar(desc_frame, orient="vertical")
        desc_scroll.pack(side="right", fill="y")

        self.desc_text = tk.Text(
            desc_frame,
            wrap="word",
            font=("Arial", 12, "bold"),
            yscrollcommand=desc_scroll.set
        )
        self.desc_text.pack(fill="both", expand=True)

        desc_scroll.config(command=self.desc_text.yview)

        # 自動換行
        self.root.bind("<Configure>", self.resize_text_wrap)

        self.update_list()

    # ============================
    # 自動縮小 Text widget 高度
    # ============================
    def shrink_text(self, text_widget):
        text_widget.update_idletasks()
        lines = int(text_widget.index("end-1c").split(".")[0])
        text_widget.configure(height=max(1, lines))

    # ============================
    # 右欄自動換行
    # ============================
    def resize_text_wrap(self, event=None):
        width = self.desc_text.winfo_width()
        if width > 50:
            wrap = width - 20
            for t in [self.info_text, self.ability_text, self.desc_text]:
                t.configure(wrap="word", wraplength=wrap)

    # ============================
    # 搜尋 + 篩選
    # ============================
    def update_list(self, *args):
        keyword = self.search_var.get().lower()
        attr_filter = self.attr_var.get()
        race_filter = self.race_var.get()

        self.listbox.delete(0, tk.END)

        for card in self.cards:
            name = card.get("name", "").lower()

            if keyword not in name:
                continue
            if attr_filter != "全部" and card.get("attribute_raw") != attr_filter:
                continue
            if race_filter != "全部" and card.get("race") != race_filter:
                continue

            self.listbox.insert(tk.END, card["name"])

    # ============================
    # 顯示卡片資料
    # ============================
    def show_card(self, event):
        if not self.listbox.curselection():
            return

        index = self.listbox.curselection()[0]
        name = self.listbox.get(index)
        card = next(c for c in self.cards if c["name"] == name)

        self.title_label.config(text=card["name"])
        self.show_attribute_badge(card.get("attribute_raw"))

        # 基本資料
        self.info_text.delete("1.0", "end")
        info = ""
        if "number" in card:
            info += f"No：{card['number']}\n"
        if "rare" in card:
            info += f"レア：{card['rare']}\n"           
        if "series" in card:
            info += f"系列：{card['series']}\n"
        if "race" in card:
            info += f"種族：{card['race']}\n"           
        if "attack" in card:
            info += f"攻撃：{card['attack']}\n"
        if "hp" in card:
            info += f"耐久：{card['hp']}\n"


        self.info_text.insert("1.0", info)

        # ⭐ 移動色（彩色圓點）
        move_raw = card.get("move_color", "")
        move_text, move_color = parse_move_color(move_raw)

        self.info_text.insert("end", "移動色：")
        self.info_text.insert("end", move_text + "\n", ("move_color",))
        self.info_text.tag_config("move_color", foreground=move_color)

        self.shrink_text(self.info_text)

        # 能力
        ability = html_to_text(card.get("ability_html", ""))
        self.ability_text.delete("1.0", "end")
        self.ability_text.insert("1.0", ability)
        self.shrink_text(self.ability_text)

        # 說明
        desc = html_to_text(card.get("description_html", ""))
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", desc)
        self.shrink_text(self.desc_text)

        # 圖片
        self.show_images(card)

    # ============================
    # 屬性徽章
    # ============================
    def show_attribute_badge(self, attr):
        colors = {
            "黄": "#FFD700",
            "赤": "#FF4500",
            "青": "#1E90FF",
            "緑": "#32CD32"
        }
        color = colors.get(attr, "#AAAAAA")
        self.attr_label.config(text=attr, background=color, foreground="black")

    # ============================
    # 顯示圖片（本地優先）
    # ============================
    def show_images(self, card):
        for widget in self.image_buttons_frame.winfo_children():
            widget.destroy()

        self.current_images = []

        if "image_url" in card:
            self.current_images.append(card["image_url"])

        if "images" in card:
            for imgset in card["images"]:
                if "original" in imgset:
                    self.current_images.append(imgset["original"])

        # 沒有圖片 → 顯示 placeholder
        if not self.current_images:
            self.image_label.config(
                image="",
                text="（無圖片）",
                background="#333333",
                foreground="white"
            )
            return

        # 有圖片 → 顯示第一張
        self.load_image(self.current_images[0])

        # 建立切換按鈕
        for i, url in enumerate(self.current_images):
            btn = ttk.Button(self.image_buttons_frame, text=f"圖片 {i+1}",
                             command=lambda u=url: self.load_image(u))
            btn.pack(side="left", padx=5)

    # ============================
    # 載入圖片（本地優先）
    # ============================
    def load_image(self, url):
        try:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)

            local_folder = "avalon_images"
            local_path = os.path.join(local_folder, filename)

            if os.path.exists(local_path):
                img = Image.open(local_path)
            else:
                if url.startswith("//"):
                    url = "https:" + url
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))

            small = img.resize((360, 500), Image.LANCZOS)
            self.tk_img = ImageTk.PhotoImage(small)
            self.image_label.config(image=self.tk_img, text="")

        except Exception:
            self.image_label.config(
                image="",
                text="（圖片載入失敗）",
                background="#333333",
                foreground="white"
            )

    def open_large_image(self, img):
        top = tk.Toplevel(self.root)
        top.title("大圖")

        big = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
        tk_big = ImageTk.PhotoImage(big)

        lbl = ttk.Label(top, image=tk_big)
        lbl.image = tk_big
        lbl.pack()
    def scale_ui(self, factor):
        self.root.tk.call('tk', 'scaling', factor)

# ============================
# 主程式入口
# ============================
if __name__ == "__main__":
    root = tb.Window(themename="litera")
    root.configure(bg="white")
    app = CardViewer(root)
    root.mainloop()
