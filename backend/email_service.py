"""
Email service for sending verification and notification emails.
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.from_name = from_name
        self.use_tls = use_tls

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send an email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML body of the email
            text_content: Plain text body (optional fallback)

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            # Add plain text version if provided
            if text_content:
                part1 = MIMEText(text_content, "plain")
                msg.attach(part1)

            # Add HTML version
            part2 = MIMEText(html_content, "html")
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_verification_email(
        self, to_email: str, user_name: str, verification_link: str
    ) -> bool:
        """
        Send email verification email to user.

        Args:
            to_email: User's email address
            user_name: User's display name
            verification_link: Full verification URL with token

        Returns:
            True if sent successfully, False otherwise
        """
        subject = "Verify Your Email - Gamified Learning Platform"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 40px;
                    margin: 20px 0;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #2563eb;
                }}
                .button {{
                    display: inline-block;
                    padding: 14px 28px;
                    background: #2563eb;
                    color: #ffffff !important;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e2e8f0;
                    color: #64748b;
                    font-size: 14px;
                }}
                .link {{
                    color: #2563eb;
                    word-break: break-all;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎮 Gamified Learning</div>
                </div>
                
                <h2>Welcome, {user_name}!</h2>
                
                <p>Thank you for registering with Gamified Learning Platform. We're excited to have you join our community of learners!</p>
                
                <p>To complete your registration and start learning, please verify your email address by clicking the button below:</p>
                
                <center>
                    <a href="{verification_link}" class="button">Verify Email Address</a>
                </center>
                
                <p>Or copy and paste this link into your browser:</p>
                <p class="link">{verification_link}</p>
                
                <p><strong>This link will expire in 24 hours.</strong></p>
                
                <p>If you didn't create an account with us, you can safely ignore this email.</p>
                
                <div class="footer">
                    <p>Best regards,<br>The Gamified Learning Team</p>
                    <p style="font-size: 12px; color: #94a3b8;">
                        This is an automated email. Please do not reply.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Welcome, {user_name}!

        Thank you for registering with Gamified Learning Platform.

        To complete your registration, please verify your email address by clicking the link below:

        {verification_link}

        This link will expire in 24 hours.

        If you didn't create an account with us, you can safely ignore this email.

        Best regards,
        The Gamified Learning Team
        """

        return self.send_email(to_email, subject, html_content, text_content)

    def send_verification_otp_email(
        self, to_email: str, user_name: str, otp_code: str, expiry_minutes: int = 5
    ) -> bool:
        """
        Send OTP verification email to user.

        Args:
            to_email: User's email address
            user_name: User's display name
            otp_code: 6-digit OTP code

        Returns:
            True if sent successfully, False otherwise
        """
        subject = "Email Verification OTP"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 40px;
                    margin: 20px 0;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #2563eb;
                    text-align: center;
                    margin-bottom: 24px;
                }}
                .otp-box {{
                    background: #eff6ff;
                    border: 1px dashed #3b82f6;
                    border-radius: 8px;
                    text-align: center;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .otp-code {{
                    font-size: 36px;
                    letter-spacing: 8px;
                    font-weight: 700;
                    color: #1d4ed8;
                    margin: 8px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e2e8f0;
                    color: #64748b;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">Gamified Learning</div>
                <h2>Welcome, {user_name}!</h2>
                <p>Use the OTP below to verify your account:</p>
                <div class="otp-box">
                    <p style="margin: 0; color: #475569;">Your verification OTP</p>
                    <div class="otp-code">{otp_code}</div>
                </div>
                <p><strong>Your OTP code is {otp_code}. It expires in {expiry_minutes} minutes.</strong></p>
                <p>If you didn't create an account with us, you can safely ignore this email.</p>
                <div class="footer">
                    <p>Best regards,<br>The Gamified Learning Team</p>
                    <p style="font-size: 12px; color: #94a3b8;">This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Welcome, {user_name}!

        Your OTP code is {otp_code}. It expires in {expiry_minutes} minutes.

        If you didn't create an account with us, you can safely ignore this email.

        Best regards,
        The Gamified Learning Team
        """

        return self.send_email(to_email, subject, html_content, text_content)

    def send_password_reset_email(
        self, to_email: str, user_name: str, reset_link: str
    ) -> bool:
        """
        Send password reset email to user.

        Args:
            to_email: User's email address
            user_name: User's display name
            reset_link: Full password reset URL with token

        Returns:
            True if sent successfully, False otherwise
        """
        subject = "Reset Your Password - Gamified Learning Platform"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 40px;
                    margin: 20px 0;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #2563eb;
                }}
                .button {{
                    display: inline-block;
                    padding: 14px 28px;
                    background: #2563eb;
                    color: #ffffff !important;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e2e8f0;
                    color: #64748b;
                    font-size: 14px;
                }}
                .warning {{
                    background: #fef3c7;
                    border-left: 4px solid #f59e0b;
                    padding: 12px;
                    margin: 20px 0;
                }}
                .link {{
                    color: #2563eb;
                    word-break: break-all;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎮 Gamified Learning</div>
                </div>
                
                <h2>Password Reset Request</h2>
                
                <p>Hi {user_name},</p>
                
                <p>We received a request to reset your password. Click the button below to choose a new password:</p>
                
                <center>
                    <a href="{reset_link}" class="button">Reset Password</a>
                </center>
                
                <p>Or copy and paste this link into your browser:</p>
                <p class="link">{reset_link}</p>
                
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong> This link will expire in 1 hour for your security.
                </div>
                
                <p>If you didn't request a password reset, please ignore this email. Your password will remain unchanged.</p>
                
                <div class="footer">
                    <p>Best regards,<br>The Gamified Learning Team</p>
                    <p style="font-size: 12px; color: #94a3b8;">
                        This is an automated email. Please do not reply.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Password Reset Request

        Hi {user_name},

        We received a request to reset your password. Click the link below to choose a new password:

        {reset_link}

        This link will expire in 1 hour for your security.

        If you didn't request a password reset, please ignore this email. Your password will remain unchanged.

        Best regards,
        The Gamified Learning Team
        """

        return self.send_email(to_email, subject, html_content, text_content)
