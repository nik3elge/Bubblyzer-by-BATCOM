import sys
import os
import threading
import time

# Ensure UTF-8 output in Windows console to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from processor import BubbleProcessor
from server import start_server

def main():
    print("=" * 60)
    print("        Bubblyzer by BATCOM — Comic Bubble Detector")
    print("=" * 60)

    # Initialize ONNX Processor
    processor = BubbleProcessor()
    print("\n[1/2] Загрузка модели нейросети ONNX...")
    try:
        processor.load_model(lambda msg: print(f"  -> {msg}"))
    except Exception as e:
        print(f"\n[ERROR] Не удалось загрузить модель: {e}")
        try:
            input("Нажмите Enter для выхода...")
        except Exception:
            pass
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

    # If --cli flag or non-interactive environment, stay in console loop
    is_cli = "--cli" in sys.argv or not sys.stdin or not sys.stdin.isatty()
    
    if is_cli:
        print("  Режим: Консоль (нажмите Ctrl+C для остановки)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nСервер остановлен.")
            sys.exit(0)
    else:
        # Launch System Tray
        try:
            from tray import BubblyzerTray
            print("  Сервер запущен. Приложение свернуто в системный трей.")
            
            def on_quit():
                print("\nЗавершение работы Bubblyzer...")
                sys.exit(0)

            tray_app = BubblyzerTray(processor, on_quit)
            tray_app.run()
        except Exception as e:
            print(f"  Трей недоступен ({e}), работаем в консольном режиме.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nСервер остановлен.")
                sys.exit(0)

if __name__ == "__main__":
    main()
