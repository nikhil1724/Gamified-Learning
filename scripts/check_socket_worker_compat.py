#!/usr/bin/env python3
"""Guardrail: prevent enabling Socket.IO realtime on sync Gunicorn workers."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import sys


ASYNC_WORKER_HINTS = (
    "geventwebsocket",
    "gevent",
    "eventlet",
    "uvicorn.workers",
    "gthread",
)


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def read_web_command(procfile: Path) -> str | None:
    if not procfile.exists():
        return None

    for line in procfile.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.lower().startswith("web:"):
            return stripped.split(":", 1)[1].strip()
    return None


def is_async_gunicorn_command(command: str) -> bool:
    lower = command.lower()
    if "gunicorn" not in lower:
        return False

    worker_class_match = re.search(r"--worker-class\s+([^\s]+)", lower)
    if worker_class_match:
        worker_class = worker_class_match.group(1)
        if worker_class == "sync":
            return False

    return any(hint in lower for hint in ASYNC_WORKER_HINTS)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Socket.IO realtime flag against Gunicorn worker mode."
    )
    parser.add_argument(
        "--realtime-enabled",
        default=None,
        help="Whether frontend realtime sockets are enabled (true/false).",
    )
    parser.add_argument(
        "--procfile",
        action="append",
        default=[],
        help="Procfile path to inspect (can be provided multiple times).",
    )

    args = parser.parse_args()
    realtime_source = args.realtime_enabled
    if realtime_source is None:
        realtime_source = os.getenv("REACT_APP_ENABLE_REALTIME", "false")
    realtime_enabled = parse_bool(realtime_source)

    procfile_paths = [Path(path) for path in args.procfile] or [Path("Procfile"), Path("backend/Procfile")]

    detected = []
    for procfile in procfile_paths:
        command = read_web_command(procfile)
        if not command:
            continue
        detected.append((procfile, command, is_async_gunicorn_command(command)))

    if not realtime_enabled:
        print("PASS: REACT_APP_ENABLE_REALTIME is disabled. Socket guard OK.")
        return 0

    if not detected:
        print("FAIL: Realtime is enabled but no Procfile web command was found to validate.")
        return 1

    async_entries = [entry for entry in detected if entry[2]]
    if not async_entries:
        print("FAIL: Realtime is enabled, but no async Gunicorn worker was detected.")
        for procfile, command, _ in detected:
            print(f"  - {procfile}: {command}")
        print("Hint: use --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker, gevent, or eventlet.")
        return 1

    print("PASS: Realtime is enabled and async worker support was detected.")
    for procfile, command, is_async in detected:
        status = "async" if is_async else "not-async"
        print(f"  - {procfile}: [{status}] {command}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
