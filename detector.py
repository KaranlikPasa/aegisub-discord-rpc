"""
Aegisub process and window title detector.
Strictly checks the actual aegisub.exe process to avoid false positives.
"""
import ctypes
import ctypes.wintypes
import re
import psutil

user32 = ctypes.windll.user32
WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

AEGISUB_EXES = {"aegisub.exe", "aegisub32.exe", "aegisub64.exe"}


def get_aegisub_process():
    """
    Returns psutil.Process of actual aegisub.exe if running, else None.
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
    """
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

    # Pick the title that looks like the main window (e.g. contains ' - Aegisub' or ends with 'Aegisub')
    for t in found_windows:
        if ' - Aegisub' in t or t.endswith('Aegisub'):
            return t

    return found_windows[0] if found_windows else None


def clean_project_name(raw_name):
    """
    Cleans release tags, crc32 hashes, resolutions, extensions from subtitle filename.
    Example: '[SubsPlease] Magical Explorer - 05 (1080p) [BE62F093].tr.ass' -> 'Magical Explorer - 05'
    """
    if not raw_name:
        return ""
    name = raw_name.strip()
    # Remove dirty marks (* or * )
    name = re.sub(r'^\*\s*', '', name)
    name = re.sub(r'\s*\*$', '', name)

    # Remove extensions like .tr.ass, .ass, .srt
    name = re.sub(r'\.([a-z]{2}\.)?(ass|ssa|srt|sub|txt)$', '', name, flags=re.IGNORECASE)
    # Remove release group tags like [SubsPlease], [Erai-raws], [HorribleSubs]
    name = re.sub(r'^\[[^\]]+\]\s*', '', name)
    # Remove CRC hashes like [BE62F093]
    name = re.sub(r'\[[A-Fa-f0-9]{8}\]', '', name)
    # Remove resolutions/sources like (1080p), [1080p], (BD), [Web]
    name = re.sub(r'[\(\[]\s*(1080p|720p|480p|2160p|4k|bd|web|bluray|hevc|x264|x265)\s*[\)\]]', '', name, flags=re.IGNORECASE)
    # Strip double spaces and surrounding dashes
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

    # Split before " - Aegisub"
    if ' - Aegisub' in title:
        title = title.split(' - Aegisub')[0].strip()

    # Strip directory path if present
    if '\\' in title:
        title = title.split('\\')[-1].strip()
    elif '/' in title:
        title = title.split('/')[-1].strip()

    # Check for empty / untitled project
    if title.lower() in ['adsız', 'adsiz', 'untitled', 'sans titre', 'sin título', '']:
        return "Yeni Proje"

    if clean:
        cleaned = clean_project_name(title)
        return cleaned if cleaned else title

    return title


def get_current_aegisub_state(clean_filename=True):
    """
    Returns (is_running, file_name, raw_title, pid).
    Guaranteed: If aegisub.exe is not running, is_running is ALWAYS False!
    """
    proc = get_aegisub_process()
    if not proc:
        return False, None, None, None

    pid = proc.pid
    raw_title = get_aegisub_window_title(pid)
    if raw_title:
        parsed = parse_aegisub_title(raw_title, clean=clean_filename)
        return True, parsed, raw_title, pid

    # Process exists but window title not yet available
    return True, "Yeni Proje", "Aegisub", pid
