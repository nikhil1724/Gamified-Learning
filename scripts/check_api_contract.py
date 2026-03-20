import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


FRONTEND_CALL_RE = re.compile(
    r"\bapi\.(get|post|put|patch|delete)\(\s*([\"'`])(?P<path>/[^\"'`]+)\2",
    re.IGNORECASE,
)

BACKEND_BLUEPRINT_RE = re.compile(
    r"Blueprint\([^\)]*url_prefix\s*=\s*([\"'])(?P<prefix>/[^\"']*)\1"
)

BACKEND_DECORATOR_SIMPLE_RE = re.compile(
    r"@\w+_bp\.(?P<method>get|post|put|patch|delete)\(\s*([\"'])(?P<path>/[^\"']*)\2\s*\)",
    re.IGNORECASE,
)

BACKEND_DECORATOR_ROUTE_RE = re.compile(
    r"@\w+_bp\.route\(\s*([\"'])(?P<path>/[^\"']*)\1\s*,\s*methods\s*=\s*\[(?P<methods>[^\]]+)\]",
    re.IGNORECASE,
)

METHOD_LITERAL_RE = re.compile(r"['\"](?P<method>[A-Z]+)['\"]")


@dataclass(frozen=True)
class Endpoint:
    method: str
    path: str
    source: str


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def _normalize_path(path: str) -> str:
    normalized = (path or "").strip()
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    normalized = re.sub(r"//+", "/", normalized)
    return normalized.rstrip("/") or "/"


def _frontend_to_api_path(frontend_path: str) -> str:
    path = _normalize_path(frontend_path)
    if path == "/":
        return "/api"
    if path.startswith("/api/") or path == "/api":
        return path
    return _normalize_path(f"/api{path}")


def _canonicalize_path(path: str) -> str:
    normalized = _normalize_path(path)
    normalized = re.sub(r"\$\{[^}]+\}", "{param}", normalized)
    normalized = re.sub(r"<[^>]+>", "{param}", normalized)
    return normalized


def _to_match_pattern(canonical_path: str) -> re.Pattern:
    escaped = re.escape(canonical_path)
    escaped = escaped.replace(re.escape("{param}"), r"[^/]+")
    return re.compile(rf"^{escaped}$")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def collect_frontend_endpoints(frontend_root: Path) -> List[Endpoint]:
    endpoints: List[Endpoint] = []
    for file_path in frontend_root.rglob("*.js"):
        text = _read_text(file_path)
        for match in FRONTEND_CALL_RE.finditer(text):
            method = match.group(1).upper()
            path = match.group("path")
            api_path = _frontend_to_api_path(path)
            endpoints.append(
                Endpoint(
                    method=method,
                    path=_canonicalize_path(api_path),
                    source=str(file_path),
                )
            )

    for file_path in frontend_root.rglob("*.jsx"):
        text = _read_text(file_path)
        for match in FRONTEND_CALL_RE.finditer(text):
            method = match.group(1).upper()
            path = match.group("path")
            api_path = _frontend_to_api_path(path)
            endpoints.append(
                Endpoint(
                    method=method,
                    path=_canonicalize_path(api_path),
                    source=str(file_path),
                )
            )

    return endpoints


def _collect_blueprint_prefix(text: str) -> Optional[str]:
    match = BACKEND_BLUEPRINT_RE.search(text)
    if not match:
        return None
    return _normalize_path(match.group("prefix"))


def collect_backend_endpoints(routes_root: Path) -> List[Endpoint]:
    endpoints: List[Endpoint] = []

    for file_path in routes_root.rglob("*.py"):
        text = _read_text(file_path)
        prefix = _collect_blueprint_prefix(text)

        for match in BACKEND_DECORATOR_SIMPLE_RE.finditer(text):
            method = match.group("method").upper()
            raw_path = _normalize_path(match.group("path"))
            full_path = _normalize_path(f"{prefix or ''}{raw_path}")
            endpoints.append(
                Endpoint(
                    method=method,
                    path=_canonicalize_path(full_path),
                    source=str(file_path),
                )
            )

        for match in BACKEND_DECORATOR_ROUTE_RE.finditer(text):
            raw_path = _normalize_path(match.group("path"))
            full_path = _normalize_path(f"{prefix or ''}{raw_path}")
            methods_blob = match.group("methods")
            methods = [
                method_match.group("method").upper()
                for method_match in METHOD_LITERAL_RE.finditer(methods_blob)
            ]
            for method in methods:
                if method == "OPTIONS":
                    continue
                endpoints.append(
                    Endpoint(
                        method=method,
                        path=_canonicalize_path(full_path),
                        source=str(file_path),
                    )
                )

    return endpoints


def map_frontend_to_backend(
    frontend_endpoints: List[Endpoint], backend_endpoints: List[Endpoint]
) -> Tuple[List[Endpoint], List[Tuple[Endpoint, Endpoint]]]:
    backend_by_method: Dict[str, List[Endpoint]] = {}
    for endpoint in backend_endpoints:
        backend_by_method.setdefault(endpoint.method, []).append(endpoint)

    missing: List[Endpoint] = []
    matched: List[Tuple[Endpoint, Endpoint]] = []

    for frontend_ep in frontend_endpoints:
        candidates = backend_by_method.get(frontend_ep.method, [])
        frontend_pattern = _to_match_pattern(frontend_ep.path)
        found = None
        for backend_ep in candidates:
            backend_pattern = _to_match_pattern(backend_ep.path)
            if frontend_pattern.match(backend_ep.path) or backend_pattern.match(frontend_ep.path):
                found = backend_ep
                break

        if found:
            matched.append((frontend_ep, found))
        else:
            missing.append(frontend_ep)

    return missing, matched


def _http_request(
    method: str,
    url: str,
    payload=None,
    token: Optional[str] = None,
    timeout: int = 20,
    retries: int = 2,
):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(url=url, method=method, headers=headers, data=body)
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                text = response.read().decode("utf-8", errors="replace")
                return response.status, text, None
        except urllib.error.HTTPError as exc:
            text = exc.read().decode("utf-8", errors="replace")
            return exc.code, text, None
        except Exception as exc:
            is_last = attempt >= retries
            if is_last:
                return None, "", str(exc)
            time.sleep(0.5 * (attempt + 1))


def _fill_placeholders(path: str) -> str:
    replacements = {
        "course": "python",
        "lesson": "1",
        "user_id": "1",
        "course_id": "1",
        "problem_id": "1",
        "quiz_id": "1",
        "student_id": "1",
        "teacher_id": "1",
        "token": "invalid-token",
        "note_id": "1",
        "notification_id": "1",
        "filename": "placeholder.pdf",
    }

    def replace(match: re.Match) -> str:
        key = match.group(1)
        return replacements.get(key, "1")

    return re.sub(r"\{([^}]+)\}", replace, path)


def _is_read_only_method(method: str) -> bool:
    return method in {"GET", "HEAD"}


def _is_safe_to_probe_without_payload(path: str, method: str) -> bool:
    if method != "GET":
        return False
    deny_fragments = (
        "/uploads/",
    )
    return not any(fragment in path for fragment in deny_fragments)


def _is_public_probe_candidate(path: str) -> bool:
    canonical = _canonicalize_path(path)
    public_exact = {
        "/api/courses",
        "/api/leaderboard",
        "/api/problems",
        "/api/quizzes",
        "/api/rewards",
    }
    public_prefixes = (
        "/api/problem/",
        "/api/quiz/",
    )

    if canonical in public_exact:
        return True
    return any(canonical.startswith(prefix) for prefix in public_prefixes)


def run_live_contract_checks(
    backend_base: str,
    frontend_endpoints: List[Endpoint],
    timeout: int,
    token: Optional[str],
    probe_authless_all: bool,
) -> List[CheckResult]:
    checks: List[CheckResult] = []

    # Login/Register are checked explicitly with safe payloads.
    login_status, login_body, login_err = _http_request(
        "POST",
        f"{backend_base}/api/login",
        payload={"email": "contractcheck_missing@example.com", "password": "WrongPass123!"},
        timeout=timeout,
    )
    if login_err:
        checks.append(CheckResult("live /api/login", False, login_err))
    else:
        checks.append(
            CheckResult(
                "live /api/login",
                login_status in {400, 401, 403},
                f"status={login_status}",
            )
        )

    register_status, register_body, register_err = _http_request(
        "POST",
        f"{backend_base}/api/register",
        payload={
            "name": "Contract Check",
            "email": "contractcheck_existing@example.com",
            "password": "Test@1234",
        },
        timeout=timeout,
    )
    if register_err:
        checks.append(CheckResult("live /api/register", False, register_err))
    else:
        checks.append(
            CheckResult(
                "live /api/register",
                register_status in {201, 400, 409},
                f"status={register_status}",
            )
        )

    seen: Set[Tuple[str, str]] = set()
    for endpoint in frontend_endpoints:
        key = (endpoint.method, endpoint.path)
        if key in seen:
            continue
        seen.add(key)

        if not _is_safe_to_probe_without_payload(endpoint.path, endpoint.method):
            continue

        if not token and not probe_authless_all and not _is_public_probe_candidate(endpoint.path):
            continue

        probe_path = _fill_placeholders(endpoint.path)
        url = f"{backend_base}{probe_path}"
        status, body, err = _http_request(endpoint.method, url, timeout=timeout, token=token)

        name = f"live {endpoint.method} {endpoint.path}"
        if err:
            checks.append(CheckResult(name, False, err))
            continue

        # Contract expectation: endpoint should exist and never error with 5xx.
        # Auth-required endpoints may return 401/403 without token.
        ok = status is not None and status < 500 and status != 405
        checks.append(CheckResult(name, ok, f"status={status}"))

    return checks


def print_section(title: str):
    print("\n" + title)
    print("-" * len(title))


def main() -> int:
    parser = argparse.ArgumentParser(description="Frontend-to-backend API contract checker.")
    parser.add_argument(
        "--workspace",
        default=".",
        help="Workspace root containing frontend/ and backend/ folders.",
    )
    parser.add_argument(
        "--backend",
        default="",
        help="Optional live backend base URL (example: https://myapp.onrender.com).",
    )
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout seconds for live checks.")
    parser.add_argument(
        "--token",
        default="",
        help="Optional JWT token for live checks requiring authentication.",
    )
    parser.add_argument(
        "--probe-authless-all",
        action="store_true",
        help="Probe all discovered endpoints even without a token (can generate many expected 401 logs).",
    )
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    frontend_root = workspace / "frontend" / "src"
    routes_root = workspace / "backend" / "routes"

    if not frontend_root.exists() or not routes_root.exists():
        print("Missing expected frontend/src or backend/routes directories.")
        return 2

    frontend_eps = collect_frontend_endpoints(frontend_root)
    backend_eps = collect_backend_endpoints(routes_root)

    missing, matched = map_frontend_to_backend(frontend_eps, backend_eps)

    print_section("Static Contract Audit")
    print(f"Frontend API calls discovered: {len(frontend_eps)}")
    print(f"Backend endpoints discovered: {len(backend_eps)}")
    print(f"Matched frontend calls: {len(matched)}")
    print(f"Missing contract matches: {len(missing)}")

    if missing:
        print("\nPotential mismatches:")
        for endpoint in sorted(missing, key=lambda ep: (ep.method, ep.path))[:50]:
            print(f"  - {endpoint.method} {endpoint.path} ({endpoint.source})")

    live_failures = 0
    if args.backend:
        backend_base = args.backend.strip().rstrip("/")
        live_checks = run_live_contract_checks(
            backend_base=backend_base,
            frontend_endpoints=frontend_eps,
            timeout=args.timeout,
            token=args.token.strip() or None,
            probe_authless_all=args.probe_authless_all,
        )

        print_section("Live Contract Audit")
        print(f"Backend: {backend_base}")

        for check in live_checks:
            mark = "PASS" if check.ok else "FAIL"
            print(f"[{mark}] {check.name}: {check.detail}")
            if not check.ok:
                live_failures += 1

    static_failures = len(missing)
    total_failures = static_failures + live_failures

    print_section("Summary")
    print(f"Static failures: {static_failures}")
    print(f"Live failures: {live_failures}")
    print(f"Total failures: {total_failures}")

    return 1 if total_failures else 0


if __name__ == "__main__":
    sys.exit(main())
