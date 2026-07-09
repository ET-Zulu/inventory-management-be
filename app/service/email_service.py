import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

logger = logging.getLogger(__name__)

def send_invitation_email(email: str, role: str, raw_token: str) -> None:
    """
    Sends an invitation email using SMTP configuration.
    Falls back to console logging if SMTP is not configured.
    """
    subject = "You have been invited to the Inventory Management System"
    invite_link = f"{settings.frontend_url}/setup-password?token={raw_token}"
    body = f"""Hello,

You have been invited to join the Inventory Management System as a(n) {role.upper()}.

Please click the link below to set up your password and activate your account:

{invite_link}

This link will expire in 24 hours. If you did not expect this invitation, you can safely ignore this email.

Best regards,
Inventory Management Team
"""

    if not settings.smtp_email or not settings.smtp_password:
        # Fallback to mock logging if no SMTP credentials are provided
        print(f"\n[MOCK EMAIL to {email}]\nSubject: {subject}\n\n{body}")
        logger.info(f"Mock invitation email sent to {email}")
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = settings.smtp_email
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_email, settings.smtp_password)
            server.send_message(msg)
            
        logger.info(f"Invitation email successfully sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {e}")
        raise
