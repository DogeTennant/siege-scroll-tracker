"""
Build script for Siege Scroll Tracker
======================================
Creates a standalone SiegeTracker.exe

Requirements:
    pip install pyinstaller msgpack

Usage:
    python build.py

Output:
    dist/SiegeTracker/
        SiegeTracker.exe
        siege_addon.py     (copied automatically)
"""

import PyInstaller.__main__
import shutil
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(SCRIPT_DIR, "dist", "SiegeTracker")

print("Building SiegeTracker.exe ...")

ICO_PATH = os.path.join(SCRIPT_DIR, "siege_tracker.ico")

icon_args = ["--icon", ICO_PATH] if os.path.exists(ICO_PATH) else []

PyInstaller.__main__.run([
    "siege_gui.py",
    "--name=SiegeTracker",
    "--onedir",
    "--windowed",
    "--noconfirm",
    "--clean",
    "--hidden-import=msgpack",
    "--hidden-import=msgpack._cmsgpack",
    "--uac-admin",
] + icon_args)

# Copy siege_addon.py into dist folder (needed by mitmdump at runtime)
addon_src = os.path.join(SCRIPT_DIR, "siege_addon.py")
addon_dst = os.path.join(DIST_DIR, "siege_addon.py")
if os.path.exists(addon_src):
    shutil.copy2(addon_src, addon_dst)
    print(f"Copied siege_addon.py -> {addon_dst}")

print(f"\nBuild complete! Distribution folder: {DIST_DIR}")
print(f"Files to distribute:")
for f in os.listdir(DIST_DIR):
    size = os.path.getsize(os.path.join(DIST_DIR, f))
    print(f"  {f} ({size/1024:.0f} KB)")
