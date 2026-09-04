import os
import sys
import json
import time
import socket
import urllib.request
import urllib.parse
import urllib.error
import threading
from version import __version__

DEFAULT_AFFINITY_MCP_URL = "http://localhost:6767"
DEFAULT_SCRIPT_TITLE = "Bubblyzer by BATCOM"
DEFAULT_SCRIPT_DESC = "Comic speech bubble detector powered by ONNX AI and Affinity integration."

def get_bundled_script_code():
    """Locate and read affinity_bubblyzer.js from bundled or workspace paths."""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_dir = getattr(sys, '_MEIPASS', root_dir)
    
    search_paths = [
        os.path.join(base_dir, "affinity", "affinity_bubblyzer.js"),
        os.path.join(root_dir, "affinity", "affinity_bubblyzer.js"),
        os.path.join(os.getcwd(), "affinity", "affinity_bubblyzer.js"),
        os.path.join(base_dir, "affinity_bubblyzer.js"),
    ]
    for sp in search_paths:
        if os.path.exists(sp):
            try:
                with open(sp, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                print(f"[AffinityBridge] Failed to read script at {sp}: {e}")
    return None

class AffinityMcpClient:
    """Client for Affinity by Canva local MCP bridge."""

    def __init__(self, base_url=None):
        if base_url is None:
            base_url = DEFAULT_AFFINITY_MCP_URL
        self.base_url = base_url.rstrip("/")
        self.sse_url = f"{self.base_url}/sse"
        self.endpoint_url = None
        self._request_id = 0
        self._id_lock = threading.Lock()
        self._responses = {}
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._sse_thread = None
        self._stop_requested = False
        self._sse_response = None
        self._endpoint_ready = threading.Event()

    def _next_id(self):
        with self._id_lock:
            self._request_id += 1
            return self._request_id

    def is_port_open(self, timeout=0.5):
        """Fast TCP check to avoid long urllib timeouts if Affinity is closed."""
        try:
            parsed = urllib.parse.urlparse(self.base_url)
            host = parsed.hostname or "127.0.0.1"
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except Exception:
            return False

    def connect(self, timeout=3.0):
        """Connect to Affinity SSE stream and wait for endpoint."""
        if not self.is_port_open(timeout=min(1.0, timeout)):
            raise ConnectionError(f"Affinity MCP server not listening at {self.base_url}")

        self.close()
        self._stop_requested = False
        self._endpoint_ready.clear()
        self._responses.clear()

        # Connect to SSE
        req = urllib.request.Request(
            self.sse_url,
            headers={
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
                "User-Agent": "Bubblyzer-AffinityBridge/1.0"
            }
        )
        self._sse_response = urllib.request.urlopen(req, timeout=timeout)

        # Start SSE listener thread
        self._sse_thread = threading.Thread(target=self._read_sse_loop, daemon=True)
        self._sse_thread.start()

        # Wait for endpoint event
        if not self._endpoint_ready.wait(timeout=timeout):
            self.close()
            raise TimeoutError("Timed out waiting for MCP endpoint URL from SSE")

        # Perform MCP initialization
        self._handshake(timeout=timeout)

    def _read_sse_loop(self):
        current_event = "message"
        current_data = []

        try:
            while not self._stop_requested and self._sse_response:
                line_bytes = self._sse_response.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode("utf-8", errors="replace").rstrip("\r\n")
                if not line:
                    # End of SSE block, process event
                    if current_data:
                        data_text = "\n".join(current_data)
                        if current_event == "endpoint":
                            self.endpoint_url = urllib.parse.urljoin(self.sse_url, data_text.strip())
                            self._endpoint_ready.set()
                        elif current_event == "message":
                            try:
                                msg = json.loads(data_text)
                                msg_id = msg.get("id")
                                if msg_id is not None:
                                    with self._lock:
                                        self._responses[msg_id] = msg
                                        self._cond.notify_all()
                            except Exception:
                                pass
                    current_event = "message"
                    current_data = []
                elif line.startswith("event:"):
                    current_event = line[6:].strip()
                elif line.startswith("data:"):
                    current_data.append(line[5:].strip())
        except Exception:
            pass
        finally:
            self._endpoint_ready.set()

    def _send_rpc(self, method, params=None, is_notification=False, timeout=5.0):
        if not self.endpoint_url:
            raise ConnectionError("Not connected to Affinity MCP")

        req_id = None if is_notification else self._next_id()
        payload = {"jsonrpc": "2.0", "method": method}
        if req_id is not None:
            payload["id"] = req_id
        if params is not None:
            payload["params"] = params

        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint_url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Bubblyzer-AffinityBridge/1.0"
            }
        )

        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_bytes = resp.read()
            if resp_bytes:
                try:
                    resp_json = json.loads(resp_bytes.decode("utf-8"))
                    if isinstance(resp_json, dict) and resp_json.get("id") == req_id:
                        return resp_json
                except Exception:
                    pass

        if is_notification:
            return None

        # Wait for response from SSE stream
        start_time = time.time()
        with self._cond:
            while req_id not in self._responses:
                remaining = timeout - (time.time() - start_time)
                if remaining <= 0:
                    raise TimeoutError(f"Timeout waiting for MCP response to {method} (id={req_id})")
                self._cond.wait(timeout=remaining)
            return self._responses.pop(req_id)

    def _handshake(self, timeout=3.0):
        # 1. initialize (negotiate protocol version)
        init_res = None
        for proto_version in ["2025-11-05", "2024-11-05"]:
            init_res = self._send_rpc(
                "initialize",
                {
                    "protocolVersion": proto_version,
                    "capabilities": {},
                    "clientInfo": {"name": "Bubblyzer", "version": __version__}
                },
                timeout=timeout
            )
            if init_res and "error" in init_res:
                err_data = init_res["error"].get("data", {})
                supported = err_data.get("supported") if isinstance(err_data, dict) else None
                if supported and isinstance(supported, list) and supported:
                    # Retry with the exact version requested by the server
                    init_res = self._send_rpc(
                        "initialize",
                        {
                            "protocolVersion": supported[0],
                            "capabilities": {},
                            "clientInfo": {"name": "Bubblyzer", "version": __version__}
                        },
                        timeout=timeout
                    )
                    if init_res and "error" not in init_res:
                        break
            else:
                break

        if not init_res or "error" in init_res:
            err_msg = init_res.get("error") if isinstance(init_res, dict) else "No response"
            raise RuntimeError(f"MCP Initialize failed: {err_msg}")

        # 2. initialized notification
        self._send_rpc("notifications/initialized", is_notification=True, timeout=timeout)

    def call_tool(self, name, arguments=None, timeout=5.0):
        res = self._send_rpc(
            "tools/call",
            {"name": name, "arguments": arguments or {}},
            timeout=timeout
        )
        if not res:
            raise RuntimeError(f"No response from Affinity for {name}")
        if "error" in res:
            raise RuntimeError(res["error"].get("message", str(res["error"])))
        return res.get("result", {})

    def check_status(self, timeout=2.5):
        """Check if Affinity MCP is running and list installed scripts."""
        if not self.is_port_open(timeout=0.6):
            return {
                "connected": False,
                "installed": False,
                "scripts": [],
                "error": "Affinity MCP port not reachable"
            }

        try:
            self.connect(timeout=timeout)
            # Call list_library_scripts
            result = self.call_tool("list_library_scripts", {}, timeout=timeout)
            text_items = []
            for item in result.get("content", []):
                if item.get("type") == "text":
                    text_items.append(item.get("text", ""))
            raw_text = "\n".join(text_items)

            scripts = [
                s.strip()
                for s in raw_text.replace("\n", ",").split(",")
                if s.strip()
            ]

            installed = any(
                "bubblyzer" in s.lower()
                for s in scripts
            )

            return {
                "connected": True,
                "installed": installed,
                "scripts": scripts,
                "error": None
            }
        except Exception as e:
            # If port was open, Affinity is running even if listing tools had a transient error
            return {
                "connected": True,
                "installed": False,
                "scripts": [],
                "error": str(e)
            }
        finally:
            self.close()

    def install_script(self, code=None, title=DEFAULT_SCRIPT_TITLE, description=DEFAULT_SCRIPT_DESC, timeout=6.0):
        """Install or update script in Affinity's Scripts panel."""
        if not code:
            code = get_bundled_script_code()
            if not code:
                return {"success": False, "error": "Script file affinity_bubblyzer.js not found"}

        try:
            self.connect(timeout=min(3.0, timeout))
            result = self.call_tool(
                "save_script_to_library",
                {
                    "title": title,
                    "description": description,
                    "code": code
                },
                timeout=timeout
            )
            # Check if Affinity returned an error in the text content
            text_chunks = [
                c.get("text", "")
                for c in result.get("content", [])
                if c.get("type") == "text"
            ]
            full_text = "\n".join(text_chunks)
            if full_text.lower().startswith("error"):
                if "already exists" in full_text.lower():
                    return {"success": True, "already_installed": True, "message": full_text}
                return {"success": False, "error": full_text}

            return {"success": True, "message": "Script installed successfully into Affinity"}
        except Exception as e:
            if "already exists" in str(e).lower():
                return {"success": True, "already_installed": True, "message": str(e)}
            return {"success": False, "error": str(e)}
        finally:
            self.close()

    def execute_script(self, code=None, timeout=10.0):
        """Execute script directly in the active Affinity document."""
        if not code:
            code = get_bundled_script_code()
            if not code:
                return {"success": False, "error": "Script file affinity_bubblyzer.js not found"}

        try:
            self.connect(timeout=min(3.0, timeout))
            result = self.call_tool(
                "execute_script",
                {"script": code},
                timeout=timeout
            )
            text_chunks = [
                c.get("text", "")
                for c in result.get("content", [])
                if c.get("type") == "text"
            ]
            full_text = "\n".join(text_chunks)
            return {"success": True, "output": full_text}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            self.close()

    def close(self):
        """Cleanly close open connection."""
        self._stop_requested = True
        if self._sse_response:
            try:
                self._sse_response.close()
            except Exception:
                pass
            self._sse_response = None
        self.endpoint_url = None
        with self._cond:
            self._cond.notify_all()

_bridge_lock = threading.Lock()

def check_affinity_status(base_url=None, timeout=3.0):
    """Check connection status and script installation state."""
    with _bridge_lock:
        return AffinityMcpClient(base_url=base_url).check_status(timeout=timeout)

def install_bubblyzer_script(base_url=None, timeout=25.0):
    """Install or update Bubblyzer script in Affinity."""
    with _bridge_lock:
        return AffinityMcpClient(base_url=base_url).install_script(timeout=timeout)

def execute_bubblyzer_script(base_url=None):
    """Directly launch Bubblyzer script in active Affinity document asynchronously."""
    def _background_run():
        with _bridge_lock:
            try:
                client = AffinityMcpClient(base_url=base_url)
                client.execute_script(timeout=600.0)
            except Exception as e:
                print(f"[AffinityBridge] Background execute warning: {e}")

    # Launch in thread so modal dialog in Affinity doesn't block web HTTP response
    t = threading.Thread(target=_background_run, daemon=True)
    t.start()
    return {"success": True, "message": "Скрипт запущен в Affinity"}

