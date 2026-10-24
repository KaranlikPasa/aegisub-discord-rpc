"""
Aegisub Discord Rich Presence Application
Main entry point.
"""
import sys
import os
import customtkinter as ctk

from gui import AegisubRPCApp

def main():
    start_minimized = "--minimized" in sys.argv

    root = ctk.CTk()
    app = AegisubRPCApp(root, start_minimized=start_minimized)
    root.mainloop()

if __name__ == "__main__":
    main()
