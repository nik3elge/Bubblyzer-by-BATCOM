import subprocess
import time
import urllib.request
import urllib.parse
import json
import os
import sys
import numpy as np
import cv2

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.version import DEFAULT_PORT, DEFAULT_SERVER_URL

def create_test_comic_page(filename="test_comic_page.png"):
    img = np.full((1200, 800, 3), 255, dtype=np.uint8)
    cv2.rectangle(img, (50, 50), (750, 550), (0, 0, 0), 4)
    cv2.rectangle(img, (50, 600), (750, 1150), (0, 0, 0), 4)

    # Panel 1: Bubble 1
    cv2.ellipse(img, (300, 200), (140, 70), 0, 0, 360, (0, 0, 0), 3)
    cv2.putText(img, "WHERE IS THE BATMAN?", (190, 205), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    # Panel 1: Bubble 2
    cv2.ellipse(img, (550, 350), (120, 60), 0, 0, 360, (0, 0, 0), 3)
    cv2.putText(img, "HE IS BEHIND YOU!", (460, 355), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    # Panel 2: Bubble 3
    cv2.ellipse(img, (400, 800), (180, 80), 0, 0, 360, (0, 0, 0), 3)
    cv2.putText(img, "BUBBLYZER BY BATCOM", (260, 805), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    abs_path = os.path.abspath(filename)
    cv2.imwrite(abs_path, img)
    return abs_path

def test_target(cmd_args, label):
    print(f"\n=======================================================")
    print(f"   TESTING: {label}")
    print(f"   Args: {cmd_args}")
    print(f"=======================================================")

    test_image = create_test_comic_page()
    
    # Launch process
    proc = subprocess.Popen(cmd_args, cwd=ROOT_DIR)
    
    try:
        # 1. Wait for server
        server_ready = False
        status_data = None
        for i in range(20):
            try:
                with urllib.request.urlopen(f"{DEFAULT_SERVER_URL}/status", timeout=1) as resp:
                    if resp.status == 200:
                        status_data = json.loads(resp.read().decode('utf-8'))
                        server_ready = True
                        break
            except Exception:
                time.sleep(1)

        if not server_ready:
            print(f"[FAIL] Server failed to start for {label}")
            return False

        print(f"  [+] Status endpoint OK: {status_data}")

        # 2. Test HTML Dashboard
        with urllib.request.urlopen(f"{DEFAULT_SERVER_URL}/") as resp:
            html = resp.read().decode('utf-8')
            assert "Bubblyzer" in html
            print("  [+] HTML Dashboard OK (HTTP 200)")

        # 3. Test Config
        url = f"{DEFAULT_SERVER_URL}/config?save=1&confidence=42"
        with urllib.request.urlopen(url) as resp:
            cfg = json.loads(resp.read().decode('utf-8'))
            assert cfg.get("confidence") == 42
            print(f"  [+] Config update OK: confidence={cfg.get('confidence')}")

        # 4. Test Detection
        detect_url = f"{DEFAULT_SERVER_URL}/detect?image_path={urllib.parse.quote(test_image)}&cleanup=false&confidence=0.15"
        with urllib.request.urlopen(detect_url) as resp:
            results = json.loads(resp.read().decode('utf-8'))
            print(f"  [+] Detection OK! Found {len(results)} speech bubbles:")
            for b in results:
                print(f"      - {b['class']}: {b['bbox']} (conf: {b['confidence']})")
            assert len(results) >= 2

        print(f"==> RESULT: {label} PASSED 100%!")
        return True

    finally:
        # Clean termination
        try:
            subprocess.run(f"taskkill /F /T /PID {proc.pid}", shell=True, capture_output=True)
        except Exception:
            pass
        if os.path.exists(test_image):
            try: os.remove(test_image)
            except Exception: pass

if __name__ == "__main__":
    # Test 1: Python Source
    main_py = os.path.join(ROOT_DIR, "src", "main.py")
    ok1 = test_target([sys.executable, main_py, "--cli"], "Python Source Engine")

    # Test 2: Standalone .exe
    exe_path = os.path.join(ROOT_DIR, "dist", "Bubblyzer.exe")
    ok2 = False
    if os.path.exists(exe_path):
        ok2 = test_target([exe_path], "Compiled Standalone Bubblyzer.exe")

    if ok1 and ok2:
        print(">>> ALL TESTS PASSED: SOURCE & STANDALONE EXE ARE 100% OPERATIONAL! <<<")
        sys.exit(0)
    else:
        sys.exit(1)
