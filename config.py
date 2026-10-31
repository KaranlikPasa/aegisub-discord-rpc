"""
Configuration manager for Aegisub Discord Rich Presence.
Handles loading, saving in %APPDATA% (Windows) or ~/.config (Linux),
and startup shortcut / autostart management.
"""
import json
import os
import sys

def get_appdata_dir():
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        cfg_dir = os.path.join(base, "AegisubDiscordRPC")
    else:
        base = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        cfg_dir = os.path.join(base, "aegisub-discord-rpc")
    os.makedirs(cfg_dir, exist_ok=True)
    return cfg_dir

CONFIG_FILE = os.path.join(get_appdata_dir(), "config.json")

DEFAULT_CONFIG = {
    "activity_type": "Altyazı Çeviriyor",
    "custom_details": "",
    "show_filename": True,
    "clean_filename": True,
    "custom_state": "",
    "large_image_text": "Aegisub Subtitle Editor",
    "start_with_windows": False,
    "minimize_to_tray_on_close": True,
    "auto_close_with_aegisub": True,
    "start_minimized": False
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(data)
                return config
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Config save error: {e}")
        return False


def get_startup_shortcut_path():
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            startup_dir = os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs\Startup")
            return os.path.join(startup_dir, "AegisubDiscordRPC.lnk")
    return None


def set_windows_startup(enable=True):
    """Creates or removes Windows Startup shortcut or Linux autostart desktop entry."""
    if sys.platform != "win32":
        autostart_dir = os.path.expanduser("~/.config/autostart")
        desktop_file = os.path.join(autostart_dir, "aegisub-discord-rpc.desktop")
        if not enable:
            if os.path.exists(desktop_file):
                try:
                    os.remove(desktop_file)
                except Exception:
                    pass
            return True
        try:
            os.makedirs(autostart_dir, exist_ok=True)
            local_bin = os.path.expanduser("~/.local/bin/aegisub-discord-rpc")
            exec_bin = local_bin if os.path.exists(local_bin) else "/opt/aegisub-discord-rpc/aegisub-discord-rpc"
            content = f"""[Desktop Entry]
Type=Application
Name=Aegisub Discord RPC
Exec={exec_bin} --minimized
Icon=aegisub-discord-rpc
Comment=Discord Rich Presence for Aegisub Subtitle Editor
Terminal=false
Categories=Utility;
X-GNOME-Autostart-enabled=true
"""
            with open(desktop_file, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Failed to set Linux autostart: {e}")
            return False

    shortcut_path = get_startup_shortcut_path()
    if not shortcut_path:
        return False

    if not enable:
        if os.path.exists(shortcut_path):
            try:
                os.remove(shortcut_path)
            except Exception:
                pass
        return True

    try:
        import subprocess
        script_dir = os.path.dirname(os.path.abspath(__file__))
        target_exe = os.path.join(script_dir, "dist", "AegisubDiscordRPC", "AegisubDiscordRPC.exe")
        target_vbs = os.path.join(script_dir, "run_silently.vbs")
        icon_path = os.path.join(script_dir, "assets", "aegisub_icon_128.ico")

        if os.path.exists(target_exe):
            target = target_exe
            args = "--minimized"
            icon = target_exe
            work_dir = os.path.dirname(target_exe)
        else:
            target = "wscript.exe"
            args = f'"{target_vbs}" --minimized'
            icon = icon_path
            work_dir = script_dir

        ps_cmd = f"""
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
        $Shortcut.TargetPath = '{target}'
        $Shortcut.Arguments = '{args}'
        $Shortcut.WorkingDirectory = '{work_dir}'
        $Shortcut.Description = 'Aegisub Discord Rich Presence'
        $Shortcut.IconLocation = '{icon}'
        $Shortcut.Save()
        """
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True, creationflags=0x08000000)
        return True
    except Exception as e:
        print(f"Failed to set startup shortcut: {e}")
        return False
