import json
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkhtmlview import HTMLLabel

JSON_FILE = "merged-links.json"


class CardViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Avalon Card Viewer - Modern Edition")
        self.root.geometry("1600x900")

        tb.Style("darkly")

        # 讀取 JSON
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            self.cards = json.load(f)

        # ============================
        # 左、中、右 三欄式布局
        # ============================
        main_frame = ttk.Frame(root)
        main_frame.pack(fill="both", expand=True)

        # 左欄
        left_frame = ttk.Frame(main_frame, width=250)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        # 中欄（可捲動）
        center_frame = ttk.Frame(main_frame)
        center_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # 右欄
        right_frame = ttk.Frame(main_frame, width=350)
        right_frame.pack(side="right", fill="y", padx=10, pady=10)

        # ============================
        # 左欄內容
        # ============================
        ttk.Label(left_frame, text="搜尋卡片名稱", font=("Arial", 12, "bold")).pack()
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_list)
        ttk.Entry(left_frame, textvariable=self.search_var, width=20).pack(pady=5)

        ttk.Label(left_frame, text="屬性篩選", font=("Arial", 11, "bold")).pack(pady=5)
        self.attr_var = tk.StringVar(value="全部")
        attrs = ["全部", "黄属性", "赤属性", "青属性", "緑属性"]
        ttk.OptionMenu(left_frame, self.attr_var, "全部", *attrs, command=lambda _: self.update_list()).pack()

        ttk.Label(left_frame, text="種族篩選", font=("Arial", 11, "bold")).pack(pady=5)
        self.race_var = tk.StringVar(value="全部")
        races = ["全部"] + sorted({c.get("race", "") for c in self.cards})
        ttk.OptionMenu(left_frame, self.race_var, "全部", *races, command=lambda _: self.update_list()).pack()

        # 卡片列表 + scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill="y", pady=10)

        self.listbox = tk.Listbox(list_frame, width=25, height=40)
        self.listbox.pack(side="left", fill="y")
        self.listbox.bind("<<ListboxSelect>>", self.show_card)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # ============================
        # 中欄內容（可捲動）
        # ============================
        center_canvas = tk.Canvas(center_frame)
        center_scrollbar = ttk.Scrollbar(center_frame, orient="vertical", command=center_canvas.yview)
        center_scrollbar.pack(side="right", fill="y")

        center_canvas.pack(side="left", fill="both", expand=True)
        center_canvas.configure(yscrollcommand=center_scrollbar.set)

        self.center_inner = ttk.Frame(center_canvas)
        center_canvas.create_window((0, 0), window=self.center_inner, anchor="nw")

        self.center_inner.bind("<Configure>", lambda e: center_canvas.configure(scrollregion=center_canvas.bbox("all")))

        # 中欄內容元件
        self.title_label = ttk.Label(self.center_inner, text="", font=("Arial", 22, "bold"))
        self.title_label.pack(pady=10)

        self.attr_label = ttk.Label(self.center_inner, text="", font=("Arial", 14, "bold"))
        self.attr_label.pack()

        ttk.Label(self.center_inner, text="基本資料 Info", font=("Arial", 14, "bold")).pack(pady=5)
        self.info_html = HTMLLabel(self.center_inner, html="", width=80, height=6)
        self.info_html.pack(pady=5)

        ttk.Label(self.center_inner, text="能力 Ability", font=("Arial", 14, "bold")).pack(pady=5)
        self.ability_html = HTMLLabel(self.center_inner, html="", width=80, height=8)
        self.ability_html.pack(pady=5)

        ttk.Label(self.center_inner, text="卡片說明 Description", font=("Arial", 14, "bold")).pack(pady=5)
        self.desc_html = HTMLLabel(self.center_inner, html="", width=80, height=15)
        self.desc_html.pack(pady=5)

        # ============================
        # 右欄內容（圖片）
        # ============================
        self.image_label = ttk.Label(right_frame)
        self.image_label.pack(pady=10)

        self.image_buttons_frame = ttk.Frame(right_frame)
        self.image_buttons_frame.pack()

        # 初始化列表
        self.update_list()

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
            if attr_filter != "全部" and card.get("attribute") != attr_filter:
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
        self.show_attribute_badge(card.get("attribute"))

        # 基本資料
        info = ""
        if "series" in card:
            info += f"<b>系列：</b> {card['series']}<br/>"
        if "attack" in card:
            info += f"<b>攻撃：</b> {card['attack']}<br/>"
        if "hp" in card:
            info += f"<b>耐久：</b> {card['hp']}<br/>"
        if "rare" in card:
            info += f"<b>レア：</b> {card['rare']}<br/>"
        if "race" in card:
            info += f"<b>種族：</b> {card['race']}<br/>"
        if "move_color" in card:
            move_html = card["move_color"].replace("<span", "<span style='font-size:20px;'")
            info += f"<b>移動色：</b> {move_html}<br/>"

        self.info_html.set_html(info)

        # 能力
        ability_html = card.get("ability_html", "").replace("<br>", "<br/>")
        self.ability_html.set_html(ability_html)

        # 說明
        desc_html = card.get("description_html", "").replace("<br>", "<br/>")
        self.desc_html.set_html(desc_html)

        # 圖片
        self.show_images(card)

    # ============================
    # 屬性徽章
    # ============================
    def show_attribute_badge(self, attr):
        colors = {
            "黄属性": "#FFD700",
            "赤属性": "#FF4500",
            "青属性": "#1E90FF",
            "緑属性": "#32CD32"
        }
        color = colors.get(attr, "#AAAAAA")
        self.attr_label.config(text=attr, background=color, foreground="black")

    # ============================
    # 顯示圖片
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

        if self.current_images:
            self.load_image(self.current_images[0])

        for i, url in enumerate(self.current_images):
            btn = ttk.Button(self.image_buttons_frame, text=f"圖片 {i+1}",
                             command=lambda u=url: self.load_image(u))
            btn.pack(side="left", padx=5)

    # ============================
    # 載入圖片 + 放大
    # ============================
    def load_image(self, url):
        try:
            if url.startswith("//"):
                url = "https:" + url

            response = requests.get(url)
            img = Image.open(BytesIO(response.content))

            small = img.resize((260, 360), Image.LANCZOS)
            self.tk_img = ImageTk.PhotoImage(small)
            self.image_label.config(image=self.tk_img)

            self.image_label.bind("<Button-1>", lambda e, im=img: self.open_large_image(im))

        except:
            self.image_label.config(text="圖片載入失敗")

    def open_large_image(self, img):
        top = tk.Toplevel(self.root)
        top.title("大圖")

        big = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
        tk_big = ImageTk.PhotoImage(big)

        lbl = ttk.Label(top, image=tk_big)
        lbl.image = tk_big
        lbl.pack()


# ============================
# 主程式入口
# ============================
if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = CardViewer(root)
    root.mainloop()
