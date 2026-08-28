import sys
import os
import threading
import time
import traceback

def log_error(msg):
    try:
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bubblyzer_error.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

# Ensure UTF-8 output in Windows console
if sys.platform == "win32":
    try:
        if sys.stdout: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if sys.stderr: sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from processor import BubbleProcessor
from server import start_server
from version import __version__, __app_name__, __author__

def main():
    log_error(f"{__app_name__} v{__version__} main() starting...")
    print("=" * 60)
    print(f"        {__app_name__} v{__version__} by {__author__} — Comic Bubble Detector")
    print("=" * 60)

    # Initialize ONNX Processor
    processor = BubbleProcessor()
    print("\n[1/2] Загрузка модели нейросети ONNX...")
    try:
        processor.load_model(lambda msg: print(f"  -> {msg}"))
        log_error(f"Model loaded: {processor.active_provider}")
    except Exception as e:
        err = f"Failed to load model: {e}\n{traceback.format_exc()}"
        log_error(err)
        print(f"\n[ERROR] {err}")
        sys.exit(1)

    port = 5000
    print(f"\n[2/2] Запуск API сервера на http://127.0.0.1:{port}...")
    print(f"  -> Активный ускоритель: {processor.active_provider}")
    print("=" * 60)

    # Start Flask server in background thread
    server_thread = threading.Thread(
        target=start_server,
        args=(processor, port),
        daemon=True
    )
    server_thread.start()
    log_error("Flask server thread started.")

    is_cli = "--cli" in sys.argv
    
    if is_cli:
        log_error("Running in explicit CLI mode.")
        print("  Режим: Консоль (нажмите Ctrl+C для остановки)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nСервер остановлен.")
            sys.exit(0)
    else:
        log_error("Attempting to initialize BubblyzerTray...")
        try:
            from tray import BubblyzerTray
            
            def on_quit():
                log_error("Tray quit requested.")
                os._exit(0)

            tray_app = BubblyzerTray(processor, on_quit)
            log_error("Calling tray_app.run()...")
            tray_app.run()
        except Exception as e:
            err = f"Tray failed: {e}\n{traceback.format_exc()}"
            log_error(err)
            print(f"  Трей недоступен ({e}), работаем в консольном режиме.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nСервер остановлен.")
                sys.exit(0)

if __name__ == "__main__":
    main()
