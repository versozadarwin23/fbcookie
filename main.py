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
import traceback
import shutil
from datetime import datetime
import hashlib

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

__version__ = "10"
UPDATE_URL = "https://raw.githubusercontent.com/versozadarwin23/fbcookie/refs/heads/main/main.py"
VERSION_CHECK_URL = "https://raw.githubusercontent.com/versozadarwin23/fbcookie/refs/heads/main/version.txt"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

COLORS = {
    "bg_main": "#0F172A",
    "bg_card": "#1E293B",
    "bg_lighter": "#334155",
    "primary": "#3B82F6",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "text_main": "#F8FAFC",
    "text_sub": "#94A3B8",
    "border": "#475569"
}

FONT_HEADER = ("Roboto", 20, "bold")
FONT_SUBHEADER = ("Roboto", 14, "bold")
FONT_BODY = ("Roboto", 12)


class StatCard(ctk.CTkFrame):
    def __init__(self, parent, title, value, icon, color):
        super().__init__(parent, fg_color=COLORS["bg_card"], corner_radius=15, border_width=1,
                         border_color=COLORS["border"])
        self.value_var = ctk.StringVar(value=str(value))
        self.icon_label = ctk.CTkLabel(self, text=icon, font=("Segoe UI Emoji", 26))
        self.icon_label.place(relx=0.85, rely=0.35, anchor="center")
        self.title_label = ctk.CTkLabel(self, text=title.upper(), font=("Roboto", 11, "bold"),
                                        text_color=COLORS["text_sub"])
        self.title_label.pack(anchor="w", padx=15, pady=(12, 0))
        self.value_label = ctk.CTkLabel(self, textvariable=self.value_var, font=("Roboto", 28, "bold"),
                                        text_color=color)
        self.value_label.pack(anchor="w", padx=15, pady=(0, 12))

    def update_value(self, new_value):
        self.value_var.set(str(new_value))


class StatsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        title = ctk.CTkLabel(self, text="📊 LIVE ANALYTICS", font=FONT_SUBHEADER, text_color=COLORS["primary"])
        title.pack(anchor="w", pady=(0, 10))
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True)
        self.grid_frame.grid_columnconfigure((0, 1), weight=1)
        self.card_shares = StatCard(self.grid_frame, "Total Shares", "0", "🚀", COLORS["success"])
        self.card_shares.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")
        self.card_failed = StatCard(self.grid_frame, "Failed", "0", "⚠️", COLORS["danger"])
        self.card_failed.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="ew")
        self.card_cookies = StatCard(self.grid_frame, "Total Cookies", "0", "🍪", COLORS["primary"])
        self.card_cookies.grid(row=1, column=0, padx=(0, 5), pady=(5, 5), sticky="ew")
        self.card_devices = StatCard(self.grid_frame, "Active Threads", "0", "💻", COLORS["warning"])
        self.card_devices.grid(row=1, column=1, padx=(5, 0), pady=(5, 5), sticky="ew")

    def update_stats(self, shares, failed):
        self.card_shares.update_value(shares)
        self.card_failed.update_value(failed)

    def update_devices(self, count):
        self.card_devices.update_value(count)

    def update_cookies(self, count):
        self.card_cookies.update_value(count)


class PairFrame(ctk.CTkFrame):
    def __init__(self, parent, pair_num, on_remove):
        super().__init__(parent, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1,
                         border_color=COLORS["border"])
        self.on_remove = on_remove
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(10, 5))
        self.header_label = ctk.CTkLabel(header, text=f"📍 LINK #{pair_num}", font=("Roboto", 13, "bold"),
                                         text_color=COLORS["primary"])
        self.header_label.pack(side="left")
        if pair_num > 1:
            btn_del = ctk.CTkButton(header, text="✖", width=28, height=28, fg_color="transparent",
                                    hover_color=COLORS["danger"], text_color=COLORS["text_sub"], corner_radius=8,
                                    command=self.remove)
            btn_del.pack(side="right")
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=(0, 15))
        self.link_entry = ctk.CTkEntry(content, height=35, placeholder_text="Enter Target URL",
                                       fg_color=COLORS["bg_main"], border_color=COLORS["border"], corner_radius=8,
                                       font=FONT_BODY)
        self.link_entry.pack(fill="x", pady=(0, 10))
        cap_row = ctk.CTkFrame(content, fg_color="transparent")
        cap_row.pack(fill="x")
        self.caption_path = ctk.CTkEntry(cap_row, height=35, placeholder_text="Caption File (.txt)",
                                         fg_color=COLORS["bg_main"], border_color=COLORS["border"], corner_radius=8,
                                         font=FONT_BODY)
        self.caption_path.pack(side="left", fill="x", expand=True, padx=(0, 8))
        btn_browse = ctk.CTkButton(cap_row, text="📂", width=45, height=35, fg_color=COLORS["bg_lighter"],
                                   hover_color=COLORS["primary"], border_width=1, border_color=COLORS["border"],
                                   corner_radius=8, command=self.browse_caption)
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

        # Counters
        self.total_shares = 0
        self.error_count = 0
        self.total_attempts = 0
        self.job_list_global = []
        self.fast_mode_var = ctk.BooleanVar(value=True)
        self.history_file = "share_history.json"

        # Locks for thread-safe updates
        self.history_lock = threading.Lock()
        self.progress_lock = threading.Lock()
        self.stats_lock = threading.Lock()

        self.accounts_processed = 0
        self.total_accounts_to_process = 0
        self.share_history = self.load_share_history()

        self.layout_ui()
        self.load_settings()
        self.check_for_updates()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_share_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_share_history(self):
        with self.history_lock:
            try:
                with open(self.history_file, "w") as f:
                    json.dump(self.share_history, f, indent=2)
            except Exception as e:
                pass

    def get_account_id(self, cookie_str):
        for pair in cookie_str.split(";"):
            if "=" in pair:
                name, value = pair.strip().split("=", 1)
                if name == "c_user":
                    return value
        return hashlib.md5(cookie_str.encode()).hexdigest()

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
            except Exception as e:
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
                self.after(6000, self.check_for_updates)
        else:
            self.after(6000, self.check_for_updates)

    def on_tab_change(self):
        if self.tabview.get() == "   Saved Profiles   ":
            self.populate_saved_profiles()

    def layout_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], height=60, corner_radius=0, border_width=0)
        header.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(header, text=f"⚡ AUTOPOST V{__version__}", font=FONT_HEADER, text_color=COLORS["primary"]).pack(
            side="left", padx=20, pady=15)
        self.status_badge = ctk.CTkLabel(header, text="● IDLE", font=("Roboto", 13, "bold"),
                                         text_color=COLORS["text_sub"])
        self.status_badge.pack(side="right", padx=20)
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        main_content.grid_rowconfigure(0, weight=1)
        main_content.grid_columnconfigure(0, weight=1)
        self.tabview = ctk.CTkTabview(main_content, fg_color=COLORS["bg_main"], corner_radius=12,
                                      segmented_button_selected_color=COLORS["primary"],
                                      segmented_button_selected_hover_color="#2563EB",
                                      segmented_button_unselected_color=COLORS["bg_card"],
                                      segmented_button_unselected_hover_color=COLORS["bg_lighter"],
                                      command=self.on_tab_change)
        self.tabview.grid(row=0, column=0, sticky="nsew")
        self.tab_dash = self.tabview.add("   Dashboard   ")
        self.tab_logs = self.tabview.add("   System Logs   ")
        self.tab_saved = self.tabview.add("   Saved Profiles   ")
        self.setup_dashboard()
        self.setup_logs()
        self.setup_saved_profiles()

    def setup_dashboard(self):
        self.tab_dash.grid_columnconfigure(1, weight=1)
        self.tab_dash.grid_rowconfigure(0, weight=1)
        left_panel = ctk.CTkScrollableFrame(self.tab_dash, fg_color="transparent", width=350)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.overall_stats = StatsFrame(left_panel)
        self.overall_stats.pack(fill="x", pady=(0, 15))

        control_frame = ctk.CTkFrame(left_panel, fg_color=COLORS["bg_card"], corner_radius=15, border_width=1,
                                     border_color=COLORS["border"])
        control_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(control_frame, text="⚙️ ACTIONS", font=("Roboto", 12, "bold"),
                     text_color=COLORS["text_main"]).pack(anchor="w", padx=15, pady=(15, 10))

        lbl_cookies = ctk.CTkLabel(control_frame, text="Cookie File Path:", font=("Roboto", 11, "bold"),
                                   text_color=COLORS["text_sub"])
        lbl_cookies.pack(anchor="w", padx=15, pady=(5, 0))
        cookie_row = ctk.CTkFrame(control_frame, fg_color="transparent")
        cookie_row.pack(fill="x", padx=15, pady=(0, 15))
        self.cookie_entry = ctk.CTkEntry(cookie_row, height=35, placeholder_text="Path to cookies.txt", corner_radius=8)
        self.cookie_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.cookie_entry.insert(0, self.global_cookie_path)
        btn_browse = ctk.CTkButton(cookie_row, text="📂", width=45, height=35, fg_color=COLORS["bg_lighter"],
                                   hover_color=COLORS["primary"], border_width=1, border_color=COLORS["border"],
                                   corner_radius=8, command=self.browse_global_cookie)
        btn_browse.pack(side="right")

        self.fast_mode_switch = ctk.CTkSwitch(control_frame, text="⚡ Fast Mode",
                                              variable=self.fast_mode_var, font=("Roboto", 12, "bold"),
                                              text_color=COLORS["warning"])
        self.fast_mode_switch.pack(anchor="w", padx=15, pady=(5, 10))

        btn_grid = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_grid.pack(fill="x", padx=15, pady=5)
        self.start_btn = ctk.CTkButton(btn_grid, text="▶ START", height=45, fg_color=COLORS["success"],
                                       hover_color="#059669", font=("Roboto", 14, "bold"), corner_radius=8,
                                       command=self.start_threads)
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.stop_btn = ctk.CTkButton(btn_grid, text="⏹ STOP", height=45, fg_color=COLORS["danger"],
                                      hover_color="#DC2626", font=("Roboto", 14, "bold"), state="disabled",
                                      corner_radius=8,
                                      command=self.stop_automation)
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))

        lbl_delay = ctk.CTkLabel(control_frame, text="Pre/Post Action Delay (s)", font=("Roboto", 11, "bold"),
                                 text_color=COLORS["text_sub"])
        lbl_delay.pack(anchor="w", padx=15, pady=(10, 0))
        delay_row = ctk.CTkFrame(control_frame, fg_color="transparent")
        delay_row.pack(fill="x", padx=15, pady=(0, 15))
        self.dash_pre_delay = ctk.CTkEntry(delay_row, width=70, height=32, justify="center", corner_radius=8)
        self.dash_pre_delay.pack(side="left", padx=(0, 5))
        self.dash_pre_delay.insert(0, "10")
        ctk.CTkLabel(delay_row, text="/", font=("Roboto", 16, "bold"), text_color=COLORS["text_sub"]).pack(side="left")
        self.dash_post_delay = ctk.CTkEntry(delay_row, width=70, height=32, justify="center", corner_radius=8)
        self.dash_post_delay.pack(side="left", padx=(5, 0))
        self.dash_post_delay.insert(0, "10")

        ctk.CTkButton(control_frame, text="💾 Save Configuration", height=35, fg_color="transparent",
                      border_width=1, border_color=COLORS["primary"], text_color=COLORS["primary"], font=FONT_BODY,
                      corner_radius=8, hover_color=COLORS["bg_lighter"],
                      command=self.save_config).pack(fill="x", padx=15, pady=(5, 5))

        ctk.CTkButton(control_frame, text="🔄 Check for Updates", height=35, fg_color="transparent",
                      border_width=1, border_color=COLORS["warning"], text_color=COLORS["warning"], font=FONT_BODY,
                      corner_radius=8, hover_color=COLORS["bg_lighter"],
                      command=lambda: self.check_for_updates(manual=True)).pack(fill="x", padx=15, pady=(5, 5))

        ctk.CTkButton(control_frame, text="🗑 Clear Share History", height=35, fg_color="transparent",
                      border_width=1, border_color=COLORS["danger"], text_color=COLORS["danger"], font=FONT_BODY,
                      corner_radius=8, hover_color=COLORS["bg_lighter"],
                      command=self.clear_share_history).pack(fill="x", padx=15, pady=(5, 20))

        right_panel = ctk.CTkFrame(self.tab_dash, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew")
        header = ctk.CTkFrame(right_panel, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(header, text="📋 TASKS", font=FONT_SUBHEADER, text_color=COLORS["text_main"]).pack(side="left")
        ctk.CTkButton(header, text="+ Add Link", width=100, height=32, fg_color=COLORS["primary"],
                      font=("Roboto", 12, "bold"),
                      corner_radius=8, hover_color="#2563EB", command=self.add_pair).pack(side="right")
        self.pairs_scroll = ctk.CTkScrollableFrame(right_panel, fg_color="transparent")
        self.pairs_scroll.pack(fill="both", expand=True, padx=0, pady=5)
        self.add_pair()

    def clear_share_history(self):
        ans = messagebox.askyesno("Clear History",
                                  "Clear share history? This will allow processed accounts to share the same links again.")
        if ans:
            with self.history_lock:
                self.share_history = {}
                try:
                    if os.path.exists(self.history_file):
                        os.remove(self.history_file)
                except Exception as e:
                    pass
            messagebox.showinfo("Success", "Share history cleared successfully!")

    def setup_logs(self):
        self.tab_logs.grid_columnconfigure(0, weight=1)
        self.tab_logs.grid_rowconfigure(2, weight=1)
        top_bar = ctk.CTkFrame(self.tab_logs, fg_color="transparent", height=40)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 5))
        ctk.CTkLabel(top_bar, text="VIEWING LOGS:", font=FONT_SUBHEADER).pack(side="left", padx=(0, 10))
        self.log_shares_label = ctk.CTkLabel(top_bar, text="✅ SHARES: 0", font=("Roboto", 13, "bold"),
                                             text_color=COLORS["success"])
        self.log_shares_label.pack(side="left", padx=(0, 15))
        self.log_failed_label = ctk.CTkLabel(top_bar, text="⚠️ FAILED: 0", font=("Roboto", 13, "bold"),
                                             text_color=COLORS["danger"])
        self.log_failed_label.pack(side="left", padx=(0, 15))
        self.log_cookies_label = ctk.CTkLabel(top_bar, text="🍪 COOKIES: 0", font=("Roboto", 13, "bold"),
                                              text_color=COLORS["primary"])
        self.log_cookies_label.pack(side="left", padx=(0, 15))
        self.log_threads_label = ctk.CTkLabel(top_bar, text="💻 ACTIVE THREADS: 0", font=("Roboto", 13, "bold"),
                                              text_color=COLORS["warning"])
        self.log_threads_label.pack(side="left", padx=(0, 15))
        self.logs_stop_btn = ctk.CTkButton(top_bar, text="⏹ STOP", width=90, height=32, fg_color=COLORS["danger"],
                                           hover_color="#DC2626", state="disabled", corner_radius=8,
                                           command=self.stop_automation)
        self.logs_stop_btn.pack(side="right", padx=(0, 5))
        ctk.CTkButton(top_bar, text="🗑 Clear", width=90, height=32, fg_color="transparent", border_width=1,
                      border_color=COLORS["border"], hover_color=COLORS["bg_lighter"], corner_radius=8,
                      command=self.clear_logs).pack(side="right", padx=(0, 10))
        progress_frame = ctk.CTkFrame(self.tab_logs, fg_color="transparent")
        progress_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.progress_label = ctk.CTkLabel(progress_frame, text="Progress: 0 / 0 Accounts", font=("Roboto", 12, "bold"),
                                           text_color=COLORS["text_sub"])
        self.progress_label.pack(side="left", padx=(0, 15))
        self.progress_bar = ctk.CTkProgressBar(progress_frame, fg_color=COLORS["bg_card"],
                                               progress_color=COLORS["primary"], height=12)
        self.progress_bar.pack(side="left", fill="x", expand=True)
        self.progress_bar.set(0)
        logs_container = ctk.CTkFrame(self.tab_logs, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1,
                                      border_color=COLORS["border"])
        logs_container.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        logs_container.grid_columnconfigure(0, weight=1)
        logs_container.grid_rowconfigure(0, weight=1)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=COLORS["bg_card"], foreground=COLORS["text_main"],
                        fieldbackground=COLORS["bg_card"], borderwidth=0, rowheight=30, font=("Roboto", 11))
        style.map('Treeview', background=[('selected', COLORS["bg_lighter"])])
        style.configure("Treeview.Heading", background=COLORS["bg_main"], foreground=COLORS["text_sub"],
                        font=("Roboto", 11, "bold"), borderwidth=0, padding=(0, 8))
        tree_f1 = ctk.CTkFrame(logs_container, corner_radius=12, fg_color="transparent")
        tree_f1.pack(fill="both", expand=True, padx=2, pady=2)
        cols1 = ("Time", "Worker", "Link", "Caption", "Status")
        self.table_auto = ttk.Treeview(tree_f1, columns=cols1, show="headings", height=8)
        self.table_auto.heading("Time", text="TIME", anchor="center")
        self.table_auto.column("Time", width=100, anchor="center")
        self.table_auto.heading("Worker", text="WORKER", anchor="center")
        self.table_auto.column("Worker", width=100, anchor="center")
        self.table_auto.heading("Link", text="LINK", anchor="center")
        self.table_auto.column("Link", width=250, anchor="center")
        self.table_auto.heading("Caption", text="CAPTION", anchor="center")
        self.table_auto.column("Caption", width=250, anchor="center")
        self.table_auto.heading("Status", text="STATUS", anchor="center")
        self.table_auto.column("Status", width=300, anchor="center")
        sb1 = ctk.CTkScrollbar(tree_f1, command=self.table_auto.yview)
        self.table_auto.configure(yscrollcommand=sb1.set)
        sb1.pack(side="right", fill="y", pady=5)
        self.table_auto.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.table_auto.tag_configure("SUCCESS", foreground=COLORS["success"])
        self.table_auto.tag_configure("ERROR", foreground=COLORS["danger"])
        self.table_auto.tag_configure("WARN", foreground=COLORS["warning"])
        self.table_auto.bind("<Double-1>", self.on_log_double_click)

    def setup_saved_profiles(self):
        self.tab_saved.grid_columnconfigure(0, weight=1)
        self.tab_saved.grid_rowconfigure(1, weight=1)
        top_bar = ctk.CTkFrame(self.tab_saved, fg_color="transparent", height=40)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 5))
        ctk.CTkLabel(top_bar, text="📁 SAVED SESSIONS", font=FONT_SUBHEADER).pack(side="left", padx=(0, 10))

        # Total Saved Sessions Label
        self.lbl_total_saved = ctk.CTkLabel(top_bar, text="Total: 0", font=("Roboto", 13, "bold"),
                                            text_color=COLORS["success"])
        self.lbl_total_saved.pack(side="left", padx=(10, 0))

        ctk.CTkButton(top_bar, text="🔄 Refresh List", width=120, height=32, corner_radius=8,
                      command=self.populate_saved_profiles).pack(side="right", padx=(0, 5))

        ctk.CTkButton(top_bar, text="🗑 Delete All", width=100, height=32, fg_color=COLORS["danger"],
                      hover_color="#B91C1C", corner_radius=8,
                      command=self.delete_all_profiles).pack(side="right", padx=(0, 10))

        ctk.CTkButton(top_bar, text="📋 Copy All", width=100, height=32, fg_color=COLORS["success"],
                      hover_color="#059669", corner_radius=8,
                      command=self.copy_all_profiles).pack(side="right", padx=(0, 10))

        self.profiles_scroll = ctk.CTkScrollableFrame(self.tab_saved, fg_color=COLORS["bg_main"])
        self.profiles_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.populate_saved_profiles()

    def populate_saved_profiles(self):
        for widget in self.profiles_scroll.winfo_children():
            widget.destroy()
        profiles_dir = os.path.join(os.getcwd(), "profiles")

        count = 0
        if os.path.exists(profiles_dir):
            uids = [d for d in os.listdir(profiles_dir) if os.path.isdir(os.path.join(profiles_dir, d))]
            count = len(uids)
            if not uids:
                ctk.CTkLabel(self.profiles_scroll, text="No saved profiles or cookies yet.", font=FONT_BODY,
                             text_color=COLORS["text_sub"]).pack(pady=30)
            else:
                for i, uid in enumerate(uids):
                    self.create_profile_row(i + 1, uid)
        else:
            ctk.CTkLabel(self.profiles_scroll, text="No saved profiles or cookies yet.", font=FONT_BODY,
                         text_color=COLORS["text_sub"]).pack(pady=30)

        # Update Total Label
        if hasattr(self, 'lbl_total_saved'):
            self.lbl_total_saved.configure(text=f"Total: {count}")

    def create_profile_row(self, index, uid):
        row = ctk.CTkFrame(self.profiles_scroll, fg_color=COLORS["bg_card"], corner_radius=8, border_width=1,
                           border_color=COLORS["border"])
        row.pack(fill="x", pady=5, padx=5)
        lbl_idx = ctk.CTkLabel(row, text=f"{index}.", width=30, font=("Roboto", 13, "bold"),
                               text_color=COLORS["text_sub"])
        lbl_idx.pack(side="left", padx=(10, 5), pady=10)
        fb_link = f"https://www.facebook.com/{uid}"
        lbl_link = ctk.CTkLabel(row, text=fb_link, font=("Roboto", 13, "underline"), text_color=COLORS["primary"],
                                cursor="hand2")
        lbl_link.pack(side="left", padx=10, pady=10)
        lbl_link.bind("<Double-1>", lambda e, url=fb_link: webbrowser.open(url))
        ctk.CTkLabel(row, text="(Double-click to open)", font=("Roboto", 10, "italic"),
                     text_color=COLORS["text_sub"]).pack(side="left", padx=(0, 10))
        btn_copy = ctk.CTkButton(row, text="📋 Copy URL", width=90, height=28, fg_color=COLORS["bg_lighter"],
                                 hover_color=COLORS["primary"], corner_radius=6, text_color=COLORS["text_main"],
                                 command=lambda u=fb_link: self.copy_to_clipboard(u))
        btn_copy.pack(side="right", padx=(5, 10), pady=10)
        btn_del = ctk.CTkButton(row, text="🗑 Delete Data", width=90, height=28, fg_color="transparent", border_width=1,
                                border_color=COLORS["danger"],
                                text_color=COLORS["danger"], hover_color=COLORS["danger"], corner_radius=6,
                                command=lambda r=row, u=uid: self.delete_profile(r, u))
        btn_del.pack(side="right", padx=5, pady=10)

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

    def copy_all_profiles(self):
        profiles_dir = os.path.join(os.getcwd(), "profiles")
        if not os.path.exists(profiles_dir):
            messagebox.showinfo("Info", "No saved profiles to copy.")
            return
        uids = [d for d in os.listdir(profiles_dir) if os.path.isdir(os.path.join(profiles_dir, d))]
        if not uids:
            messagebox.showinfo("Info", "No saved profiles to copy.")
            return
        links = [f"https://www.facebook.com/{uid}" for uid in uids]
        all_links_str = "\n".join(links)
        self.clipboard_clear()
        self.clipboard_append(all_links_str)
        self.update()
        messagebox.showinfo("Copied", f"Copied {len(links)} links to clipboard!")

    def delete_profile(self, row_widget, uid):
        prof_path = os.path.join(os.getcwd(), "profiles", uid)
        try:
            if os.path.exists(prof_path):
                shutil.rmtree(prof_path)
            row_widget.destroy()
            self.overall_stats.update_cookies(max(0, int(self.overall_stats.card_cookies.value_var.get()) - 1))

            # Subtract 1 from the total label
            current_text = self.lbl_total_saved.cget("text")
            current_count = int(current_text.split(": ")[1])
            self.lbl_total_saved.configure(text=f"Total: {max(0, current_count - 1)}")

        except Exception as e:
            messagebox.showerror("Error", f"Cannot delete the profile folder:\n{e}")

    def delete_all_profiles(self):
        response = messagebox.askyesno("Delete All", "Are you sure you want to delete ALL saved profiles?")
        if response:
            profiles_dir = os.path.join(os.getcwd(), "profiles")
            if os.path.exists(profiles_dir):
                try:
                    shutil.rmtree(profiles_dir)
                    os.makedirs(profiles_dir, exist_ok=True)
                except Exception as e:
                    messagebox.showerror("Error", f"Error deleting some folders:\n{e}")
            self.populate_saved_profiles()
            self.overall_stats.update_cookies(0)

    def update_progress_ui(self, processed, total):
        if total > 0:
            val = processed / total
            self.progress_bar.set(val)
            self.progress_label.configure(text=f"Progress: {processed} / {total} Accounts")
        else:
            self.progress_bar.set(0)
            self.progress_label.configure(text="Progress: 0 / 0 Accounts")

    def log_row(self, worker_id, link, caption, status, level="INFO"):
        ts = datetime.now().strftime("%I:%M:%S %p")
        d_name = worker_id
        disp_link = (link[:40] + '...') if len(link) > 40 else link
        disp_cap = (caption[:40] + '...') if caption and len(caption) > 40 else caption
        if not disp_cap: disp_cap = "---"
        self.after(10, lambda: self._safe_insert(self.table_auto, (ts, d_name, disp_link, disp_cap, status), level,
                                                 full_link=link))

    def _safe_insert(self, tree, values, tag, full_link=""):
        try:
            tree.insert("", "end", text=full_link, values=values, tags=(tag,))
            children = tree.get_children()
            if len(children) > 100:
                tree.delete(children[0])
            tree.yview_moveto(1)
        except Exception as e:
            pass

    def clear_logs(self):
        for item in self.table_auto.get_children():
            self.table_auto.delete(item)

    def on_log_double_click(self, event):
        try:
            tree = event.widget
            item = tree.item(tree.identify_row(event.y))
            url = item.get('text', '')
            if not url:
                url = item['values'][2]
            if "http" in url:
                webbrowser.open(url)
        except Exception as e:
            pass

    def on_close(self):
        self.stop_automation()
        self.destroy()
        os._exit(0)

    def _count_and_update_cookies(self, file_path):
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    ac = [l.strip() for l in f if l.strip()]
                self.update_total_cookies_ui(len(ac))
            except Exception as e:
                self.update_total_cookies_ui(0)
        else:
            self.update_total_cookies_ui(0)

    def browse_global_cookie(self):
        f = filedialog.askopenfilename(filetypes=[("Txt", "*.txt")])
        if f:
            self.cookie_entry.delete(0, "end")
            self.cookie_entry.insert(0, f)
            self.global_cookie_path = f
            self._count_and_update_cookies(f)

    def load_settings(self):
        try:
            with open("pc_settings.json", "r") as f:
                d = json.load(f)
                self.global_cookie_path = d.get("global_cookie_path", "")
                self.fast_mode_var.set(d.get("fast_mode", True))
                self.after(500, lambda: self._set_vals(d))
        except Exception as e:
            pass

    def _set_vals(self, d):
        try:
            self.dash_pre_delay.delete(0, "end")
            self.dash_pre_delay.insert(0, d.get("dash_pre_delay", "10"))
            self.dash_post_delay.delete(0, "end")
            self.dash_post_delay.insert(0, d.get("dash_post_delay", "10"))
            cookie_path = d.get("global_cookie_path", "")
            if hasattr(self, 'cookie_entry'):
                self.cookie_entry.delete(0, "end")
                self.cookie_entry.insert(0, cookie_path)
            self._count_and_update_cookies(cookie_path)
        except Exception as e:
            pass

    def save_config(self):
        self.global_cookie_path = self.cookie_entry.get()
        self.saved_settings = {
            "global_cookie_path": self.global_cookie_path,
            "dash_pre_delay": self.dash_pre_delay.get(),
            "dash_post_delay": self.dash_post_delay.get(),
            "fast_mode": self.fast_mode_var.get()
        }
        with open("pc_settings.json", "w") as f:
            json.dump(self.saved_settings, f, indent=2)
        messagebox.showinfo("Saved", "Configuration updated.")

    def add_pair(self):
        pair_num = len(self.pair_widgets) + 1
        new_pair = PairFrame(self.pairs_scroll, pair_num, lambda: self.remove_pair(new_pair))
        new_pair.pack(fill="x", padx=5, pady=8)
        self.pair_widgets.append(new_pair)

    def remove_pair(self, frame):
        if len(self.pair_widgets) > 1:
            frame.destroy()
            self.pair_widgets.remove(frame)
            for i, f in enumerate(self.pair_widgets):
                f.header_label.configure(text=f"📍 LINK #{i + 1}")

    def parse_playwright_cookies(self, cookie_str):
        cookies = []
        expires_time = int(time.time()) + (365 * 24 * 60 * 60)
        for pair in cookie_str.split(";"):
            if "=" in pair:
                name, value = pair.strip().split("=", 1)
                cookies.append({
                    "name": name,
                    "value": value,
                    "domain": ".facebook.com",
                    "path": "/",
                    "expires": expires_time
                })
        return cookies

    def update_active_threads_ui(self, count):
        self.overall_stats.update_devices(count)
        if hasattr(self, 'log_threads_label'):
            self.log_threads_label.configure(text=f"💻 ACTIVE THREADS: {count}")

    def update_total_cookies_ui(self, count):
        self.overall_stats.update_cookies(count)
        if hasattr(self, 'log_cookies_label'):
            self.log_cookies_label.configure(text=f"🍪 COOKIES: {count}")

    def _mark_account_done(self):
        try:
            self.cookie_queue.task_done()
        except:
            pass
        with self.progress_lock:
            self.accounts_processed += 1
            c = self.accounts_processed
            t = self.total_accounts_to_process
        self.after(0, lambda: self.update_progress_ui(c, t))

    def run_pc_automation(self, worker_id):
        self.log_row(worker_id, "---", "---", "🚀 STARTED", "INFO")
        try:
            pre_wait = float(self.dash_pre_delay.get())
        except Exception as e:
            pre_wait = 5.0
        is_fast_mode = self.fast_mode_var.get()
        limit = 0
        processed = 0
        with sync_playwright() as p:
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
                acc_id = self.get_account_id(cookie_str)
                pending_jobs = []
                for link, cap_file in self.job_list_global:
                    if link in self.share_history and acc_id in self.share_history[link]:
                        self.log_row(worker_id, link, "---", f"SKIPPED (ALREADY SHARED) Acc {acc_idx}", "WARN")
                    else:
                        pending_jobs.append((link, cap_file))
                if not pending_jobs:
                    self._mark_account_done()
                    continue
                processed += 1
                context = None
                link_idx = 0
                total_links = len(pending_jobs)
                profile_dir = os.path.join(os.getcwd(), "profiles", acc_id)
                delete_profile_flag = False
                success_count = 0
                was_already_saved = False
                try:
                    while link_idx < total_links and self.is_running:
                        ln = link_idx + 1
                        link, cap_file = pending_jobs[link_idx]
                        sel_cap = "---"
                        try:
                            if context is None:
                                browser_args = [
                                    "--blink-settings=imagesEnabled=false,videoAutoplayEnabled=false",
                                    "--disable-notifications",
                                    "--no-sandbox",
                                    "--mute-audio",
                                    "--disable-popup-blocking",
                                    "--disable-infobars",
                                    "--disable-dev-shm-usage",
                                    "--disable-extensions",
                                    "--ignore-certificate-errors",
                                    "--renderer-process-limit=1",
                                    "--single-process",
                                    "--disable-background-networking",
                                    "--disable-sync",
                                    "--disable-translate",
                                    "--disk-cache-size=1",
                                    "--media-cache-size=1"
                                ]
                                os.makedirs(profile_dir, exist_ok=True)
                                context = p.chromium.launch_persistent_context(
                                    user_data_dir=profile_dir,
                                    headless=True,
                                    args=browser_args,
                                    viewport={'width': 360, 'height': 640},
                                    user_agent="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
                                )
                                self.active_browsers.append(context)
                                current_cookies = context.cookies()
                                is_logged_in = any(c.get('name') == 'c_user' for c in current_cookies)
                                was_already_saved = is_logged_in
                                if not is_logged_in:
                                    cookies = self.parse_playwright_cookies(cookie_str)
                                    if cookies:
                                        context.add_cookies(cookies)
                                    self.log_row(worker_id, "---", "---", f"INJECTED COOKIE (Acc {acc_idx})",
                                                 "INFO")
                                else:
                                    self.log_row(worker_id, "---", "---", f"USING SAVED SESSION (Acc {acc_idx})",
                                                 "SUCCESS")
                                page = context.pages[0] if context.pages else context.new_page()
                                client = context.new_cdp_session(page)
                                client.send("Network.setUserAgentOverride", {
                                    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                                    "platform": "Win32",
                                    "acceptLanguage": "en-US,en;q=0.9"
                                })
                                if is_fast_mode:
                                    blocked_urls = ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.css", "*.mp4", "*.avi",
                                                    "*.woff", "*.woff2", "*.ttf", "*.ico", "*favicon*"]
                                    client.send("Network.enable")
                                    client.send("Network.setBlockedURLs", {"urls": blocked_urls})
                            else:
                                page = context.pages[0] if context.pages else context.new_page()
                            page.goto(f"https://www.facebook.com/sharer/sharer.php?u={link}", timeout=90 * 1000)
                            dialog_xpath = "xpath=//*[@aria-label='Close composer dialog']"
                            dialog_locator = page.locator(dialog_xpath).first
                            try:
                                dialog_locator.wait_for(state="visible", timeout=30000)
                            except PlaywrightTimeoutError:
                                self.log_row(worker_id, link, "---", f"COOKIE EXPIRED Account {acc_idx}", "ERROR")
                                delete_profile_flag = True
                                with self.stats_lock:
                                    self.error_count += 1
                                    self.total_attempts += 1
                                self.update_stats()
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

                            # TINA-TRY I-CLICK ANG SHARE BUTTON
                            post_btn = page.locator(
                                "button[type='submit'], input[type='submit'], button[name='share'], button[value='Share'], [aria-label='Share'], button:has-text('Share'), button:has-text('Next')").first
                            try:
                                post_btn.wait_for(state="visible", timeout=15000)
                                post_btn.click()
                            except PlaywrightTimeoutError:
                                page.evaluate(
                                    "let btn = document.querySelector('button[type=\"submit\"], input[type=\"submit\"]'); if(btn) btn.click();")

                            # CHECK KUNG SUCCESS TALAGA ANG PAG-CLICK
                            is_dialog_closed = False
                            try:
                                dialog_locator.wait_for(state="hidden", timeout=20000)
                                is_dialog_closed = True
                            except PlaywrightTimeoutError:
                                is_dialog_closed = False

                            # KUNG SUMARA ANG DIALOG, SUCCESS YUN
                            if is_dialog_closed:
                                with self.history_lock:
                                    if link not in self.share_history:
                                        self.share_history[link] = []
                                    if acc_id not in self.share_history[link]:
                                        self.share_history[link].append(acc_id)
                                self.save_share_history()
                                self.log_row(worker_id, link, sel_cap, f"SUCCESS LINK {ln} Account {acc_idx}",
                                             "SUCCESS")

                                with self.stats_lock:
                                    success_count += 1
                                    self.total_shares += 1
                                    self.total_attempts += 1
                                self.update_stats()

                            # KUNG HINDI SUMARA ANG DIALOG, FAILED ANG SHARE
                            else:
                                self.log_row(worker_id, link, sel_cap, f"FAILED TO SHARE (Button/Block) Acc {acc_idx}",
                                             "ERROR")
                                with self.stats_lock:
                                    self.error_count += 1
                                    self.total_attempts += 1
                                self.update_stats()

                            time.sleep(2)
                        except Exception as e:
                            err_str = str(e).replace('\n', ' ')
                            traceback.print_exc()
                            self.log_row(worker_id, link, sel_cap, f"ERR: {err_str[:40]}", "ERROR")
                            with self.stats_lock:
                                self.error_count += 1
                                self.total_attempts += 1
                            self.update_stats()
                        link_idx += 1
                except Exception as e:
                    self.log_row(worker_id, "---", "---", f"FATAL WORKER ERR: {str(e)[:30]}", "ERROR")
                    traceback.print_exc()
                    with self.stats_lock:
                        self.error_count += 1
                        self.total_attempts += 1
                    self.update_stats()
                finally:
                    if context:
                        try:
                            if context in self.active_browsers:
                                self.active_browsers.remove(context)
                            context.close()
                        except:
                            pass

                    if delete_profile_flag or (not was_already_saved and success_count == 0):
                        for _ in range(3):
                            try:
                                time.sleep(1.5)
                                if os.path.exists(profile_dir):
                                    shutil.rmtree(profile_dir, ignore_errors=True)
                                if not os.path.exists(profile_dir):
                                    break
                            except Exception:
                                pass

                    self._mark_account_done()
        self.active_worker_count -= 1
        self.after(0, lambda: self.update_active_threads_ui(self.active_worker_count))

    def update_stats(self):
        self.after(0, lambda: self.overall_stats.update_stats(self.total_shares, self.error_count))
        if hasattr(self, 'log_shares_label'):
            self.after(0, lambda: self.log_shares_label.configure(text=f"✅ SHARES: {self.total_shares}"))
        if hasattr(self, 'log_failed_label'):
            self.after(0, lambda: self.log_failed_label.configure(text=f"⚠️ FAILED: {self.error_count}"))

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
                raise Exception("Cookie list is empty")
            self.update_total_cookies_ui(len(ac))
            self.total_accounts_to_process = len(ac)
            self.accounts_processed = 0
            self.update_progress_ui(0, self.total_accounts_to_process)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", "Cookie file empty/error!")
            return
        self._launch_workers(ac)

    def _launch_workers(self, ac):
        num_accounts = len(ac)
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
        self.tabview.set("   System Logs   ")
        self.worker_threads = []
        for i in range(num_threads):
            t = threading.Thread(target=self.run_pc_automation, args=(f"Worker-{i + 1}",))
            t.start()
            self.worker_threads.append(t)
            self.active_worker_count += 1
            self.update_active_threads_ui(self.active_worker_count)

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
            self.after(0, self.populate_saved_profiles)

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
                except Exception as e:
                    traceback.print_exc()
            self.active_browsers = []
            self.after(0, lambda: messagebox.showinfo("Stopped", "Automation Force Stopped."))
            self.after(0, self.populate_saved_profiles)

        threading.Thread(target=kill, daemon=True).start()


if __name__ == "__main__":
    app = FacebookAutomationGUI()
    app.mainloop()
