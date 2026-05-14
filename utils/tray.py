import os
import sys
import subprocess
import time
from pathlib import Path

# Required: pip install pystray Pillow
try:
    from pystray import Icon, Menu, MenuItem
    from PIL import Image, ImageDraw
except ImportError:
    print("⚠️ Tray icon requires pystray and Pillow. Install them: pip install pystray Pillow")
    sys.exit(1)

ROOT_DIR = Path(__file__).parent.parent
DASHBOARD_PATH = ROOT_DIR / "utils" / "dashboard.py"
LAUNCHER_PATH = ROOT_DIR / "vibe_launcher.py"

def create_image():
    # Generate a simple brain icon
    width, height = 64, 64
    image = Image.new('RGB', (width, height), color=(15, 23, 42))
    dc = ImageDraw.Draw(image)
    dc.ellipse([10, 10, 54, 54], fill=(56, 189, 248)) # Blue brain base
    dc.text((20, 20), "VIBE", fill=(255, 255, 255))
    return image

def launch_launcher():
    subprocess.Popen([sys.executable, str(LAUNCHER_PATH)], creationflags=subprocess.CREATE_NEW_CONSOLE)

def launch_dashboard():
    subprocess.Popen([sys.executable, str(DASHBOARD_PATH)])

def on_quit(icon, item):
    icon.stop()

def setup_tray():
    menu = Menu(
        MenuItem("🚀 Launch Vibe Coder", launch_launcher),
        MenuItem("📊 Open Dashboard", launch_dashboard),
        MenuItem("❌ Exit", on_quit)
    )
    
    icon = Icon("VibeCoder", create_image(), "Vibe Coder Pro", menu)
    print("🧠 Vibe Coder Tray Icon Active.")
    icon.run()

if __name__ == "__main__":
    setup_tray()
