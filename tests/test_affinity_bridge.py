import os
import sys
import json
import time
import socket
import threading
import unittest
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

class MockMcpServerHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress logs in tests

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/sse":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            # Store connection for sending SSE events
            self.server.active_sse_wfile = self.wfile
            self.server.active_sse_handler = self

            # Send endpoint event
            endpoint_msg = "event: endpoint\ndata: /message?sessionId=test-session-123\n\n"
            self.wfile.write(endpoint_msg.encode("utf-8"))
            self.wfile.flush()

            # Keep connection open until server stops
            while not self.server.stop_requested:
                time.sleep(0.05)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/message":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)

            self.server.received_messages.append(data)

            msg_id = data.get("id")
            method = data.get("method")
            params = data.get("params", {})

            # Respond via SSE event stream or direct response
            response = None
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "MockAffinity", "version": "2.5.0"}
                    }
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                if tool_name == "read_sdk_documentation_topic":
                    response = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {"content": [{"type": "text", "text": "Preamble content"}]}
                    }
                elif tool_name == "list_library_scripts":
                    response = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {"content": [{"type": "text", "text": "ExistingScript, Bubblyzer by BATCOM"}]}
                    }
                elif tool_name == "save_script_to_library":
                    self.server.installed_scripts.append(tool_args)
                    response = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {"content": [{"type": "text", "text": "Saved successfully"}]}
                    }
                elif tool_name == "execute_script":
                    self.server.executed_scripts.append(tool_args)
                    response = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {"content": [{"type": "text", "text": "Script output: Done"}]}
                    }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"{}")

            # Send response over SSE
            if response and hasattr(self.server, "active_sse_wfile") and self.server.active_sse_wfile:
                sse_payload = f"event: message\ndata: {json.dumps(response)}\n\n"
                try:
                    self.server.active_sse_wfile.write(sse_payload.encode("utf-8"))
                    self.server.active_sse_wfile.flush()
                except Exception:
                    pass
        else:
            self.send_response(404)
            self.end_headers()

class TestAffinityBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start mock MCP server on a free port
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), MockMcpServerHandler)
        cls.port = cls.server.server_port
        cls.server.stop_requested = False
        cls.server.received_messages = []
        cls.server.installed_scripts = []
        cls.server.executed_scripts = []
        cls.server.active_sse_wfile = None

        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop_requested = True
        cls.server.shutdown()
        cls.server.server_close()

    def test_01_offline_server(self):
        from affinity_bridge import AffinityMcpClient
        # Connect to an unused port
        client = AffinityMcpClient(base_url="http://127.0.0.1:59999")
        status = client.check_status(timeout=0.3)
        self.assertFalse(status["connected"])
        self.assertIn("error", status)

    def test_02_mock_server_handshake_and_status(self):
        from affinity_bridge import AffinityMcpClient
        client = AffinityMcpClient(base_url=f"http://127.0.0.1:{self.port}")
        status = client.check_status(timeout=2.0)
        self.assertTrue(status["connected"])
        self.assertTrue(status.get("installed"))
        self.assertIn("Bubblyzer by BATCOM", status.get("scripts", []))

    def test_03_install_script(self):
        from affinity_bridge import AffinityMcpClient
        client = AffinityMcpClient(base_url=f"http://127.0.0.1:{self.port}")
        result = client.install_script(
            title="Bubblyzer by BATCOM",
            description="Comic bubble detector",
            code="// test code"
        )
        self.assertTrue(result["success"])
        self.assertTrue(any(s["title"] == "Bubblyzer by BATCOM" for s in self.server.installed_scripts))

    def test_04_execute_script(self):
        from affinity_bridge import AffinityMcpClient
        client = AffinityMcpClient(base_url=f"http://127.0.0.1:{self.port}")
        result = client.execute_script("// console.log('hello');")
        self.assertTrue(result["success"])
        self.assertEqual(len(self.server.executed_scripts), 1)

    def test_05_server_endpoints(self):
        import affinity_bridge
        import server

        # Temporarily patch default URL to point to mock server
        orig_url = affinity_bridge.DEFAULT_AFFINITY_MCP_URL
        affinity_bridge.DEFAULT_AFFINITY_MCP_URL = f"http://127.0.0.1:{self.port}"
        try:
            client = server.app.test_client()

            # Test GET /affinity/status
            resp = client.get('/affinity/status')
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertTrue(data["connected"])

            # Test POST /affinity/install
            resp = client.post('/affinity/install')
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertTrue(data["success"])

            # Test POST /affinity/execute
            resp = client.post('/affinity/execute')
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertTrue(data["success"])
        finally:
            affinity_bridge.DEFAULT_AFFINITY_MCP_URL = orig_url

if __name__ == "__main__":
    unittest.main()
