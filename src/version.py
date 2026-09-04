"""
Single source of truth for Bubblyzer version, network ports, and metadata.
"""

__version__ = "1.1.2"
__app_name__ = "Bubblyzer"
__author__ = "BATCOM"
__author_url__ = "https://nananabat.com"
__boosty_url__ = "https://boosty.to/nananabatcom"

# Dedicated non-standard port to avoid conflicts with AirPlay (5000), React (3000), Vite (5173), etc.
DEFAULT_PORT = 28734
DEFAULT_HOST = "127.0.0.1"
DEFAULT_SERVER_URL = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}"
