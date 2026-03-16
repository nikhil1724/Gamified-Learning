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


def _request(method: str, url: str, payload=None, timeout: int = 20):
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
    return f"deploycheck_{stamp}_{suffix}@example.com"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check deployed frontend and backend health.")
    parser.add_argument("--frontend", required=True, help="Frontend base URL, e.g. https://example.vercel.app")
    parser.add_argument("--backend", required=True, help="Backend base URL, e.g. https://example.onrender.com")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout seconds")
    parser.add_argument(
        "--skip-register",
        action="store_true",
        help="Skip register endpoint test (register creates a test account).",
    )
    args = parser.parse_args()

    frontend = _normalize_base(args.frontend)
    backend = _normalize_base(args.backend)

    checks = []

    def add_result(name: str, ok: bool, detail: str):
        checks.append((name, ok, detail))

    status, body, err = _request("GET", f"{frontend}/", timeout=args.timeout)
    if err:
        add_result("frontend /", False, err)
    else:
        ok = status == 200 and _contains_html(body)
        add_result("frontend /", ok, f"status={status}")

    status, body, err = _request("GET", f"{frontend}/register", timeout=args.timeout)
    if err:
        add_result("frontend /register", False, err)
    else:
        ok = status == 200 and _contains_html(body)
        add_result("frontend /register", ok, f"status={status}")

    status, body, err = _request("GET", f"{backend}/", timeout=args.timeout)
    if err:
        add_result("backend /", False, err)
    else:
        ok = status == 200 and "Gamified Learning API" in body
        add_result("backend /", ok, f"status={status}")

    status, body, err = _request("GET", f"{backend}/api/test", timeout=args.timeout)
    if err:
        add_result("backend /api/test", False, err)
    else:
        ok = status == 200 and "Backend working" in body
        add_result("backend /api/test", ok, f"status={status}")

    bad_login_payload = {"email": "__deploy_check_missing__@example.com", "password": "WrongPass123!"}
    status, body, err = _request("POST", f"{backend}/api/login", payload=bad_login_payload, timeout=args.timeout)
    if err:
        add_result("backend /api/login", False, err)
    else:
        ok = status in (400, 401, 403)
        add_result("backend /api/login", ok, f"status={status} body={body[:120]}")

    if args.skip_register:
        add_result("backend /api/register", True, "skipped")
    else:
        register_payload = {
            "name": "Deploy Check",
            "email": _rand_email(),
            "role": "student",
            "password": "Test@1234",
        }
        status, body, err = _request(
            "POST",
            f"{backend}/api/register",
            payload=register_payload,
            timeout=args.timeout,
        )
        if err:
            add_result("backend /api/register", False, err)
        else:
            ok = status in (201, 409)
            add_result("backend /api/register", ok, f"status={status} body={body[:120]}")

    failures = 0
    print("Deployment health check")
    print("-----------------------")
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
