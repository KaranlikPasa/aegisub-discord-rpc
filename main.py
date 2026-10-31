"""
Aegisub Discord Rich Presence Application
Main entry point.
"""
import sys
import os
import socket
import customtkinter as ctk

from gui import AegisubRPCApp

SINGLE_INSTANCE_PORT = 49581


def acquire_single_instance_lock():
    """Ensures only a single instance of the application runs at any time."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", SINGLE_INSTANCE_PORT))
        s.listen(0)
        return s
    except socket.error:
        return None


def main():
    lock = acquire_single_instance_lock()
    if lock is None:
        print("[Bilgi] Aegisub Discord RPC zaten arka planda çalışıyor.")
        sys.exit(0)

    start_minimized = "--minimized" in sys.argv

    root = ctk.CTk()
    app = AegisubRPCApp(root, start_minimized=start_minimized)
    try:
        root.mainloop()
    finally:
        try:
            lock.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
