"""Serve only public keys and verified release artifacts on the local network."""

import argparse
import json
import mimetypes
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from socketserver import TCPServer

ROOT = Path(__file__).resolve().parents[1]


class LanServer(ThreadingHTTPServer):
    def server_bind(self) -> None:
        # HTTPServer's reverse DNS lookup can stall on local Wi-Fi addresses.
        TCPServer.server_bind(self)
        self.server_name, self.server_port = self.server_address[:2]


class DownloadHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        version = json.loads((ROOT / "package.json").read_text())["version"]
        allowed = {
            "/key": ROOT / ".cache/ssh/deckymods_ed25519.pub",
            "/mods.zip": ROOT / f"release/DeckyMods-v{version}.zip",
            "/source.tar.gz": ROOT / f"release/DeckyMods-v{version}-source.tar.gz",
            "/SHA256SUMS": ROOT / "release/SHA256SUMS",
            "/update.json": ROOT / "release/update.json",
            "/update.json.sig": ROOT / "release/update.json.sig",
        }
        target = allowed.get(self.path)
        if target is None or target.is_symlink() or not target.is_file():
            self.send_error(404)
            return
        payload = target.read_bytes()
        self.send_response(200)
        self.send_header(
            "Content-Type", mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        )
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bind", required=True)
    parser.add_argument("--port", default=8767, type=int)
    parser.add_argument("--persistent", action="store_true")
    args = parser.parse_args()
    with LanServer((args.bind, args.port), DownloadHandler) as server:
        timer = None if args.persistent else threading.Timer(7200, server.shutdown)
        if timer:
            timer.daemon = True
            timer.start()
        try:
            print(f"LAN downloads: http://{args.bind}:{args.port}/mods.zip", flush=True)
            server.serve_forever()
        finally:
            if timer:
                timer.cancel()


if __name__ == "__main__":
    main()
