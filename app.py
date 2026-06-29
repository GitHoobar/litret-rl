#!/usr/bin/env python3
"""
Minimal, dependency-free HTTP service for converting durations.

Uses only the Python standard library, so it runs with no extra packages:

    python app.py            # serves on http://localhost:8000

Endpoints
---------
GET /health
    Liveness probe.
    -> 200  {"status": "ok"}

GET /convert?value=<duration>
    Convert a duration into a number of seconds. ``value`` may be a plain
    integer number of seconds ("3600") or a unit-suffixed string using one of
    s (seconds), m (minutes), h (hours) or d (days), e.g. "30s", "15m", "2h".

    -> 200  {"value": "<duration>", "seconds": <int>}
    -> 400  {"error": "<message>"}   for a missing or invalid ``value``
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


# Duration unit -> seconds.
UNITS = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
}


def convert_to_seconds(value: str) -> int:
    """
    Convert a duration string into seconds.

    Accepts a plain integer number of seconds ("3600") or a unit-suffixed
    string ("30s", "15m", "2h", "1d").

    Raises:
        ValueError: if the value is empty, uses an unknown unit, or the numeric
            portion cannot be parsed.
    """
    text = value.strip().lower()
    if not text:
        raise ValueError("duration is empty")

    unit = text[-1]
    if unit not in UNITS:
        raise ValueError(f"unknown duration unit: {unit!r}")

    amount = int(text[:-1])
    if amount <= 0:
        raise ValueError("duration must be positive")

    return amount * UNITS[unit]


class DurationHandler(BaseHTTPRequestHandler):
    """Routes GET requests for the duration service."""

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            self._send_json(200, {"status": "ok"})
            return

        if parsed.path == "/convert":
            params = parse_qs(parsed.query)
            value = params.get("value", [""])[0]
            try:
                seconds = convert_to_seconds(value)
            except ValueError as exc:
                self._send_json(400, {"error": str(exc)})
                return
            self._send_json(200, {"value": value, "seconds": seconds})
            return

        self._send_json(404, {"error": "not found"})

    def log_message(self, *args):
        # Quiet by default; the service is meant to be scripted against.
        pass


def main(host="0.0.0.0", port=8000):
    server = HTTPServer((host, port), DurationHandler)
    print(f"Serving duration service on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
