"""
Discord Rich Presence Manager.
Handles connecting, updating presence, and reconnecting to Discord.
"""
import time
import threading
import pypresence

CLIENT_ID = "592657785368477728"  # Verified Aegisub Application ID


class DiscordRPCManager:
    def __init__(self, client_id=CLIENT_ID):
        self.client_id = client_id
        self.rpc = None
        self.is_connected = False
        self._lock = threading.Lock()
        self.current_presence = {}
        self.start_time = None
        self.last_project = None
        self.last_connect_attempt = 0.0
        self.last_update_time = 0.0

    def connect(self):
        """Attempts to connect to Discord IPC with rate limit cooldown."""
        now = time.time()
        # Cooldown: Don't hammer connect attempts faster than once every 5 seconds
        if now - self.last_connect_attempt < 5.0:
            return False

        with self._lock:
            if self.is_connected and self.rpc:
                return True
            self.last_connect_attempt = now
            try:
                self.rpc = pypresence.Presence(self.client_id)
                self.rpc.connect()
                self.is_connected = True
                return True
            except Exception:
                self.rpc = None
                self.is_connected = False
                return False

    def close(self):
        """Closes Discord connection."""
        acquired = self._lock.acquire(timeout=1.0)
        try:
            if self.rpc:
                try:
                    self.rpc.close()
                except Exception:
                    pass
            self.rpc = None
            self.is_connected = False
            self.current_presence = {}
        finally:
            if acquired:
                self._lock.release()

    def clear(self):
        """Clears current Discord presence without disconnecting."""
        acquired = self._lock.acquire(timeout=1.0)
        try:
            if self.is_connected and self.rpc:
                try:
                    self.rpc.clear()
                except Exception:
                    self.is_connected = False
                    self.rpc = None
            self.current_presence = {}
        finally:
            if acquired:
                self._lock.release()

    def update_presence(self, details="Altyazı Çeviriyor", state="", large_text="Aegisub Subtitle Editor", reset_timer_on_project_change=True, force=False):
        """
        Updates Discord Rich Presence.
        Auto-connects if not yet connected.
        Skips redundant updates to prevent rate limiting and flickering drops.
        """
        # Ensure connection
        if not self.is_connected or not self.rpc:
            if not self.connect():
                return False

        # Manage start timer
        if self.start_time is None or (reset_timer_on_project_change and state != self.last_project):
            self.start_time = int(time.time())
            self.last_project = state

        kwargs = {
            "large_image": "aegisub",
            "large_text": large_text if large_text else "Aegisub",
            "start": self.start_time
        }

        if details:
            kwargs["details"] = details[:128]
        if state:
            kwargs["state"] = state[:128]

        # Prevent redundant update calls (Discord already displays this presence)
        if not force and self.current_presence == kwargs and self.is_connected:
            return True

        now = time.time()
        # Enforce minimum 1.5 seconds between actual Discord IPC network calls
        if not force and (now - self.last_update_time < 1.5):
            return True

        with self._lock:
            try:
                self.rpc.update(**kwargs)
                self.current_presence = kwargs
                self.last_update_time = now
                return True
            except Exception:
                # Connection dropped
                self.is_connected = False
                self.rpc = None
                self.current_presence = {}
                return False
