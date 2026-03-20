import os

import resend

from config import SENDER_EMAIL


def _resend_enabled(config):
    return bool(config.get("RESEND_API_KEY") or os.environ.get("RESEND_API_KEY"))


def send_email(config, to_email, subject, text_body, html_body=None):
    """Send an email using Resend API settings from app config.

    Returns True when sent successfully, else False.
    """
    if not to_email:
        return False

    if not _resend_enabled(config):
        return False

    sender = config.get("EMAIL_FROM", SENDER_EMAIL)
    api_key = config.get("RESEND_API_KEY") or os.environ.get("RESEND_API_KEY")
    resend.api_key = api_key

    payload = {
        "from": sender,
        "to": [to_email],
        "subject": subject,
        "text": text_body,
    }
    if html_body:
        payload["html"] = html_body

    try:
        resend.Emails.send(payload)
        return True
    except Exception:
        return False


def test_email(config, to_email="your_email@gmail.com"):
    """Quick send test for Resend integration using the configured sender identity."""
    if not _resend_enabled(config):
        return False

    api_key = config.get("RESEND_API_KEY") or os.environ.get("RESEND_API_KEY")
    resend.api_key = api_key

    try:
        resend.Emails.send(
            {
                "from": config.get("EMAIL_FROM", SENDER_EMAIL),
                "to": [to_email],
                "subject": "Test Email",
                "html": "<p>Working 🚀</p>",
            }
        )
        return True
    except Exception:
        return False
