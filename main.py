import sys
from tkinter import filedialog, messagebox
from tkinter import ttk
import customtkinter as ctk
import time
import os
import json
import random
import threading
import queue
import urllib.request
import webbrowser
from datetime import datetime

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

__version__ = "2"
UPDATE_URL = "https://raw.githubusercontent.com/versozadarwin23/fbcookie/refs/heads/main/main.py"
VERSION_CHECK_URL = "https://raw.githubusercontent.com/versozadarwin23/fbcookie/refs/heads/main/version.txt"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

COLORS = {
    "bg_main": "#0D1117",
    "bg_card": "#161B22",
    "bg_lighter": "#21262D",
    "primary": "#58A6FF",
    "success": "#2EA043",
    "warning": "#E3B341",
    "danger": "#F85149",
    "text_main": "#C9D1D9",
    "text_sub": "#8B949E",
    "border": "#30363D"
}

FONT_HEADER = ("Roboto", 18, "bold")
FONT_SUBHEADER = ("Roboto", 13, "bold")
FONT_BODY = ("Roboto", 11)


class StatCard(ctk.CTkFrame):
    def __init__(self, parent, title, value, icon, color):
        super().__init__(parent, fg_color=COLORS["bg_card"], corner_radius=10, border_width=1,
                         border_color=COLORS["border"])
        self.value_var = ctk.StringVar(value=str(value))
        self.icon_label = ctk.CTkLabel(self, text=icon, font=("Segoe UI Emoji", 20))
        self.icon_label.place(relx=0.85, rely=0.25, anchor="center")
        self.title_label = ctk.CTkLabel(self, text=title.upper(), font=("Roboto", 10, "bold"),
                                        text_color=COLORS["text_sub"])
        self.title_label.pack(anchor="w", padx=10, pady=(8, 0))
        self.value_label = ctk.CTkLabel(self, textvariable=self.value_var, font=("Roboto", 22, "bold"),
                                        text_color=color)
        self.value_label.pack(anchor="w", padx=10, pady=(0, 8))

    def update_value(self, new_value):
        self.value_var.set(str(new_value))


class StatsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        title = ctk.CTkLabel(self, text="📊 LIVE ANALYTICS", font=FONT_SUBHEADER, text_color=COLORS["primary"])
        title.pack(anchor="w", pady=(0, 5))
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True)
        self.grid_frame.grid_columnconfigure((0, 1), weight=1)
        self.card_shares = StatCard(self.grid_frame, "Total Shares", "0", "🚀", COLORS["success"])
        self.card_shares.grid(row=0, column=0, padx=(0, 3), pady=3, sticky="ew")
        self.card_failed = StatCard(self.grid_frame, "Failed", "0", "⚠️", COLORS["danger"])
        self.card_failed.grid(row=0, column=1, padx=(3, 0), pady=3, sticky="ew")
        self.card_devices = StatCard(self.grid_frame, "Active Threads", "0", "💻", COLORS["warning"])
        self.card_devices.grid(row=1, column=0, columnspan=2, padx=0, pady=(3, 3), sticky="ew")

    def update_stats(self, shares, failed):
        self.card_shares.update_value(shares)
        self.card_failed.update_value(failed)

    def update_devices(self, count):
        self.card_devices.update_value(count)


class PairFrame(ctk.CTkFrame):
    def __init__(self, parent, pair_num, on_remove):
        super().__init__(parent, fg_color=COLORS["bg_lighter"], corner_radius=8, border_width=1,
                         border_color=COLORS["border"])
        self.on_remove = on_remove
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(8, 2))
        self.header_label = ctk.CTkLabel(header, text=f"📍 LINK #{pair_num}", font=("Roboto", 12, "bold"),
                                         text_color=COLORS["primary"])
        self.header_label.pack(side="left")
        if pair_num > 1:
            btn_del = ctk.CTkButton(header, text="✖", width=25, height=25, fg_color="transparent",
                                    hover_color=COLORS["danger"], text_color=COLORS["text_sub"], corner_radius=6,
                                    command=self.remove)
            btn_del.pack(side="right")
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=(0, 10))
        self.link_entry = ctk.CTkEntry(content, height=30, placeholder_text="Enter Target URL",
                                       fg_color=COLORS["bg_main"], border_color=COLORS["border"], corner_radius=6,
                                       font=FONT_BODY)
        self.link_entry.pack(fill="x", pady=(0, 8))
        cap_row = ctk.CTkFrame(content, fg_color="transparent")
        cap_row.pack(fill="x")
        self.caption_path = ctk.CTkEntry(cap_row, height=30, placeholder_text="Caption File (.txt)",
                                         fg_color=COLORS["bg_main"], border_color=COLORS["border"], corner_radius=6,
                                         font=FONT_BODY)
        self.caption_path.pack(side="left", fill="x", expand=True, padx=(0, 5))
        btn_browse = ctk.CTkButton(cap_row, text="📂", width=40, height=30, fg_color=COLORS["bg_card"],
                                   hover_color=COLORS["primary"], border_width=1, border_color=COLORS["border"],
                                   corner_radius=6, command=self.browse_caption)
        btn_browse.pack(side="right")

    def remove(self):
        self.on_remove()

    def browse_caption(self):
        file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file:
            self.caption_path.delete(0, "end")
            self.caption_path.insert(0, file)


class FacebookAutomationGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.log_storage = {"auto": [], "debug": [], "sys": []}
        self.saved_settings = {}
        self.active_browsers = []
        self.cookie_queue = queue.Queue()

        self.title(f"AutoPost V{__version__}")
        self.geometry("1100x700")
        self.after(0, lambda: self.state("zoomed"))
        self.configure(fg_color=COLORS["bg_main"])

        self.is_running = False
        self.global_cookie_path = ""
        self.worker_threads = []
        self.active_worker_count = 0
        self.pair_widgets = []
        self.total_shares = 0
        self.error_count = 0
        self.total_attempts = 0
        self.job_list_global = []

        self.load_settings()
        self.layout_ui()
        self.check_for_updates()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def check_for_updates(self, manual=False):
        if manual:
            self.status_badge.configure(text="● CHECKING...", text_color=COLORS["warning"])

        def _check():
            try:
                req = urllib.request.Request(VERSION_CHECK_URL, headers={'Cache-Control': 'no-cache'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    remote_version = response.read().decode('utf-8').strip()
                if remote_version and remote_version != __version__:
                    self.after(0, lambda: self.show_update_popup(remote_version))
                else:
                    if manual:
                        self.after(0, lambda: messagebox.showinfo("Up to Date", f"Latest Version: V{__version__}"))
            except:
                pass
            finally:
                if manual:
                    self.after(0, lambda: self.status_badge.configure(text="● IDLE", text_color=COLORS["text_sub"]))

        threading.Thread(target=_check, daemon=True).start()

    def show_update_popup(self, remote_version):
        msg = f"A new update is available! (Version V{remote_version})\n\nWould you like to download and install the update now?"
        response = messagebox.askyesno("Update Available", msg)

        if response:
            try:
                req = urllib.request.Request(UPDATE_URL, headers={'Cache-Control': 'no-cache'})
                with urllib.request.urlopen(req, timeout=10) as download_response:
                    new_code = download_response.read().decode('utf-8')

                current_file = os.path.abspath(__file__)
                with open(current_file, 'w', encoding='utf-8') as f:
                    f.write(new_code)

                messagebox.showinfo("Update Complete",
                                    "The application has been updated successfully. It will now restart.")

                os.execl(sys.executable, sys.executable, *sys.argv)

            except Exception as e:
                messagebox.showerror("Update Failed", f"An error occurred while updating:\n{e}")
                self.after(120000, self.check_for_updates)
        else:
            self.after(120000, self.check_for_updates)

    def layout_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], height=50, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(header, text=f"AUTOPOST V{__version__}", font=FONT_HEADER, text_color=COLORS["primary"]).pack(
            side="left", padx=15, pady=10)
        self.status_badge = ctk.CTkLabel(header, text="● IDLE", font=("Roboto", 12, "bold"),
                                         text_color=COLORS["text_sub"])
        self.status_badge.pack(side="right", padx=15)

        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_content.grid_rowconfigure(0, weight=1)
        main_content.grid_columnconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(main_content, fg_color=COLORS["bg_main"], corner_radius=10)
        self.tabview.grid(row=0, column=0, sticky="nsew")

        self.tab_dash = self.tabview.add(" Dashboard ")
        self.tab_logs = self.tabview.add(" System Logs ")

        self.setup_dashboard()
        self.setup_logs()

    def setup_dashboard(self):
        self.tab_dash.grid_columnconfigure(1, weight=1)
        self.tab_dash.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkScrollableFrame(self.tab_dash, fg_color="transparent", width=330)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        self.overall_stats = StatsFrame(left_panel)
        self.overall_stats.pack(fill="x", pady=(0, 10))

        control_frame = ctk.CTkFrame(left_panel, fg_color=COLORS["bg_card"], corner_radius=10)
        control_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(control_frame, text="PC AUTOMATION CONTROL", font=("Roboto", 11, "bold"),
                     text_color=COLORS["text_sub"]).pack(anchor="w", padx=15, pady=(10, 5))

        lbl_cookies = ctk.CTkLabel(control_frame, text="Cookie File Path:", font=("Roboto", 11, "bold"),
                                   text_color=COLORS["text_sub"])
        lbl_cookies.pack(anchor="w", padx=15, pady=(5, 0))

        cookie_row = ctk.CTkFrame(control_frame, fg_color="transparent")
        cookie_row.pack(fill="x", padx=10, pady=(0, 10))

        self.cookie_entry = ctk.CTkEntry(cookie_row, height=30, placeholder_text="Path to cookies.txt")
        self.cookie_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.cookie_entry.insert(0, self.global_cookie_path)

        btn_browse = ctk.CTkButton(cookie_row, text="📂", width=40, height=30, fg_color=COLORS["bg_card"],
                                   hover_color=COLORS["primary"], border_width=1, border_color=COLORS["border"],
                                   corner_radius=6, command=self.browse_global_cookie)
        btn_browse.pack(side="right")

        btn_grid = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_grid.pack(fill="x", padx=10, pady=5)
        self.start_btn = ctk.CTkButton(btn_grid, text="▶ START", height=40, fg_color=COLORS["success"],
                                       hover_color="#1E8233", font=("Roboto", 13, "bold"), command=self.start_threads)
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.stop_btn = ctk.CTkButton(btn_grid, text="⏹ STOP", height=40, fg_color=COLORS["danger"],
                                      hover_color="#C53030", font=("Roboto", 13, "bold"), state="disabled",
                                      command=self.stop_automation)
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))

        lbl_delay = ctk.CTkLabel(control_frame, text="Pre/Post Action Delay (s)", font=("Roboto", 11, "bold"),
                                 text_color=COLORS["text_sub"])
        lbl_delay.pack(anchor="w", padx=15, pady=(5, 0))
        delay_row = ctk.CTkFrame(control_frame, fg_color="transparent")
        delay_row.pack(fill="x", padx=10, pady=(0, 10))
        self.dash_pre_delay = ctk.CTkEntry(delay_row, width=60, height=28, justify="center")
        self.dash_pre_delay.pack(side="left", padx=5)
        self.dash_pre_delay.insert(0, "10")
        ctk.CTkLabel(delay_row, text="/", font=("Roboto", 14, "bold")).pack(side="left")
        self.dash_post_delay = ctk.CTkEntry(delay_row, width=60, height=28, justify="center")
        self.dash_post_delay.pack(side="left", padx=5)
        self.dash_post_delay.insert(0, "10")

        ctk.CTkButton(control_frame, text="💾 Save Configuration", height=30, fg_color=COLORS["bg_card"],
                      border_width=1, border_color=COLORS["primary"], font=FONT_BODY,
                      command=self.save_config).pack(fill="x", padx=12, pady=(5, 5))
        ctk.CTkButton(control_frame, text="🔄 Check for Updates", height=30,
                      fg_color=COLORS["bg_card"], border_width=1,
                      border_color=COLORS["warning"], text_color=COLORS["warning"],
                      font=FONT_BODY, hover_color="#3D3014",
                      command=lambda: self.check_for_updates(manual=True)).pack(fill="x", padx=12, pady=(0, 15))
        right_panel = ctk.CTkFrame(self.tab_dash, fg_color=COLORS["bg_card"], corner_radius=10)
        right_panel.grid(row=0, column=1, sticky="nsew")
        header = ctk.CTkFrame(right_panel, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(header, text="TASKS", font=FONT_SUBHEADER, text_color=COLORS["primary"]).pack(side="left")
        ctk.CTkButton(header, text="+ Add", width=80, height=30, fg_color=COLORS["primary"], font=FONT_BODY,
                      command=self.add_pair).pack(side="right")
        self.pairs_scroll = ctk.CTkScrollableFrame(right_panel, fg_color="transparent")
        self.pairs_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        self.add_pair()

    def setup_logs(self):
        self.tab_logs.grid_columnconfigure(0, weight=1)
        self.tab_logs.grid_rowconfigure(1, weight=1)

        top_bar = ctk.CTkFrame(self.tab_logs, fg_color="transparent", height=40)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 5))
        ctk.CTkLabel(top_bar, text="VIEWING LOGS:", font=FONT_SUBHEADER).pack(side="left", padx=(0, 10))

        self.log_shares_label = ctk.CTkLabel(top_bar, text="✅ SHARES: 0", font=("Roboto", 12, "bold"),
                                             text_color=COLORS["success"])
        self.log_shares_label.pack(side="left", padx=(0, 15))

        self.logs_stop_btn = ctk.CTkButton(top_bar, text="⏹ STOP", width=80, height=28, fg_color=COLORS["danger"],
                                           hover_color="#C53030", state="disabled", command=self.stop_automation)
        self.logs_stop_btn.pack(side="right", padx=(0, 5))
        ctk.CTkButton(top_bar, text="🗑 Clear", width=100, height=28, fg_color=COLORS["bg_card"], border_width=1,
                      border_color=COLORS["border"], command=self.clear_logs).pack(side="right", padx=(0, 10))

        logs_container = ctk.CTkFrame(self.tab_logs, fg_color="transparent")
        logs_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        logs_container.grid_columnconfigure(0, weight=1)
        logs_container.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=COLORS["bg_card"], foreground=COLORS["text_main"],
                        fieldbackground=COLORS["bg_card"], borderwidth=0, rowheight=22, font=("Roboto", 10))
        style.map('Treeview', background=[('selected', COLORS["primary"])])
        style.configure("Treeview.Heading", background=COLORS["bg_lighter"], foreground=COLORS["text_main"],
                        font=("Roboto", 10, "bold"))

        f1 = ctk.CTkFrame(logs_container, fg_color="transparent")
        f1.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        ctk.CTkLabel(f1, text="📝 MAIN LOGS", font=FONT_SUBHEADER, text_color=COLORS["primary"]).pack(anchor="w")
        tree_f1 = ctk.CTkFrame(f1, corner_radius=0, fg_color="transparent")
        tree_f1.pack(fill="both", expand=True)

        cols1 = ("Time", "Worker", "Link", "Caption", "Status")
        self.table_auto = ttk.Treeview(tree_f1, columns=cols1, show="headings", height=8)

        self.table_auto.heading("Time", text="TIME")
        self.table_auto.column("Time", width=80)
        self.table_auto.heading("Worker", text="WORKER")
        self.table_auto.column("Worker", width=80)
        self.table_auto.heading("Link", text="LINK")
        self.table_auto.column("Link", width=200)
        self.table_auto.heading("Caption", text="CAPTION")
        self.table_auto.column("Caption", width=200)
        self.table_auto.heading("Status", text="STATUS")
        self.table_auto.column("Status", width=100)

        sb1 = ctk.CTkScrollbar(tree_f1, command=self.table_auto.yview)
        self.table_auto.configure(yscrollcommand=sb1.set)
        sb1.pack(side="right", fill="y")
        self.table_auto.pack(side="left", fill="both", expand=True)
        self.table_auto.tag_configure("SUCCESS", foreground=COLORS["success"])
        self.table_auto.tag_configure("ERROR", foreground=COLORS["danger"])
        self.table_auto.tag_configure("WARN", foreground=COLORS["warning"])
        self.table_auto.bind("<Double-1>", self.on_log_double_click)

    def log_row(self, worker_id, link, caption, status, level="INFO"):
        ts = datetime.now().strftime("%I:%M:%S %p")
        d_name = worker_id

        disp_link = (link[:30] + '...') if len(link) > 30 else link
        disp_cap = (caption[:30] + '...') if caption and len(caption) > 30 else caption
        if not disp_cap: disp_cap = "---"

        self.after(10, lambda: self._safe_insert(self.table_auto, (ts, d_name, disp_link, disp_cap, status), level))

    def _safe_insert(self, tree, values, tag):
        try:
            tree.insert("", "end", values=values, tags=(tag,))
            children = tree.get_children()
            if len(children) > 100:
                tree.delete(children[0])
        except:
            pass

    def clear_logs(self):
        for item in self.table_auto.get_children():
            self.table_auto.delete(item)

    def on_log_double_click(self, event):
        try:
            tree = event.widget
            item = tree.item(tree.identify_row(event.y))
            url = item['values'][2]
            if "http" in url:
                webbrowser.open(url)
        except:
            pass

    def on_close(self):
        self.stop_automation()
        self.destroy()
        os._exit(0)

    def browse_global_cookie(self):
        f = filedialog.askopenfilename(filetypes=[("Txt", "*.txt")])
        if f:
            self.cookie_entry.delete(0, "end")
            self.cookie_entry.insert(0, f)
            self.global_cookie_path = f

    def load_settings(self):
        try:
            with open("pc_settings.json", "r") as f:
                d = json.load(f)
                self.global_cookie_path = d.get("global_cookie_path", "")
                self.after(500, lambda: self._set_vals(d))
        except:
            pass

    def _set_vals(self, d):
        try:
            self.dash_pre_delay.delete(0, "end")
            self.dash_pre_delay.insert(0, d.get("dash_pre_delay", "10"))
            self.dash_post_delay.delete(0, "end")
            self.dash_post_delay.insert(0, d.get("dash_post_delay", "10"))

            if hasattr(self, 'cookie_entry'):
                self.cookie_entry.delete(0, "end")
                self.cookie_entry.insert(0, d.get("global_cookie_path", ""))
        except:
            pass

    def save_config(self):
        self.global_cookie_path = self.cookie_entry.get()
        self.saved_settings = {
            "global_cookie_path": self.global_cookie_path,
            "dash_pre_delay": self.dash_pre_delay.get(),
            "dash_post_delay": self.dash_post_delay.get(),
        }
        with open("pc_settings.json", "w") as f:
            json.dump(self.saved_settings, f, indent=2)
        messagebox.showinfo("Saved", "Configuration updated.")

    def add_pair(self):
        pair_num = len(self.pair_widgets) + 1
        new_pair = PairFrame(self.pairs_scroll, pair_num, lambda: self.remove_pair(new_pair))
        new_pair.pack(fill="x", padx=5, pady=5)
        self.pair_widgets.append(new_pair)

    def remove_pair(self, frame):
        if len(self.pair_widgets) > 1:
            frame.destroy()
            self.pair_widgets.remove(frame)
            for i, f in enumerate(self.pair_widgets):
                f.header_label.configure(text=f"📍 LINK #{i + 1}")

    def parse_playwright_cookies(self, cookie_str):
        cookies = []
        for pair in cookie_str.split(";"):
            if "=" in pair:
                name, value = pair.strip().split("=", 1)
                cookies.append({
                    "name": name,
                    "value": value,
                    "domain": ".facebook.com",
                    "path": "/"
                })
        return cookies

    # --- PLAYWRIGHT AUTOMATION ENGINE ---
    def run_pc_automation(self, worker_id):
        self.log_row(worker_id, "---", "---", "🚀 STARTED", "INFO")

        try:
            pre_wait = float(self.dash_pre_delay.get())
        except:
            pre_wait = 5.0

        limit = 0
        processed = 0

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=
                [
                    "--blink-settings=imagesEnabled=false,videoAutoplayEnabled=false",
                    "--disable-notifications",
                    "--no-sandbox",
                    "--mute-audio",
                    "--disable-popup-blocking",
                    "--disable-infobars"
                    "--blink-settings=imagesEnabled=false,videoAutoplayEnabled=false",
                    "--disable-notifications",
                    "--disable-dev-shm-usage",
                    "--disable-extensions",
                    "--disable-infobars",
                    "--ignore-certificate-errors"
                    "--renderer-process-limit=1",
                    "--single-process",
                    "--disable-background-networking",
                    "--disable-sync",
                    "--disable-translate"
                    "--disk-cache-size=1"
                    "--media-cache-size=1"
                ]
            )
            self.active_browsers.append(browser)

            while self.is_running:
                if limit > 0 and processed >= limit:
                    self.log_row(worker_id, "---", "---", "⛔ LIMIT REACHED", "WARN")
                    break
                try:
                    data = self.cookie_queue.get(timeout=2)
                    cookie_str = data['cookie']
                    acc_idx = data['index']
                except queue.Empty:
                    if self.cookie_queue.empty():
                        break
                    continue

                processed += 1
                context = None
                try:
                    context = browser.new_context(
                        viewport={'width': 360, 'height': 640},
                        user_agent="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
                    )
                    page = context.new_page()

                    cookies = self.parse_playwright_cookies(cookie_str)
                    if cookies:
                        context.add_cookies(cookies)

                    for ln, (link, cap_file) in enumerate(self.job_list_global, 1):
                        if not self.is_running:
                            break
                        sel_cap = "---"
                        success = False
                        for attempt in range(2):
                            if not self.is_running:
                                break
                            try:
                                client = context.new_cdp_session(page)
                                client.send("Network.setUserAgentOverride", {
                                    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                                    "platform": "Win32",
                                    "acceptLanguage": "en-US,en;q=0.9"
                                })

                                blocked_urls = [
                                    "*.jpg", "*.jpeg", "*.png", "*.gif",
                                    "*.css",
                                    "*.mp4", "*.avi",
                                    "*.woff", "*.woff2", "*.ttf",
                                    "*.ico",
                                    "*favicon*",
                                ]

                                client.send("Network.enable")
                                client.send("Network.setBlockedURLs", {"urls": blocked_urls})

                                page.goto(f"https://www.facebook.com/sharer/sharer.php?u={link}", timeout=90 * 1000)
                                dialog_xpath = "xpath=//*[@aria-label='Close composer dialog']"
                                dialog_locator = page.locator(dialog_xpath).first

                                try:
                                    dialog_locator.wait_for(state="visible", timeout=30000)
                                except PlaywrightTimeoutError:
                                    self.log_row(worker_id, link, "---", f"EXPIRED COOKIE Account {acc_idx} LINK {ln}", "ERROR")
                                    success = False
                                    break
                                if cap_file and os.path.exists(cap_file):
                                    try:
                                        with open(cap_file, "r", encoding="utf-8") as f:
                                            lines = [x.strip() for x in f if x.strip()]
                                        if lines:
                                            sel_cap = random.choice(lines)
                                            page.keyboard.type(sel_cap)
                                            time.sleep(pre_wait)
                                    except:
                                        pass

                                post_xpath = "xpath=//*[@aria-label='Share']"
                                post_btn = page.locator(post_xpath).first
                                post_btn.scroll_into_view_if_needed()
                                post_btn.click()
                                try:
                                    post_btn.wait_for(state="detached", timeout=30000)
                                    self.log_row(worker_id, link, sel_cap, f"SUCCESS LINK {ln} Account {acc_idx}", "SUCCESS")
                                    self.total_shares += 1
                                    self.total_attempts += 1
                                    self.update_stats()
                                    success = True
                                    break
                                except:
                                    pass

                            except Exception as e:
                                try:
                                    page.reload()
                                except:
                                    pass

                        if not success:
                            self.total_attempts += 1
                            self.update_stats()
                            break

                    if context:
                        context.close()
                except Exception as e:
                    self.log_row(worker_id, "---", "---", f"CRASH: {str(e)[:30]}", "ERROR")
                    if context:
                        try:
                            context.close()
                        except:
                            pass
                finally:
                    if self.is_running:
                        try:
                            self.cookie_queue.task_done()
                        except:
                            pass

            if browser in self.active_browsers:
                self.active_browsers.remove(browser)
            browser.close()

        self.active_worker_count -= 1
        self.overall_stats.update_devices(self.active_worker_count)

    def update_stats(self):
        self.after(0, lambda: self.overall_stats.update_stats(self.total_shares, self.error_count))
        if hasattr(self, 'log_shares_label'):
            self.after(0, lambda: self.log_shares_label.configure(text=f"✅ SHARES: {self.total_shares}"))

    def start_threads(self):
        self.job_list_global = [(p.link_entry.get(), p.caption_path.get()) for p in self.pair_widgets if
                                p.link_entry.get().strip()]
        if not self.job_list_global:
            messagebox.showerror("Error", "No links configured!")
            return
        if not os.path.exists(self.cookie_entry.get()):
            messagebox.showerror("Error", "Invalid Cookie File!")
            return

        try:
            with open(self.cookie_entry.get(), "r") as f:
                ac = [l.strip() for l in f if l.strip()]
            if not ac:
                raise Exception
        except:
            messagebox.showerror("Error", "Cookie file empty/error!")
            return

        self._launch_workers(ac)

    def _launch_workers(self, ac):
        num_accounts = len(ac)

        # DITO MO I-EDIT ANG NUMBER OF THREADS (1 hanggang 10 ay recommended):
        max_threads_cap = 10

        num_threads = min(num_accounts, max_threads_cap)

        if num_threads < 1:
            num_threads = 1

        with self.cookie_queue.mutex:
            self.cookie_queue.queue.clear()
        for i, c in enumerate(ac):
            self.cookie_queue.put({'cookie': c, 'index': i + 1})

        self.is_running = True
        self.status_badge.configure(text="● RUNNING", text_color=COLORS["success"])

        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        try:
            self.logs_stop_btn.configure(state="normal")
        except:
            pass

        self.tabview.set(" System Logs ")

        self.worker_threads = []
        for i in range(num_threads):
            t = threading.Thread(target=self.run_pc_automation, args=(f"Worker-{i + 1}",))
            t.start()
            self.worker_threads.append(t)
            self.active_worker_count += 1
            self.overall_stats.update_devices(self.active_worker_count)

        def monitor():
            while self.is_running:
                alive = [t for t in self.worker_threads if t.is_alive()]
                if not alive:
                    break
                time.sleep(1)

            self.is_running = False
            self.after(0, lambda: self.status_badge.configure(text="● FINISHED", text_color=COLORS["text_sub"]))
            self.after(0, lambda: self.start_btn.configure(state="normal"))
            self.after(0, lambda: self.stop_btn.configure(state="disabled"))

        threading.Thread(target=monitor, daemon=True).start()

    def stop_automation(self):
        self.is_running = False
        self.stop_btn.configure(state="disabled")
        self.status_badge.configure(text="● STOPPING...", text_color=COLORS["danger"])

        with self.cookie_queue.mutex:
            self.cookie_queue.queue.clear()

        def kill():
            for b in list(self.active_browsers):
                try:
                    b.close()
                except:
                    pass
            self.active_browsers = []
            self.after(0, lambda: messagebox.showinfo("Stopped", "Automation Force Stopped."))

        threading.Thread(target=kill, daemon=True).start()


if __name__ == "__main__":
    app = FacebookAutomationGUI()
    app.mainloop()

