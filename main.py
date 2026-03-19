import os
import tkinter as tk
from tkinter import ttk
from urllib.parse import urlparse
from PIL import Image, ImageTk
import requests
from io import BytesIO
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import threading

from utils import load_json_with_fallback, html_to_text, parse_move_color, JSON_FILE


class CardViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("tkoa Card Collector App")
        self.root.geometry("1260x620")
        self.root.minsize(1200, 620)  # 最小窗口尺寸

        # Load JSON
        self.cards = load_json_with_fallback(JSON_FILE)
        if self.cards is None:
            return

        tb.Style("litera")

        # -------------------------
        # Layout grid: 2 rows, 3 columns
        # row0: left_frame | center_frame | right_frame
        # row1: bottom_frame (gallery) spans columns 1-2
        # -------------------------
        root.grid_columnconfigure(0, weight=0)
        root.grid_columnconfigure(1, weight=0)
        root.grid_columnconfigure(2, weight=1)
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=0)

        # -------------------------
        # Left panel
        # -------------------------
        left_frame = ttk.Frame(root, width=250)
        left_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
        left_frame.grid_propagate(False)

        ttk.Label(left_frame, text="Card Name or No. ", font=("Arial", 12, "bold")).pack()
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_list)
        ttk.Entry(left_frame, textvariable=self.search_var, width=12, font=("Arial", 12, "bold")).pack(pady=5)

        ttk.Label(left_frame, text="Attribute Filtering", font=("Arial", 12, "bold")).pack(pady=5)
        self.attr_var = tk.StringVar(value="全部")
        attrs = ["全部", "黄属性", "赤属性", "青属性", "緑属性"]
        ttk.OptionMenu(left_frame, self.attr_var, "全部", *attrs, command=lambda _: self.update_list()).pack()

        ttk.Label(left_frame, text="Ethnicity Filtering", font=("Arial", 12, "bold")).pack(pady=5)
        self.race_var = tk.StringVar(value="全部")
        races = ["全部"] + sorted({c.get("race", "") for c in self.cards})
        ttk.OptionMenu(left_frame, self.race_var, "全部", *races, command=lambda _: self.update_list()).pack()

        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill="y", pady=10)

        self.listbox = tk.Listbox(list_frame, width=25, height=40)
        self.listbox.pack(side="left", fill="y")
        self.listbox.bind("<<ListboxSelect>>", self.show_card)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # -------------------------
        # Center panel
        # -------------------------
        center_frame = ttk.Frame(root, width=256)
        center_frame.grid(row=0, column=1, sticky="ns", padx=10, pady=10)
        center_frame.grid_propagate(False)

        self.image_label = ttk.Label(center_frame, text="（無圖片）", anchor="center",
                                     width=256, background="#FFFFFF", foreground="white",
                                     font=("Arial", 20, "bold"))
        self.image_label.pack(pady=10, ipady=200)

        self.image_buttons_frame = ttk.Frame(center_frame)
        self.image_buttons_frame.pack()

        # -------------------------
        # Right panel
        # -------------------------
        right_frame = ttk.Frame(root)
        right_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        right_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ttk.Label(right_frame, text="", font=("Arial", 22, "bold"))
        self.title_label.pack(pady=10, anchor="w")

        self.attr_label = ttk.Label(right_frame, text="", font=("Arial", 14, "bold"))
        self.attr_label.pack(anchor="w")

        # Info + Ability 左右排
        middle_frame = ttk.Frame(right_frame)
        middle_frame.pack(fill="x", pady=5)
        middle_frame.columnconfigure(0, weight=1)
        middle_frame.columnconfigure(1, weight=1)

        # Info
        info_frame = ttk.Frame(middle_frame)
        info_frame.grid(row=0, column=0, sticky="nsew", padx=5)
        ttk.Label(info_frame, text="Info", font=("Arial", 14, "bold")).pack(anchor="w")
        info_scroll = ttk.Scrollbar(info_frame, orient="vertical")
        info_scroll.pack(side="right", fill="y")
        self.info_text = tk.Text(info_frame, wrap="word", height=6, font=("Arial", 12, "bold"),
                                 yscrollcommand=info_scroll.set)
        self.info_text.pack(fill="both", expand=True)
        info_scroll.config(command=self.info_text.yview)

        # Ability
        ability_frame = ttk.Frame(middle_frame)
        ability_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        ttk.Label(ability_frame, text="Ability", font=("Arial", 14, "bold")).pack(anchor="w")
        ability_scroll = ttk.Scrollbar(ability_frame, orient="vertical")
        ability_scroll.pack(side="right", fill="y")
        self.ability_text = tk.Text(ability_frame, wrap="word", height=6, font=("Arial", 12, "bold"),
                                    yscrollcommand=ability_scroll.set)
        self.ability_text.pack(fill="both", expand=True)
        ability_scroll.config(command=self.ability_text.yview)

        # Description
        desc_frame = ttk.Frame(right_frame)
        desc_frame.pack(fill="x", pady=5)
        ttk.Label(desc_frame, text="Description", font=("Arial", 14, "bold")).pack(anchor="w")
        desc_scroll = ttk.Scrollbar(desc_frame, orient="vertical")
        desc_scroll.pack(side="right", fill="y")
        self.desc_text = tk.Text(desc_frame, wrap="word", font=("Arial", 12, "bold"),
                                 yscrollcommand=desc_scroll.set)
        self.desc_text.pack(fill="x")
        desc_scroll.config(command=self.desc_text.yview)

        # -------------------------
        # Bottom panel: Gallery 10x2
        # -------------------------
        bottom_frame = ttk.Frame(root)
        bottom_frame.grid(row=1, column=1, columnspan=2, sticky="ew", padx=10, pady=10)
        ttk.Label(bottom_frame, text="Deck", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=10, sticky="w")

        self.grid_cells = []
        CELL_W, CELL_H = 47, 64
        for r in range(2):
            for c in range(10):
                cell = tk.Frame(bottom_frame, width=CELL_W, height=CELL_H, bg="#cccccc", relief="solid", bd=1)
                cell.grid(row=r+1, column=c, padx=2, pady=2)
                cell.grid_propagate(False)
                self.grid_cells.append(cell)

        # Progress bar
        self.progress = ttk.Progressbar(root, mode="determinate", length=300)
        self.progress.place(x=20, rely=1.0, y=-30, anchor="sw")
        self.progress["value"] = 0
        self.progress["maximum"] = 100

        self.root.bind("<Configure>", self.resize_text_wrap)
        self.update_list()

    # -------------------------
    # Methods
    # -------------------------
    def update_list(self, *args):
        keyword = self.search_var.get().lower()
        attr_filter = self.attr_var.get()
        race_filter = self.race_var.get()
        self.listbox.delete(0, tk.END)
        for card in self.cards:
            name = card.get("name", "").lower()
            number = card.get("number", "").lower()
            if keyword not in name and keyword not in number:
                continue
            if attr_filter != "全部" and card.get("attribute_raw") != attr_filter:
                continue
            if race_filter != "全部" and card.get("race") != race_filter:
                continue
            self.listbox.insert(tk.END, card["name"])

    def show_card(self, event):
        if not self.listbox.curselection():
            return
        index = self.listbox.curselection()[0]
        name = self.listbox.get(index)
        card = next(c for c in self.cards if c["name"] == name)

        self.title_label.config(text=card["name"])
        self.show_attribute_badge(card.get("attribute_raw"))

        # Info
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

        # Move color
        move_raw = card.get("move_color", "")
        move_text, move_color = parse_move_color(move_raw)
        self.info_text.insert("end", "移動色：")
        self.info_text.insert("end", move_text + "\n", ("move_color",))
        self.info_text.tag_config("move_color", foreground=move_color)
        self.shrink_text(self.info_text)

        # Ability
        ability = html_to_text(card.get("ability_html", ""))
        self.ability_text.delete("1.0", "end")
        self.ability_text.insert("1.0", ability)
        self.shrink_text(self.ability_text)

        # Description
        desc = html_to_text(card.get("description_html", ""))
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", desc)
        self.shrink_text(self.desc_text)

        # Images
        self.show_images(card)

    def show_attribute_badge(self, attr):
        colors = {"黄": "#FFD700", "赤": "#FF4500", "青": "#1E90FF", "緑": "#32CD32"}
        color = colors.get(attr, "#AAAAAA")
        self.attr_label.config(text=attr, background=color, foreground="black")

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
        if not self.current_images:
            self.image_label.config(image="", text="（無圖片）", background="#333333", foreground="white")
            return
        self.load_image(self.current_images[0])
        for i, url in enumerate(self.current_images):
            btn = ttk.Button(self.image_buttons_frame, text=f"圖片 {i+1}", command=lambda u=url: self.load_image(u))
            btn.pack(side="left", padx=5)

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
            small = img.resize((280, 384), Image.LANCZOS)
            self.tk_img = ImageTk.PhotoImage(small)
            self.image_label.config(image=self.tk_img, text="")
        except Exception:
            self.image_label.config(image="", text="（圖片載入失敗）", background="#333333", foreground="white")

    def shrink_text(self, text_widget):
        text_widget.update_idletasks()
        lines = int(text_widget.index("end-1c").split(".")[0])
        text_widget.configure(height=max(1, lines))

    def resize_text_wrap(self, event=None):
        width = self.desc_text.winfo_width()
        if width > 50:
            wrap = width - 20
            for t in [self.info_text, self.ability_text, self.desc_text]:
                t.configure(wrap="word", wraplength=wrap)


# -------------------------
# MAIN PROGRAM
# -------------------------
if __name__ == "__main__":
    import download_images_auto

    def should_download_images():
        folder = "avalon_images"
        if not os.path.exists(folder):
            return True
        return len(os.listdir(folder)) == 0

    root = tb.Window(themename="litera")
    root.configure(bg="white")
    app = CardViewer(root)

    if should_download_images():
        def start_download():
            def update_progress(done, total):
                percent = int(done / total * 100)
                root.after(0, lambda: app.progress.config(value=percent))
                if done == total:
                    root.after(500, lambda: app.progress.place_forget())
            download_images_auto.run(callback=update_progress)

        threading.Thread(target=start_download, daemon=True).start()
    else:
        app.progress.place_forget()

    root.mainloop()
