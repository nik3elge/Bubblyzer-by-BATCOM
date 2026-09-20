import unittest
import json
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.server import app

class TestServerEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_status_endpoint(self):
        response = self.client.get('/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn("name", data)
        self.assertIn("version", data)
        self.assertEqual(data.get("status"), "ready")

    def test_dashboard_endpoint(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Bubblyzer", html)
        self.assertIn("Bubblyzer.afscript", html)
        # Verify MCP card is not present
        self.assertNotIn("affinity-card", html)
        self.assertNotIn("affinity_bridge", html)

    def test_config_endpoint(self):
        response = self.client.get('/config')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIsInstance(data, dict)

    def test_download_afscript_endpoint(self):
        response = self.client.get('/download/afscript')
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response.headers.get("Content-Disposition", ""))
        self.assertIn("Bubblyzer.afscript", response.headers.get("Content-Disposition", ""))
        self.assertGreater(len(response.data), 1000)
        response.close()

if __name__ == '__main__':
    unittest.main()
