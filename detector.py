"""
Aegisub process and window title detector.
Strictly checks the actual aegisub process to avoid false positives.
Cross-platform support: Windows & Linux (Arch Linux, Ubuntu, etc.)
"""
import os
import sys
import re
import psutil

if sys.platform == "win32":
    import ctypes
    import ctypes.wintypes
    user32 = ctypes.windll.user32
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
else:
    user32 = None
    WNDENUMPROC = None

AEGISUB_EXES = {"aegisub", "aegisub.exe", "aegisub32.exe", "aegisub64.exe", "aegisub-cli"}


def get_aegisub_process():
    """
    Returns psutil.Process of actual aegisub process if running, else None.
    Strictly checks process name to avoid matching other apps.
    """
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            name = proc.info.get('name')
            if name and name.lower() in AEGISUB_EXES:
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None


def get_aegisub_window_title(target_pid):
    """
    Finds the main window title for the specific aegisub process PID.
    Supports Windows (Win32 API) and Linux (xdotool, wmctrl, and open files inspection).
    """
    if sys.platform == "win32" and user32:
        found_windows = []

        def enum_cb(hwnd, lparam):
            if user32.IsWindowVisible(hwnd):
                pid = ctypes.wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                if pid.value == target_pid:
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buff = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buff, length + 1)
                        title = buff.value.strip()
                        if title and not title.startswith("GDI+") and not title.startswith("MSCTFIME"):
                            found_windows.append(title)
            return True

        cb = WNDENUMPROC(enum_cb)
        user32.EnumWindows(cb, 0)

        # Fallback to default desktop if running inside another desktop station
        if not found_windows:
            h_desk = user32.OpenDesktopW('default', 0, False, 0x0100)
            if h_desk:
                user32.EnumDesktopWindows(h_desk, cb, 0)
                user32.CloseDesktop(h_desk)

        # Pick the title that looks like the main window
        for t in found_windows:
            if ' - Aegisub' in t or t.endswith('Aegisub'):
                return t

        return found_windows[0] if found_windows else None

    # Linux implementation
    title = None
    try:
        import subprocess
        res = subprocess.run(["xdotool", "search", "--pid", str(target_pid), "getwindowname"],
                             capture_output=True, text=True, timeout=1)
        lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
        for l in lines:
            if " - Aegisub" in l or l.endswith("Aegisub"):
                title = l
                break
        if not title and lines:
            title = lines[0]
    except Exception:
        pass

    if not title:
        try:
            import subprocess
            res = subprocess.run(["wmctrl", "-lp"], capture_output=True, text=True, timeout=1)
            for line in res.stdout.splitlines():
                parts = line.split(None, 4)
                if len(parts) >= 5 and parts[2] == str(target_pid):
                    candidate = parts[4].strip()
                    if " - Aegisub" in candidate or candidate.endswith("Aegisub"):
                        title = candidate
                        break
        except Exception:
            pass

    # Fallback: inspect open subtitle files of the process
    if not title:
        try:
            proc = psutil.Process(target_pid)
            for f in proc.open_files():
                if f.path.lower().endswith(('.ass', '.ssa', '.srt', '.sub')):
                    base = os.path.basename(f.path)
                    title = f"{base} - Aegisub"
                    break
        except Exception:
            pass

    return title


def clean_project_name(raw_name):
    """
    Cleans release tags, crc32 hashes, resolutions, extensions from subtitle filename.
    Example: '[SubsPlease] Magical Explorer - 05 (1080p) [BE62F093].tr.ass' -> 'Magical Explorer - 05'
    """
    if not raw_name:
        return ""
    name = raw_name.strip()
    name = re.sub(r'^\*\s*', '', name)
    name = re.sub(r'\s*\*$', '', name)

    name = re.sub(r'\.([a-z]{2}\.)?(ass|ssa|srt|sub|txt)$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'^\[[^\]]+\]\s*', '', name)
    name = re.sub(r'\[[A-Fa-f0-9]{8}\]', '', name)
    name = re.sub(r'[\(\[]\s*(1080p|720p|480p|2160p|4k|bd|web|bluray|hevc|x264|x265)\s*[\)\]]', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+', ' ', name).strip(' -_')
    return name


def parse_aegisub_title(raw_title, clean=True):
    """
    Parses the Aegisub window title to extract the file/project name.
    """
    if not raw_title:
        return "Boş Proje"

    title = raw_title.strip()
    title = re.sub(r'^\*\s*', '', title)

    if ' - Aegisub' in title:
        title = title.split(' - Aegisub')[0].strip()

    if '\\' in title:
        title = title.split('\\')[-1].strip()
    elif '/' in title:
        title = title.split('/')[-1].strip()

    if title.lower() in ['adsız', 'adsiz', 'untitled', 'sans titre', 'sin título', '']:
        return "Yeni Proje"

    if clean:
        cleaned = clean_project_name(title)
        return cleaned if cleaned else title

    return title


def get_current_aegisub_state(clean_filename=True):
    """
    Returns (is_running, file_name, raw_title, pid).
    Guaranteed: If aegisub is not running, is_running is ALWAYS False!
    """
    proc = get_aegisub_process()
    if not proc:
        return False, None, None, None

    pid = proc.pid
    raw_title = get_aegisub_window_title(pid)
    if raw_title:
        parsed = parse_aegisub_title(raw_title, clean=clean_filename)
        return True, parsed, raw_title, pid

    return True, "Yeni Proje", "Aegisub", pid
