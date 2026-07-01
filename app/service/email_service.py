import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

logger = logging.getLogger(__name__)


def _send_email(to: str, subject: str, body: str) -> None:
    """Internal helper — sends via SMTP or falls back to console logging."""
    if not settings.smtp_email or not settings.smtp_password:
        print(f"\n[MOCK EMAIL to {to}]\nSubject: {subject}\n\n{body}")
        logger.info(f"Mock email sent to {to}")
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = settings.smtp_email
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_email, settings.smtp_password)
            server.send_message(msg)

        logger.info(f"Email successfully sent to {to}")
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        raise


def send_invitation_email(email: str, role: str, raw_token: str) -> None:
    """Sends an invitation email with an account setup token."""
    subject = "You have been invited to the Inventory Management System"
    body = f"""Hello,

You have been invited to join the Inventory Management System as a(n) {role.upper()}.

Please use the following invite token to set up your account:
{raw_token}

This token will expire in 24 hours.

Best regards,
Inventory Management Team
"""
    _send_email(email, subject, body)


def send_password_reset_email(email: str, raw_token: str) -> None:
    """Sends a password reset email with a time-limited reset token."""
    subject = "Password Reset Request – Inventory Management System"
    body = f"""Hello,

We received a request to reset the password for your account.

Use the following token to reset your password:
{raw_token}

This token will expire in 1 hour. If you did not request a password reset, you can safely ignore this email.

Best regards,
Inventory Management Team
"""
    _send_email(email, subject, body)
