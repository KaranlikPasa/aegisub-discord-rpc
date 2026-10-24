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

    def connect(self):
        """Attempts to connect to Discord IPC."""
        with self._lock:
            if self.is_connected and self.rpc:
                return True
            try:
                self.rpc = pypresence.Presence(self.client_id)
                self.rpc.connect()
                self.is_connected = True
                return True
            except Exception as e:
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
        finally:
            if acquired:
                self._lock.release()

    def update_presence(self, details="Altyazı Çeviriyor", state="", large_text="Aegisub Subtitle Editor", reset_timer_on_project_change=True):
        """
        Updates Discord Rich Presence.
        Auto-connects if not yet connected.
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

        with self._lock:
            try:
                self.rpc.update(**kwargs)
                self.current_presence = kwargs
                return True
            except Exception as e:
                # Connection dropped
                self.is_connected = False
                self.rpc = None
                return False
