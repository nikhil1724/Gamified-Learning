"""
Email service for sending verification and notification emails via SMTP.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        smtp_username: str,
        smtp_password: str,
        from_email: str,
        from_name: str = "Gamified Learning Platform",
        use_tls: bool = True,
        smtp_timeout_seconds: int = 8,
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.from_name = from_name
        self.use_tls = use_tls
        self.smtp_timeout_seconds = smtp_timeout_seconds

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Send an email via SMTP."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            if text_content:
                msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(
                self.smtp_server,
                self.smtp_port,
                timeout=self.smtp_timeout_seconds,
            ) as server:
                server.ehlo()
                if self.use_tls:
                    server.starttls()
                    server.ehlo()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

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
        subject = "Verify Your Account"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #111827;">
            <h2>Verify Your Account</h2>
            <p>Hello {user_name},</p>
            <p>Your OTP for account verification is:</p>
            <p style="font-size: 32px; font-weight: bold; letter-spacing: 6px;">{otp_code}</p>
            <p>This OTP is valid for {expiry_minutes} minutes.</p>
            <p>If you did not request this OTP, please ignore this email.</p>
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
