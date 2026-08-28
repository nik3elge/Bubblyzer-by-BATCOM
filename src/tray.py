import os
import sys
import webbrowser
import threading
from PIL import Image, ImageDraw

def get_tray_image(size=(32, 32)):
    """Load application icon from file or generate fallback."""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_dir = getattr(sys, '_MEIPASS', root_dir)
    
    search_dirs = [
        os.path.join(base_dir, "assets"),
        base_dir,
        os.path.join(root_dir, "assets"),
        os.path.join(os.getcwd(), "assets"),
        os.getcwd()
    ]
    
    for sdir in search_dirs:
        for filename in ['tray_icon.png', 'app_icon.png', 'app_icon.ico']:
            path = os.path.join(sdir, filename)
            if os.path.exists(path):
                try:
                    img = Image.open(path).convert('RGBA')
                    return img.resize(size, Image.Resampling.LANCZOS)
                except Exception:
                    pass

    # Fallback procedural icon
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse([2, 2, 29, 23], fill=(0, 210, 255, 255), outline=(255, 255, 255, 255), width=1)
    tail_points = [(7, 21), (3, 29), (14, 21)]
    draw.polygon(tail_points, fill=(0, 210, 255, 255), outline=(255, 255, 255, 255))
    draw.polygon([(7, 20), (8, 22), (13, 20)], fill=(0, 210, 255, 255))
    dot_color = (15, 23, 42, 255)
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
        from version import DEFAULT_SERVER_URL
        webbrowser.open(DEFAULT_SERVER_URL)

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
        from version import __version__, __app_name__, __author__, DEFAULT_SERVER_URL
        
        accelerator = self.processor.active_provider if self.processor else "Auto"

        menu = pystray.Menu(
            pystray.MenuItem(f"💬 {__app_name__} v{__version__} by {__author__}", self.open_web_dashboard, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(f"🟢 Сервер: {DEFAULT_SERVER_URL}", self.open_web_dashboard),
            pystray.MenuItem(f"⚡ Ускоритель: {accelerator}", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🌐 Открыть статус в браузере", self.open_web_dashboard),
            pystray.MenuItem("📁 Открыть папку программы", self.open_app_folder),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ Выход", self.quit_app)
        )

        image = get_tray_image((32, 32))
        self.icon = pystray.Icon(
            "Bubblyzer",
            image,
            f"{__app_name__} v{__version__} by {__author__}",
            menu=menu
        )

        def notify_start():
            try:
                self.icon.notify(
                    f"Сервер активен на {DEFAULT_SERVER_URL}\nУскоритель: {accelerator}",
                    f"{__app_name__} v{__version__} by {__author__}"
                )
            except Exception:
                pass

        threading.Timer(0.8, notify_start).start()
        self.icon.run()
