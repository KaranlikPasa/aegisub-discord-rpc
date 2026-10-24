"""
Modern GUI for Aegisub Discord Rich Presence.
Using CustomTkinter and pystray.
"""
import os
import sys
import time
import threading
import customtkinter as ctk
from PIL import Image
import pystray

from config import load_config, save_config, set_windows_startup
from detector import get_current_aegisub_state
from discord_rpc import DiscordRPCManager

def get_resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        res_path = os.path.join(base_path, relative_path)
        if os.path.exists(res_path):
            return res_path
        res_path2 = os.path.join(os.path.dirname(sys.executable), relative_path)
        if os.path.exists(res_path2):
            return res_path2
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

ICON_ICO = get_resource_path(os.path.join("assets", "aegisub_icon_128.ico"))
ICON_PNG = get_resource_path(os.path.join("assets", "aegisub_icon_128.png"))

PRESET_ACTIVITIES = [
    "Altyazı Çeviriyor",
    "Bölüm Çeviriyor",
    "Zamanlama (Timing) Yapıyor",
    "Typesetting (Dizgi) Yapıyor",
    "Karaoke / FX Yapıyor",
    "Altyazı Kontrolü (QC) Yapıyor",
    "Özel Metin..."
]


class AegisubRPCApp:
    def __init__(self, root, start_minimized=False):
        self.root = root
        self.config = load_config()
        self.rpc = DiscordRPCManager()
        self.is_running = True
        self.is_paused = False
        self.last_state = None
        self.last_title = None
        self.last_update_time = time.time()
        self.start_timestamp = int(time.time())
        self.tray_icon = None
        self.clean_filename = self.config.get("clean_filename", True)
        self.show_filename = self.config.get("show_filename", True)
        self.auto_close_with_aegisub = self.config.get("auto_close_with_aegisub", True)
        self.has_seen_aegisub = False

        self._setup_window()
        self._build_ui()
        self._setup_tray()

        # Start background monitor thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        # Start UI timer tick
        self._tick_timer()

        if start_minimized or self.config.get("start_minimized", False):
            self.root.after(100, self.minimize_to_tray)

    def _setup_window(self):
        self.root.title("Aegisub Discord Rich Presence")
        self.root.geometry("520x720")
        self.root.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        if os.path.exists(ICON_ICO):
            try:
                self.root.iconbitmap(ICON_ICO)
            except Exception:
                pass

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        # Main scrollable or static frame
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=12, fg_color="#1e1f22")
        self.main_frame.pack(fill="both", expand=True, padx=14, pady=14)

        # 1. Header Frame
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 10))

        if os.path.exists(ICON_PNG):
            pil_img = Image.open(ICON_PNG)
            self.header_img = ctk.CTkImage(pil_img, size=(46, 46))
            logo_label = ctk.CTkLabel(header, image=self.header_img, text="")
            logo_label.pack(side="left", padx=(0, 12))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", fill="both")

        lbl_app_title = ctk.CTkLabel(
            title_box,
            text="Aegisub Discord RPC",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#f2f3f5"
        )
        lbl_app_title.pack(anchor="w")

        lbl_app_sub = ctk.CTkLabel(
            title_box,
            text="Discord Profilinde Çeviri Durumu",
            font=ctk.CTkFont(size=12),
            text_color="#949ba4"
        )
        lbl_app_sub.pack(anchor="w")

        # Status badge in header
        self.badge_status = ctk.CTkLabel(
            header,
            text="● Kontrol Ediliyor",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2b2d31",
            text_color="#f0b232",
            corner_radius=8,
            padx=10,
            pady=4
        )
        self.badge_status.pack(side="right", pady=4)

        # 2. Discord Preview Card
        preview_container = ctk.CTkFrame(self.main_frame, fg_color="#2b2d31", corner_radius=10)
        preview_container.pack(fill="x", padx=16, pady=6)

        lbl_preview_title = ctk.CTkLabel(
            preview_container,
            text="DISCORD GÖRÜNÜMÜ",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#b5bac1"
        )
        lbl_preview_title.pack(anchor="w", padx=14, pady=(10, 4))

        preview_inner = ctk.CTkFrame(preview_container, fg_color="#1e1f22", corner_radius=8)
        preview_inner.pack(fill="x", padx=14, pady=(0, 12))

        # Preview Icon & Details
        if os.path.exists(ICON_PNG):
            self.prev_img = ctk.CTkImage(Image.open(ICON_PNG), size=(56, 56))
            prev_logo = ctk.CTkLabel(preview_inner, image=self.prev_img, text="")
            prev_logo.pack(side="left", padx=12, pady=12)

        prev_text_box = ctk.CTkFrame(preview_inner, fg_color="transparent")
        prev_text_box.pack(side="left", fill="both", expand=True, pady=10)

        self.prev_app_name = ctk.CTkLabel(
            prev_text_box,
            text="Aegisub",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff",
            anchor="w"
        )
        self.prev_app_name.pack(fill="x")

        self.prev_details = ctk.CTkLabel(
            prev_text_box,
            text="Altyazı Çeviriyor",
            font=ctk.CTkFont(size=13),
            text_color="#dbdee1",
            anchor="w"
        )
        self.prev_details.pack(fill="x")

        self.prev_state = ctk.CTkLabel(
            prev_text_box,
            text="Dosya bekleniyor...",
            font=ctk.CTkFont(size=13),
            text_color="#949ba4",
            anchor="w"
        )
        self.prev_state.pack(fill="x")

        self.prev_timer = ctk.CTkLabel(
            prev_text_box,
            text="00:00:00 geçti",
            font=ctk.CTkFont(size=11),
            text_color="#949ba4",
            anchor="w"
        )
        self.prev_timer.pack(fill="x")

        # 3. Settings Card
        settings_box = ctk.CTkFrame(self.main_frame, fg_color="#2b2d31", corner_radius=10)
        settings_box.pack(fill="both", expand=True, padx=16, pady=8)

        # Activity Type Dropdown
        lbl_act = ctk.CTkLabel(
            settings_box,
            text="Aktivite Durumu (Details):",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#dbdee1"
        )
        lbl_act.pack(anchor="w", padx=14, pady=(12, 4))

        current_preset = self.config.get("activity_type", "Altyazı Çeviriyor")
        if current_preset not in PRESET_ACTIVITIES:
            current_preset = "Özel Metin..."

        self.cb_activity = ctk.CTkComboBox(
            settings_box,
            values=PRESET_ACTIVITIES,
            command=self._on_activity_changed,
            height=34,
            corner_radius=6,
            fg_color="#1e1f22",
            border_color="#3b3e45",
            button_color="#5865f2"
        )
        self.cb_activity.set(current_preset)
        self.cb_activity.pack(fill="x", padx=14, pady=(0, 6))

        # Custom text entry
        self.entry_custom = ctk.CTkEntry(
            settings_box,
            placeholder_text="Özel çeviri durumu yazın (örn: Final Bölümü Çeviriyor...)",
            height=32,
            corner_radius=6,
            fg_color="#1e1f22",
            border_color="#3b3e45"
        )
        self.entry_custom.pack(fill="x", padx=14, pady=(0, 10))
        saved_custom = self.config.get("custom_details", "")
        if saved_custom and not saved_custom.startswith("Özel çeviri") and saved_custom != "Aegisub Discord Rich Presence":
            self.entry_custom.insert(0, saved_custom)
        self.entry_custom.bind("<KeyRelease>", lambda e: self._on_config_changed())

        if current_preset != "Özel Metin...":
            self.entry_custom.configure(state="disabled")

        # File display options
        lbl_file_opt = ctk.CTkLabel(
            settings_box,
            text="Dosya Adı & Bölüm Seçenekleri (State):",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#dbdee1"
        )
        lbl_file_opt.pack(anchor="w", padx=14, pady=(6, 4))

        self.var_show_filename = ctk.BooleanVar(value=self.config.get("show_filename", True))
        self.chk_show_filename = ctk.CTkCheckBox(
            settings_box,
            text="Açık olan dosya / bölüm adını Discord'da göster",
            variable=self.var_show_filename,
            command=self._on_config_changed,
            fg_color="#5865f2",
            hover_color="#4752c4"
        )
        self.chk_show_filename.pack(anchor="w", padx=14, pady=4)

        self.var_clean_filename = ctk.BooleanVar(value=self.config.get("clean_filename", True))
        self.chk_clean_filename = ctk.CTkCheckBox(
            settings_box,
            text="Dosya adını sadeleştir ([SubsPlease], [1080p], .ass etiketlerini gizle)",
            variable=self.var_clean_filename,
            command=self._on_config_changed,
            fg_color="#5865f2",
            hover_color="#4752c4"
        )
        self.chk_clean_filename.pack(anchor="w", padx=14, pady=4)

        # Custom state override
        self.entry_custom_state = ctk.CTkEntry(
            settings_box,
            placeholder_text="Sabit proje adı (Boş bırakırsanız dosya adı otomatik algılanır)",
            height=32,
            corner_radius=6,
            fg_color="#1e1f22",
            border_color="#3b3e45"
        )
        self.entry_custom_state.pack(fill="x", padx=14, pady=(6, 10))
        if self.config.get("custom_state"):
            self.entry_custom_state.insert(0, self.config.get("custom_state"))
        self.entry_custom_state.bind("<KeyRelease>", lambda e: self._on_config_changed())

        # System options
        lbl_sys = ctk.CTkLabel(
            settings_box,
            text="Sistem Seçenekleri:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#dbdee1"
        )
        lbl_sys.pack(anchor="w", padx=14, pady=(6, 4))

        self.var_startup = ctk.BooleanVar(value=self.config.get("start_with_windows", False))
        self.chk_startup = ctk.CTkCheckBox(
            settings_box,
            text="Windows başladığında otomatik çalıştır",
            variable=self.var_startup,
            command=self._on_startup_toggled,
            fg_color="#5865f2",
            hover_color="#4752c4"
        )
        self.chk_startup.pack(anchor="w", padx=14, pady=4)

        self.var_tray_on_close = ctk.BooleanVar(value=self.config.get("minimize_to_tray_on_close", True))
        self.chk_tray = ctk.CTkCheckBox(
            settings_box,
            text="Pencere kapatıldığında saatin yanına (arka plana) küçült",
            variable=self.var_tray_on_close,
            command=self._on_config_changed,
            fg_color="#5865f2",
            hover_color="#4752c4"
        )
        self.chk_tray.pack(anchor="w", padx=14, pady=4)

        self.var_auto_close = ctk.BooleanVar(value=self.config.get("auto_close_with_aegisub", True))
        self.chk_auto_close = ctk.CTkCheckBox(
            settings_box,
            text="Aegisub kapatıldığında bu uygulamayı da otomatik kapat",
            variable=self.var_auto_close,
            command=self._on_config_changed,
            fg_color="#5865f2",
            hover_color="#4752c4"
        )
        self.chk_auto_close.pack(anchor="w", padx=14, pady=(4, 12))

        # 4. Action Buttons
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(4, 6))

        self.btn_pause = ctk.CTkButton(
            btn_frame,
            text="Duraklat",
            command=self._toggle_pause,
            fg_color="#3b3e45",
            hover_color="#4e5058",
            height=36,
            corner_radius=6,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.btn_pause.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.btn_minimize = ctk.CTkButton(
            btn_frame,
            text="Tepsiye Küçült",
            command=self.minimize_to_tray,
            fg_color="#5865f2",
            hover_color="#4752c4",
            height=36,
            corner_radius=6,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.btn_minimize.pack(side="right", fill="x", expand=True, padx=(6, 0))

        # Full Quit Button in GUI
        self.btn_quit = ctk.CTkButton(
            self.main_frame,
            text="Uygulamayı Tamamen Kapat (Çıkış)",
            command=self.quit_app,
            fg_color="#da373c",
            hover_color="#a1282c",
            height=34,
            corner_radius=6,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.btn_quit.pack(fill="x", padx=16, pady=(0, 10))

    def _setup_tray(self):
        if not os.path.exists(ICON_PNG):
            return
        icon_img = Image.open(ICON_PNG)
        menu = pystray.Menu(
            pystray.MenuItem("Pencereyi Aç", self.restore_from_tray, default=True),
            pystray.MenuItem("Duraklat / Devam Et", self._toggle_pause),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Tamamen Kapat", self.quit_app)
        )
        self.tray_icon = pystray.Icon("AegisubRPC", icon_img, "Aegisub Discord RPC", menu=menu)
        self.tray_icon.run_detached()

    def minimize_to_tray(self):
        self.root.withdraw()

    def restore_from_tray(self, icon=None, item=None):
        self.root.after(0, self._show_window)

    def _show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _on_close(self):
        if self.var_tray_on_close.get():
            self.minimize_to_tray()
        else:
            self.quit_app()

    def quit_app(self, icon=None, item=None):
        self.is_running = False

        def _do_shutdown():
            # 1. Clear presence from Discord immediately
            try:
                if self.rpc:
                    self.rpc.clear()
                    self.rpc.close()
            except Exception:
                pass

            # 2. Hide tray icon immediately so it disappears from taskbar/tray
            try:
                if self.tray_icon:
                    self.tray_icon.visible = False
            except Exception:
                pass

            # 3. Destroy Tkinter if still alive
            try:
                self.root.quit()
                self.root.destroy()
            except Exception:
                pass

            # 4. Immediate and clean process exit
            os._exit(0)

        threading.Thread(target=_do_shutdown, daemon=True).start()

    def _on_activity_changed(self, choice):
        if choice == "Özel Metin...":
            self.entry_custom.configure(state="normal")
            self.entry_custom.focus()
        else:
            self.entry_custom.configure(state="disabled")
        self._on_config_changed()

    def _on_startup_toggled(self):
        enabled = self.var_startup.get()
        set_windows_startup(enabled)
        self._on_config_changed()

    def _on_config_changed(self):
        self.clean_filename = self.var_clean_filename.get()
        self.show_filename = self.var_show_filename.get()
        self.auto_close_with_aegisub = self.var_auto_close.get()
        self.config["activity_type"] = self.cb_activity.get()
        self.config["custom_details"] = self.entry_custom.get().strip()
        self.config["show_filename"] = self.show_filename
        self.config["clean_filename"] = self.clean_filename
        self.config["custom_state"] = self.entry_custom_state.get().strip()
        self.config["start_with_windows"] = self.var_startup.get()
        self.config["minimize_to_tray_on_close"] = self.var_tray_on_close.get()
        self.config["auto_close_with_aegisub"] = self.auto_close_with_aegisub
        save_config(self.config)
        self._update_presence_now()

    def _toggle_pause(self, icon=None, item=None):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.configure(text="Devam Et", fg_color="#248046", hover_color="#1a6334")
            self.badge_status.configure(text="● Duraklatıldı", text_color="#f0b232")
            self.rpc.clear()
        else:
            self.btn_pause.configure(text="Duraklat", fg_color="#3b3e45", hover_color="#4e5058")
            self._update_presence_now()

    def _get_current_details_text(self):
        preset = self.cb_activity.get()
        if preset == "Özel Metin...":
            custom = self.entry_custom.get().strip()
            return custom if custom else "Altyazı Çeviriyor"
        return preset

    def _get_current_state_text(self, file_name):
        custom_override = self.entry_custom_state.get().strip()
        if custom_override:
            return custom_override
        if not self.var_show_filename.get():
            return ""
        return file_name if file_name else "Yeni Proje"

    def _update_presence_now(self):
        if self.is_paused:
            return

        is_running, file_name, raw_title, pid = get_current_aegisub_state(clean_filename=self.clean_filename)
        details = self._get_current_details_text()
        state = self._get_current_state_text(file_name)

        # Update preview
        self.prev_details.configure(text=details)
        self.prev_state.configure(text=state if state else "Dosya gizlendi")

        if is_running:
            ok = self.rpc.update_presence(details=details, state=state)
            if ok:
                self.badge_status.configure(text="● Discord Aktif", text_color="#23a55a")
            else:
                self.badge_status.configure(text="● Discord Bekleniyor", text_color="#f23f43")
        else:
            self.rpc.clear()
            self.badge_status.configure(text="● Aegisub Bekleniyor", text_color="#949ba4")
            self.prev_state.configure(text="Aegisub açık değil")

    def _tick_timer(self):
        """Updates the preview elapsed timer every second."""
        if self.is_running:
            try:
                elapsed = int(time.time()) - self.start_timestamp
                hrs = elapsed // 3600
                mins = (elapsed % 3600) // 60
                secs = elapsed % 60
                self.prev_timer.configure(text=f"{hrs:02d}:{mins:02d}:{secs:02d} geçti")
                self.root.after(1000, self._tick_timer)
            except Exception:
                pass

    def _monitor_loop(self):
        """Background thread that checks Aegisub every 2 seconds."""
        while self.is_running:
            if not self.is_paused:
                try:
                    is_running, file_name, raw_title, pid = get_current_aegisub_state(clean_filename=self.clean_filename)
                    if is_running:
                        self.has_seen_aegisub = True
                        # If project changed, reset start timestamp
                        if file_name != self.last_state:
                            self.start_timestamp = int(time.time())
                            self.last_state = file_name

                        try:
                            self.root.after(0, self._update_presence_now)
                        except Exception:
                            pass
                    else:
                        if self.last_state is not None:
                            self.last_state = None
                            try:
                                self.root.after(0, self._update_presence_now)
                            except Exception:
                                pass

                            # If Aegisub was running and is now closed, auto-close if enabled
                            if self.has_seen_aegisub and self.auto_close_with_aegisub:
                                time.sleep(0.5)
                                self.quit_app()
                                break
                except Exception:
                    pass

            time.sleep(2.0)
