import os
import json
import http.server
import socketserver
from pathlib import Path

PORT = 8180
HISTORY_FILE = Path.home() / ".agent_os_history"

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/history':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            history = []
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, 'r') as f:
                    for line in f:
                        processed_line = line.strip()
                        if processed_line:
                            try:
                                history.append(json.loads(processed_line))
                            except json.JSONDecodeError:
                                pass
            
            # Reverse to show newest on top
            history.reverse()
            self.wfile.write(json.dumps(history).encode())
        else:
            # Fallback to default static file serving for HTML/CSS/JS
            super().do_GET()

if __name__ == "__main__":
    from http.server import ThreadingHTTPServer
    # Ensure server runs out of the dashboard/ directory so index.html works natively
    os.chdir(Path(__file__).parent)
    server_address = ('', PORT)
    with ThreadingHTTPServer(server_address, DashboardHandler) as httpd:
        print(f"Serving Telemetry API on port {PORT}")
        httpd.serve_forever()
