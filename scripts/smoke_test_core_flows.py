import argparse
import json
import random
import string
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone


def _normalize_base(url: str) -> str:
    return (url or "").strip().rstrip("/")


def _request(method: str, url: str, payload=None, timeout: int = 25):
    body = None
    headers = {}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url=url, data=body, method=method, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            return resp.status, text, None
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        return exc.code, text, None
    except Exception as exc:
        return None, "", str(exc)


def _contains_html(text: str) -> bool:
    sample = (text or "").lower()
    return "<html" in sample or "<!doctype html" in sample


def _rand_email() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"smoketest_{stamp}_{suffix}@example.com"


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test core frontend/backend flows.")
    parser.add_argument("--frontend", required=True, help="Frontend base URL")
    parser.add_argument("--backend", required=True, help="Backend base URL")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds")
    parser.add_argument(
        "--skip-register",
        action="store_true",
        help="Skip register endpoint check (recommended for CI to avoid test-user churn).",
    )
    args = parser.parse_args()

    frontend = _normalize_base(args.frontend)
    backend = _normalize_base(args.backend)

    checks = []

    def add_result(name: str, ok: bool, detail: str):
        checks.append((name, ok, detail))

    # Frontend reachability
    status, body, err = _request("GET", f"{frontend}/", timeout=args.timeout)
    if err:
        add_result("frontend /", False, err)
    else:
        add_result("frontend /", status == 200 and _contains_html(body), f"status={status}")

    status, body, err = _request("GET", f"{frontend}/login", timeout=args.timeout)
    if err:
        add_result("frontend /login", False, err)
    else:
        add_result("frontend /login", status == 200 and _contains_html(body), f"status={status}")

    # Backend liveness and auth behavior
    status, body, err = _request("GET", f"{backend}/api/test", timeout=args.timeout)
    if err:
        add_result("backend /api/test", False, err)
    else:
        add_result("backend /api/test", status == 200 and "Backend working" in body, f"status={status}")

    status, body, err = _request(
        "POST",
        f"{backend}/api/login",
        payload={"email": "missing_smoke_user@example.com", "password": "WrongPass123!"},
        timeout=args.timeout,
    )
    if err:
        add_result("backend /api/login invalid creds", False, err)
    else:
        add_result(
            "backend /api/login invalid creds",
            status in (400, 401, 403),
            f"status={status}",
        )

    # Read-only endpoints that should not 5xx/405 under normal conditions.
    for endpoint in ("/api/courses", "/api/leaderboard"):
        status, body, err = _request("GET", f"{backend}{endpoint}", timeout=args.timeout)
        if err:
            add_result(f"backend {endpoint}", False, err)
            continue
        add_result(f"backend {endpoint}", status is not None and status < 500 and status != 405, f"status={status}")

    if args.skip_register:
        add_result("backend /api/register", True, "skipped")
    else:
        payload = {
            "name": "Smoke Test",
            "email": _rand_email(),
            "role": "student",
            "password": "Test@1234",
        }
        status, body, err = _request("POST", f"{backend}/api/register", payload=payload, timeout=args.timeout)
        if err:
            add_result("backend /api/register", False, err)
        else:
            add_result("backend /api/register", status in (201, 409), f"status={status}")

    failures = 0
    print("Core smoke test")
    print("---------------")
    print(f"Frontend: {frontend}")
    print(f"Backend : {backend}")
    print("")

    for name, ok, detail in checks:
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name}: {detail}")
        if not ok:
            failures += 1

    print("")
    if failures:
        print(f"Result: FAILED ({failures} checks failed)")
        return 1

    print("Result: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
