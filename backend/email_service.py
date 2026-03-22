import os
import logging
import time
import traceback
from email.utils import parseaddr
import json
import ssl
import urllib.error
import urllib.request

from config import SENDER_EMAIL


logger = logging.getLogger(__name__)


RESEND_DEFAULT_FROM = "Gamified Learning <onboarding@resend.dev>"
_PERSONAL_MAILBOX_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "outlook.com",
    "hotmail.com",
    "live.com",
    "icloud.com",
    "aol.com",
    "proton.me",
    "protonmail.com",
}


def _normalize_resend_api_url(config):
    """Return Resend API base URL compatible with the SDK.

    The SDK appends endpoint paths (like /emails) internally, so this value
    must be the API base (https://api.resend.com), not a full endpoint URL.
    """
    configured = (
        config.get("RESEND_API_URL")
        or os.environ.get("RESEND_API_URL")
        or "https://api.resend.com"
    ).strip()

    if configured.endswith("/emails"):
        return configured[: -len("/emails")]

    return configured.rstrip("/")


def _resend_enabled(config):
    api_key = (config.get("RESEND_API_KEY") or os.environ.get("RESEND_API_KEY") or "").strip()
    if not api_key:
        logger.warning("Resend disabled: RESEND_API_KEY is missing or empty.")
    return bool(api_key)


def _resolve_sender(config):
    sender = (
        (config.get("RESEND_FROM_EMAIL") or "").strip()
        or (config.get("EMAIL_FROM") or "").strip()
        or (os.environ.get("RESEND_FROM_EMAIL") or "").strip()
        or (os.environ.get("EMAIL_FROM") or "").strip()
        or SENDER_EMAIL
    )

    _, sender_email = parseaddr(sender)
    sender_email = (sender_email or "").strip().lower()
    sender_domain = sender_email.split("@")[-1] if "@" in sender_email else ""

    if not sender_email:
        logger.warning("Invalid sender format '%s'. Falling back to %s.", sender, RESEND_DEFAULT_FROM)
        return RESEND_DEFAULT_FROM

    # Resend requires verified domains or allowed sandbox sender identities.
    if sender_domain in _PERSONAL_MAILBOX_DOMAINS:
        logger.warning(
            "Sender domain '%s' is a personal mailbox and typically not allowed by Resend. Falling back to %s.",
            sender_domain,
            RESEND_DEFAULT_FROM,
        )
        return RESEND_DEFAULT_FROM

    return sender


def _ssl_verify_enabled(config):
    raw = (
        config.get("RESEND_SSL_VERIFY")
        or os.environ.get("RESEND_SSL_VERIFY")
        or "true"
    )
    return str(raw).strip().lower() not in {"0", "false", "no", "off"}


def _validate_email_env(config):
    api_key = (config.get("RESEND_API_KEY") or os.environ.get("RESEND_API_KEY") or "").strip()
    sender = _resolve_sender(config)

    if not api_key:
        logger.error("Email send blocked: RESEND_API_KEY is missing.")
        return False, "missing_api_key"

    if not sender:
        logger.error("Email send blocked: RESEND_FROM_EMAIL/EMAIL_FROM is missing.")
        return False, "missing_sender"

    return True, "ok"


def _extract_message_id(response):
    if isinstance(response, dict):
        return response.get("id") or response.get("message_id") or response.get("messageId")

    for attr in ("id", "message_id", "messageId"):
        value = getattr(response, attr, None)
        if value:
            return value

    return None


def send_email(config, to_email, subject, text_body, html_body=None):
    """Send an email using Resend API settings from app config.

    Returns True when sent successfully, else False.
    """
    if not to_email:
        return False

    env_ok, _ = _validate_email_env(config)
    if not env_ok:
        return False

    if not _resend_enabled(config):
        return False

    sender = _resolve_sender(config)
    api_key = (config.get("RESEND_API_KEY") or os.environ.get("RESEND_API_KEY") or "").strip()
    api_base = _normalize_resend_api_url(config)
    endpoint = f"{api_base}/emails"
    ssl_verify = _ssl_verify_enabled(config)

    payload = {
        "from": sender,
        "to": [to_email],
        "subject": subject,
        "text": text_body,
    }
    if html_body:
        payload["html"] = html_body

    print("SENDING OTP TO:", to_email)
    print("RESEND PAYLOAD:", payload)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    ssl_context = None
    if not ssl_verify:
        ssl_context = ssl._create_unverified_context()

    for attempt in range(2):
        try:
            request_data = json.dumps(payload).encode("utf-8")
            request = urllib.request.Request(
                endpoint,
                data=request_data,
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(
                request,
                timeout=30,
                context=ssl_context,
            ) as response:
                status_code = response.getcode()
                response_text = response.read().decode("utf-8", errors="replace")

            print("RESEND RESPONSE:", response_text)
            logger.info(
                "Resend HTTP response status=%s body=%s to=%s subject=%s attempt=%s",
                status_code,
                response_text,
                to_email,
                subject,
                attempt + 1,
            )

            if 200 <= status_code < 300:
                try:
                    body = json.loads(response_text) if response_text else {}
                except Exception:
                    body = {}
                message_id = _extract_message_id(body)
                logger.info(
                    "Resend email sent successfully to=%s subject=%s message_id=%s attempt=%s",
                    to_email,
                    subject,
                    message_id or "unknown",
                    attempt + 1,
                )
                return True

            logger.error(
                "Resend non-success status=%s to=%s subject=%s attempt=%s body=%s",
                status_code,
                to_email,
                subject,
                attempt + 1,
                response_text,
            )
        except urllib.error.HTTPError as exc:
            status_code = exc.code
            response_text = exc.read().decode("utf-8", errors="replace")
            print("RESEND RESPONSE:", response_text)
            logger.info(
                "Resend HTTP response status=%s body=%s to=%s subject=%s attempt=%s",
                status_code,
                response_text,
                to_email,
                subject,
                attempt + 1,
            )
            logger.error(
                "Resend non-success status=%s to=%s subject=%s attempt=%s body=%s",
                status_code,
                to_email,
                subject,
                attempt + 1,
                response_text,
            )
        except Exception as exc:
            print("RESEND RESPONSE:", f"exception: {exc}")
            print(traceback.format_exc())
            logger.exception(
                "Resend email send failed to=%s subject=%s attempt=%s error=%s",
                to_email,
                subject,
                attempt + 1,
                exc,
            )
            if attempt == 0:
                time.sleep(1)
                continue

        if attempt == 0:
            time.sleep(1)

    return False


def test_email(config, to_email="your_email@gmail.com"):
    """Quick send test for Resend integration using the configured sender identity."""
    env_ok, _ = _validate_email_env(config)
    if not env_ok:
        return False

    if not _resend_enabled(config):
        return False

    return send_email(
        config,
        to_email,
        "Test Email",
        "Working",
        "<p>Working</p>",
    )
