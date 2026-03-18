"""
Email service for sending verification and notification emails via Resend.
"""

import logging
from typing import Optional

import resend

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via Resend API."""

    def __init__(
        self,
        api_key: str,
        from_email: str,
        from_name: str = "Gamified Learning Platform",
    ):
        self.api_key = api_key
        self.from_email = from_email
        self.from_name = from_name

    @property
    def _from_field(self) -> str:
        return f"{self.from_name} <{self.from_email}>"

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Send an email via Resend API."""
        if not self.api_key or not self.from_email:
            logger.error("Resend is not configured (missing RESEND_API_KEY or RESEND_FROM_EMAIL)")
            return False

        try:
            resend.api_key = self.api_key

            payload = {
                "from": self._from_field,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            }
            if text_content:
                payload["text"] = text_content

            resend.Emails.send(payload)

            logger.info("Email sent successfully to %s", to_email)
            return True
        except Exception as exc:
            logger.error("Failed to send email to %s: %s", to_email, str(exc))
            return False

    def send_verification_email(
        self, to_email: str, user_name: str, verification_link: str
    ) -> bool:
        """Send legacy email-link verification message."""
        subject = "Verify Your Email - Gamified Learning Platform"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #111827;">
            <h2>Welcome, {user_name}!</h2>
            <p>Please verify your email by clicking the link below:</p>
            <p><a href="{verification_link}">{verification_link}</a></p>
            <p>This link expires in 24 hours.</p>
        </body>
        </html>
        """

        text_content = (
            f"Welcome, {user_name}!\n\n"
            f"Please verify your email: {verification_link}\n"
            "This link expires in 24 hours."
        )

        return self.send_email(to_email, subject, html_content, text_content)

    def send_verification_otp_email(
        self, to_email: str, user_name: str, otp_code: str, expiry_minutes: int = 5
    ) -> bool:
        """Send OTP verification email to user."""
        subject = "Verify your account"

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <body style="margin:0;padding:24px;background:#f3f4f6;font-family:Arial,sans-serif;color:#111827;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                <tr>
                    <td align="center">
                        <table role="presentation" width="560" cellspacing="0" cellpadding="0" style="max-width:560px;background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #e5e7eb;">
                            <tr>
                                <td style="padding:28px 24px 10px 24px;">
                                    <h2 style="margin:0 0 8px 0;font-size:24px;color:#111827;">Verify your account</h2>
                                    <p style="margin:0 0 16px 0;font-size:15px;color:#374151;">Hello {user_name}, your OTP is:</p>
                                    <p style="margin:0 0 18px 0;font-size:34px;font-weight:700;letter-spacing:8px;color:#1d4ed8;">{otp_code}</p>
                                    <p style="margin:0 0 6px 0;font-size:14px;color:#374151;">This OTP is valid for {expiry_minutes} minutes.</p>
                                    <p style="margin:0;font-size:13px;color:#6b7280;">If you did not request this OTP, you can safely ignore this email.</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        text_content = (
            f"Hello {user_name},\n\n"
            f"Your OTP is {otp_code}.\n"
            f"It is valid for {expiry_minutes} minutes.\n\n"
            "If you did not request this OTP, please ignore this email."
        )

        return self.send_email(to_email, subject, html_content, text_content)

    def send_password_reset_email(
        self, to_email: str, user_name: str, reset_link: str
    ) -> bool:
        """Send password reset email to user."""
        subject = "Reset Your Password - Gamified Learning Platform"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #111827;">
            <h2>Password Reset Request</h2>
            <p>Hello {user_name},</p>
            <p>Use the link below to reset your password:</p>
            <p><a href="{reset_link}">{reset_link}</a></p>
            <p>This link expires in 1 hour.</p>
        </body>
        </html>
        """

        text_content = (
            f"Hello {user_name},\n\n"
            f"Reset your password with this link: {reset_link}\n"
            "This link expires in 1 hour."
        )

        return self.send_email(to_email, subject, html_content, text_content)
