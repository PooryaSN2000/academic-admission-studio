#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Academic Admission Studio - Universal Runner
One-Click Launch for All Operating Systems
"""

import os
import sys
import json
import subprocess
import webbrowser
import time
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_DIR = os.path.join(BASE_DIR, "core")
sys.path.insert(0, CORE_DIR)

# Load configuration if available
config_path = os.path.join(BASE_DIR, "config.json")
config = {
    "lab_name": "Academic Admission Studio",
    "supervisor_name": "Faculty Supervisor",
    "port": 5050
}
if os.path.exists(config_path):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config.update(json.load(f))
    except Exception:
        pass

# Ensure requirements installed
try:
    from app import app
except ImportError:
    print("📦 Installing dependencies from requirements.txt...")
    req_file = os.path.join(BASE_DIR, "requirements.txt")
    if os.path.exists(req_file):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file, "--quiet"])
    else:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "openpyxl", "--quiet"])
    from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", config.get("port", 5050)))
    url = f"http://127.0.0.1:{port}"
    print("==============================================================")
    print(f"  🏛️ {config.get('lab_name', 'Academic Admission Studio')}")
    print(f"  Supervisor: {config.get('supervisor_name', 'Supervisor')}")
    print(f"  👉 Dashboard URL: {url}")
    print("==============================================================")
    print("📌 Press Ctrl + C to stop the server.\n")

    def auto_open():
        time.sleep(1.2)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    threading.Thread(target=auto_open, daemon=True).start()
    app.run(host="0.0.0.0", port=port, debug=False)
