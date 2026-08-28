import os
import sys
import webbrowser
import threading
from PIL import Image, ImageDraw

def create_tray_image(size=(32, 32)):
    """Generate a high-visibility, crisp speech bubble icon for Windows/macOS tray."""
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Outer circle/bubble (Bright cyan #00d2ff with crisp edge)
    # 32x32 coordinate space
    draw.ellipse([2, 2, 29, 23], fill=(0, 210, 255, 255), outline=(255, 255, 255, 255), width=1)
    
    # Bubble tail (down-left)
    tail_points = [(7, 21), (3, 29), (14, 21)]
    draw.polygon(tail_points, fill=(0, 210, 255, 255), outline=(255, 255, 255, 255))
    # Redraw inner triangle base to remove interior outline
    draw.polygon([(7, 20), (8, 22), (13, 20)], fill=(0, 210, 255, 255))

    # Inner 3 dark dots (high contrast)
    dot_color = (15, 23, 42, 255) # Deep navy
    draw.ellipse([8, 10, 11, 13], fill=dot_color)
    draw.ellipse([14, 10, 17, 13], fill=dot_color)
    draw.ellipse([20, 10, 23, 13], fill=dot_color)
    
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
            pystray.MenuItem("💬 Bubblyzer by BATCOM", self.open_web_dashboard, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(f"🟢 Сервер: http://127.0.0.1:5000", self.open_web_dashboard),
            pystray.MenuItem(f"⚡ Ускоритель: {accelerator}", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🌐 Открыть статус в браузере", self.open_web_dashboard),
            pystray.MenuItem("📁 Открыть папку программы", self.open_app_folder),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ Выход", self.quit_app)
        )

        image = create_tray_image((32, 32))
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
                    f"Сервер активен на http://127.0.0.1:5000\nУскоритель: {accelerator}",
                    "Bubblyzer by BATCOM"
                )
            except Exception:
                pass

        threading.Timer(0.8, notify_start).start()
        self.icon.run()
