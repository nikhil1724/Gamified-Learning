import datetime
import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:5000/api"


def post(path, payload, timeout=30):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url=f"{BASE}{path}",
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def main() -> int:
    stamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    email = f"otpcheck_{stamp}@example.com"
    password = "Test@12345"

    register_payload = {
        "name": "OTP Check User",
        "email": email,
        "password": password,
    }
    status, text = post("/register", register_payload)
    print("REGISTER_STATUS", status)
    print("REGISTER_BODY", text)
    if status >= 400:
        return 1

    register_json = json.loads(text)
    otp = register_json.get("otp_preview")
    if not otp:
        print("NO_OTP_PREVIEW")
        return 1

    status, text = post("/verify-otp", {"email": email, "otp": str(otp)})
    print("VERIFY_STATUS", status)
    print("VERIFY_BODY", text)
    if status >= 400:
        return 1

    status, text = post("/login", {"email": email, "password": password})
    print("LOGIN_STATUS", status)
    print("LOGIN_BODY", text)
    if status >= 400:
        return 1

    print("FLOW_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
