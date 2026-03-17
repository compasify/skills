#!/usr/bin/env python3
"""
Lightweight HTTP server for writing Markdown content to files.

Internal-only API. No authentication. Designed to be started on-demand
by AI agents, used for writes, then stopped.

Endpoints:
    POST /write   - Write/overwrite content to a file
    POST /append  - Append content to an existing file
    GET  /health  - Health check
    POST /stop    - Gracefully shut down the server

Usage:
    # Start server (default port 9111)
    python md_writer_server.py

    # Custom port
    python md_writer_server.py --port 8888

    # Write content via curl
    curl -X POST http://localhost:9111/write \
      -H "Content-Type: application/json" \
      -d '{"path": "output.md", "content": "# Hello World"}'

    # Append content
    curl -X POST http://localhost:9111/append \
      -H "Content-Type: application/json" \
      -d '{"path": "output.md", "content": "\\n## New Section"}'

    # Stop server
    curl -X POST http://localhost:9111/stop
"""

import argparse
import json
import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


class MdWriterHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
        else:
            self._send_json(404, {"error": f"Not found: {self.path}"})

    def do_POST(self):
        if self.path == "/write":
            self._handle_write(mode="w")
        elif self.path == "/append":
            self._handle_write(mode="a")
        elif self.path == "/stop":
            self._send_json(200, {"status": "shutting_down"})
            # Shutdown in a separate thread to allow response to complete
            threading.Thread(target=self.server.shutdown, daemon=True).start()
        else:
            self._send_json(404, {"error": f"Not found: {self.path}"})

    def _handle_write(self, mode: str):
        try:
            body = self._read_body()
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            self._send_json(400, {"error": f"Invalid JSON: {e}"})
            return

        file_path = body.get("path")
        content = body.get("content")

        if not file_path:
            self._send_json(400, {"error": "Missing required field: path"})
            return
        if content is None:
            self._send_json(400, {"error": "Missing required field: content"})
            return

        try:
            target = Path(file_path)
            target.parent.mkdir(parents=True, exist_ok=True)

            if mode == "a" and target.exists():
                existing = target.read_text(encoding="utf-8")
                if existing and not existing.endswith("\n"):
                    content = "\n" + content

            if content and not content.endswith("\n"):
                content += "\n"

            with open(target, mode, encoding="utf-8", newline="") as f:
                f.write(content)

            line_count = target.read_text(encoding="utf-8").count("\n")
            size_kb = target.stat().st_size / 1024

            action = "Appended to" if mode == "a" else "Wrote"
            self._send_json(
                200,
                {
                    "status": "ok",
                    "action": action,
                    "path": str(target.resolve()),
                    "lines": line_count,
                    "size_kb": round(size_kb, 1),
                },
            )

        except PermissionError:
            self._send_json(403, {"error": f"Permission denied: {file_path}"})
        except OSError as e:
            self._send_json(500, {"error": f"OS error: {e}"})
        except Exception as e:
            self._send_json(500, {"error": f"Unexpected error: {e}"})

    def log_message(self, format, *args):
        print(f"[md-writer] {args[0]}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Markdown writer HTTP server")
    parser.add_argument(
        "--port", type=int, default=9111, help="Port to listen on (default: 9111)"
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)"
    )
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), MdWriterHandler)
    print(f"[md-writer] Server started at http://{args.host}:{args.port}", flush=True)
    print(
        f"[md-writer] Endpoints: POST /write, POST /append, GET /health, POST /stop",
        flush=True,
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("[md-writer] Server stopped.", flush=True)


if __name__ == "__main__":
    main()
