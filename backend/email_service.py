import os
import logging
import time

import resend

from config import SENDER_EMAIL


logger = logging.getLogger(__name__)


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
    return bool(config.get("RESEND_API_KEY") or os.environ.get("RESEND_API_KEY"))


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

    if not _resend_enabled(config):
        return False

    sender = SENDER_EMAIL
    api_key = config.get("RESEND_API_KEY") or os.environ.get("RESEND_API_KEY")
    resend.api_key = api_key
    resend.api_url = _normalize_resend_api_url(config)

    payload = {
        "from": sender,
        "to": [to_email],
        "subject": subject,
        "text": text_body,
    }
    if html_body:
        payload["html"] = html_body

    for attempt in range(2):
        try:
            response = resend.Emails.send(payload)
            message_id = _extract_message_id(response)
            logger.info(
                "Resend email sent successfully to=%s subject=%s message_id=%s attempt=%s",
                to_email,
                subject,
                message_id or "unknown",
                attempt + 1,
            )
            return True
        except Exception as exc:
            logger.exception(
                "Resend email send failed to=%s subject=%s attempt=%s error=%s",
                to_email,
                subject,
                attempt + 1,
                exc,
            )
            if attempt == 0:
                time.sleep(1)

    return False


def test_email(config, to_email="your_email@gmail.com"):
    """Quick send test for Resend integration using the configured sender identity."""
    if not _resend_enabled(config):
        return False

    api_key = config.get("RESEND_API_KEY") or os.environ.get("RESEND_API_KEY")
    resend.api_key = api_key
    resend.api_url = _normalize_resend_api_url(config)

    try:
        response = resend.Emails.send(
            {
                "from": SENDER_EMAIL,
                "to": [to_email],
                "subject": "Test Email",
                "html": "<p>Working 🚀</p>",
            }
        )
        logger.info(
            "Resend test email sent to=%s message_id=%s",
            to_email,
            _extract_message_id(response) or "unknown",
        )
        return True
    except Exception as exc:
        logger.exception("Resend test email failed: %s", exc)
        return False
