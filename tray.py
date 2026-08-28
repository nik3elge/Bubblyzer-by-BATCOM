import os
import sys
import webbrowser
import threading
from PIL import Image, ImageDraw

def create_tray_image(size=(64, 64)):
    """Generate a clean vector-like speech bubble icon for the system tray."""
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Outer circle / bubble background (vibrant blue-indigo gradient look)
    draw.rounded_rectangle([4, 6, 60, 48], radius=16, fill=(56, 189, 248, 255))
    
    # Bubble tail
    tail_points = [(18, 46), (12, 60), (32, 46)]
    draw.polygon(tail_points, fill=(56, 189, 248, 255))
    
    # Inner 3 dots (chat bubble look)
    dot_color = (255, 255, 255, 255)
    draw.ellipse([18, 23, 26, 31], fill=dot_color)
    draw.ellipse([28, 23, 36, 31], fill=dot_color)
    draw.ellipse([38, 23, 46, 31], fill=dot_color)
    
    return image

class BubblyzerTray:
    def __init__(self, processor, on_quit_callback):
        self.processor = processor
        self.on_quit_callback = on_quit_callback
        self.icon = None

    def open_web_dashboard(self, icon=None, item=None):
        webbrowser.open("http://127.0.0.1:5000")

    def open_app_folder(self, icon=None, item=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if sys.platform == 'win32':
            os.startfile(base_dir)
        elif sys.platform == 'darwin':
            import subprocess
            subprocess.Popen(['open', base_dir])
        else:
            import subprocess
            subprocess.Popen(['xdg-open', base_dir])

    def quit_app(self, icon=None, item=None):
        if self.icon:
            self.icon.stop()
        if self.on_quit_callback:
            self.on_quit_callback()

    def run(self):
        import pystray
        
        accelerator = self.processor.active_provider if self.processor else "Auto"

        menu = pystray.Menu(
            pystray.MenuItem("💬 Bubblyzer by BATCOM", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🟢 Сервер: http://127.0.0.1:5000", self.open_web_dashboard),
            pystray.MenuItem(f"⚡ Ускоритель: {accelerator}", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🌐 Открыть статус в браузере", self.open_web_dashboard),
            pystray.MenuItem("📁 Открыть папку программы", self.open_app_folder),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ Выход", self.quit_app)
        )

        image = create_tray_image()
        self.icon = pystray.Icon(
            "Bubblyzer",
            image,
            "Bubblyzer by BATCOM",
            menu=menu
        )

        # Notify user that server started
        def notify_start():
            try:
                self.icon.notify(
                    f"Сервер активен (порт 5000).\nУскоритель: {accelerator}\nГотов к работе в Affinity!",
                    "Bubblyzer by BATCOM"
                )
            except Exception:
                pass

        threading.Timer(1.0, notify_start).start()
        self.icon.run()
