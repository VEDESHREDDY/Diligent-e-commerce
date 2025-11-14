"""
Simple helper to serve the repo root while automatically redirecting /
to the dashboard at /frontend/.
"""

from __future__ import annotations

import http.server
import os
import socketserver
from pathlib import Path


PORT = int(os.environ.get("PORT", "8000"))
ROOT = Path(__file__).resolve().parent


def handler_factory() -> type[http.server.SimpleHTTPRequestHandler]:
    class RedirectingHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT), **kwargs)

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            # Keep default logging behavior (prints to stdout)
            super().log_message(format, *args)

        def do_GET(self) -> None:  # noqa: D401
            if self.path in {"/", ""}:
                self.send_response(302)
                self.send_header("Location", "/frontend/")
                self.end_headers()
                return
            return super().do_GET()

    return RedirectingHandler


def main() -> None:
    handler = handler_factory()
    with socketserver.ThreadingTCPServer(("", PORT), handler) as httpd:
        print(f"🔌 Server running at http://localhost:{PORT}/frontend/")
        print("Press Ctrl+C to stop.")
        httpd.serve_forever()


if __name__ == "__main__":
    main()

