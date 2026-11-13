"""
Lightweight Live Web Viewer for Wildlife Intrusion Detection System.
Runs a zero-dependency HTTP server on port 8080 in a background thread.
Enables instant verification of the latest captured image from any laptop or phone browser:
    http://<raspberrypi-ip>:8080
"""

import http.server
import json
import os
import socketserver
import threading
from pathlib import Path
import urllib.parse

from src.Rasp_Pi.raspi_config import LOG_DIR, DETECTION_IMAGE_DIR

PORT = 8080
LATEST_IMAGE_PATH = LOG_DIR / "latest.jpg"
LATEST_JSON_PATH = LOG_DIR / "latest.json"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wildlife Live Detection Monitor</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        body { background: #0f172a; color: #f8fafc; padding: 20px; display: flex; flex-direction: column; align-items: center; min-height: 100vh; }
        .container { max-width: 800px; width: 100%; display: flex; flex-direction: column; gap: 16px; }
        header { background: #1e293b; padding: 18px 24px; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }
        h1 { font-size: 1.25rem; font-weight: 700; color: #38bdf8; display: flex; align-items: center; gap: 8px; }
        .live-dot { width: 10px; height: 10px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 10px #22c55e; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
        .card { background: #1e293b; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }
        .badge-row { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; align-items: center; }
        .badge { padding: 6px 14px; border-radius: 8px; font-weight: 700; text-transform: uppercase; font-size: 0.9rem; letter-spacing: 0.05em; }
        .badge-wildboar { background: #b45309; color: #fef3c7; border: 1px solid #f59e0b; }
        .badge-elephant { background: #1d4ed8; color: #dbeafe; border: 1px solid #3b82f6; }
        .badge-monkey { background: #7c2d12; color: #ffedd5; border: 1px solid #ea580c; }
        .badge-background { background: #334155; color: #94a3b8; border: 1px solid #475569; }
        .badge-uncertain { background: #6b21a8; color: #f3e8ff; border: 1px solid #a855f7; }
        .meta-item { color: #94a3b8; font-size: 0.9rem; }
        .meta-item strong { color: #e2e8f0; }
        .image-box { width: 100%; border-radius: 8px; overflow: hidden; background: #020617; border: 1px solid #334155; display: flex; justify-content: center; align-items: center; min-height: 380px; position: relative; }
        .image-box img { width: 100%; max-height: 540px; object-fit: contain; display: block; }
        .placeholder { color: #64748b; font-size: 1.1rem; text-align: center; }
        .controls { display: flex; justify-content: space-between; align-items: center; margin-top: 12px; font-size: 0.85rem; color: #64748b; }
        button { background: #0284c7; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 600; transition: background 0.2s; }
        button:hover { background: #0369a1; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1><span class="live-dot"></span> Wildlife Live Monitor</h1>
            <div style="font-size: 0.85rem; color: #94a3b8;">Auto-refresh: <strong>Active (2s)</strong></div>
        </header>

        <div class="card">
            <div class="badge-row">
                <span id="speciesBadge" class="badge badge-uncertain">WAITING FOR CAPTURE</span>
                <span class="meta-item">Confidence: <strong id="confidenceVal">--</strong></span>
                <span class="meta-item">Time: <strong id="timeVal">--</strong></span>
                <span class="meta-item">Action: <strong id="actionVal">--</strong></span>
            </div>

            <div class="image-box">
                <img id="latestImg" src="/latest.jpg" alt="Latest Captured Image" onerror="this.style.display='none'; document.getElementById('placeholder').style.display='block';" onload="this.style.display='block'; document.getElementById('placeholder').style.display='none';">
                <div id="placeholder" class="placeholder" style="display:none;">No image captured yet.<br>Sensor standing by for motion.</div>
            </div>

            <div class="controls">
                <span id="statusText">Polling Raspberry Pi...</span>
                <button onclick="refreshData()">Manual Refresh</button>
            </div>
        </div>
    </div>

    <script>
        let lastTimestamp = "";

        async function refreshData() {
            try {
                const res = await fetch('/latest.json?t=' + Date.now());
                if (res.ok) {
                    const data = await res.json();
                    if (data.timestamp !== lastTimestamp) {
                        lastTimestamp = data.timestamp;
                        const species = (data.species || "unknown").toLowerCase();
                        const badge = document.getElementById("speciesBadge");
                        badge.textContent = species.toUpperCase();
                        badge.className = "badge badge-" + species;
                        document.getElementById("confidenceVal").textContent = data.confidence || "--";
                        document.getElementById("timeVal").textContent = data.timestamp || "--";
                        document.getElementById("actionVal").textContent = data.action || "--";

                        const img = document.getElementById("latestImg");
                        img.src = "/latest.jpg?t=" + Date.now();
                        document.getElementById("statusText").textContent = "Updated: " + new Date().toLocaleTimeString();
                    }
                }
            } catch (e) {
                document.getElementById("statusText").textContent = "Waiting for next capture...";
            }
        }

        setInterval(refreshData, 2000);
        refreshData();
    </script>
</body>
</html>
"""


class WildlifeHttpHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
            return

        elif path == "/latest.jpg":
            if LATEST_IMAGE_PATH.exists():
                try:
                    with open(LATEST_IMAGE_PATH, "rb") as f:
                        data = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                except Exception:
                    pass
            self.send_error(404, "No image captured yet")
            return

        elif path == "/latest.json":
            if LATEST_JSON_PATH.exists():
                try:
                    with open(LATEST_JSON_PATH, "rb") as f:
                        data = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                except Exception:
                    pass
            # Default empty json
            default_json = json.dumps({"timestamp": "", "species": "STANDBY", "confidence": "--", "action": "standby"}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(default_json)
            return

        elif path.startswith("/detections/"):
            filename = Path(path).name
            target = DETECTION_IMAGE_DIR / filename
            if target.exists() and target.is_file():
                with open(target, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.end_headers()
                self.wfile.write(data)
                return

        self.send_error(404, "File Not Found")

    def log_message(self, format, *args):
        # Suppress routine HTTP GET logging so it doesn't clutter detection console
        pass


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


_server_thread = None

def start_web_viewer(port=PORT):
    """Starts the web viewer in a background daemon thread."""
    global _server_thread
    if _server_thread is not None and _server_thread.is_alive():
        return

    def run():
        try:
            server = ThreadedHTTPServer(("0.0.0.0", port), WildlifeHttpHandler)
            print(f"[WEB VIEWER] Live image monitor running at http://0.0.0.0:{port}/")
            server.serve_forever()
        except Exception as e:
            print(f"[WEB VIEWER WARNING] Could not start web viewer on port {port}: {e}")

    _server_thread = threading.Thread(target=run, daemon=True, name="WildlifeWebViewer")
    _server_thread.start()


if __name__ == "__main__":
    start_web_viewer()
    import time
    print("Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
