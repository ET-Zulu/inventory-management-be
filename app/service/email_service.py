import logging

logger = logging.getLogger(__name__)

def send_invitation_email(email: str, role: str, raw_token: str) -> None:
    """
    Mock email service that logs the email content to the console.
    In a production environment, this would integrate with a real SMTP provider
    like SendGrid, AWS SES, or standard smtplib.
    """
    email_content = f"""
    ==================================================
    📧 MOCK EMAIL DISPATCH
    ==================================================
    To: {email}
    Subject: You have been invited to the Inventory Management System
    
    Hello,
    
    You have been invited to join the Inventory Management System as a(n) {role.upper()}.
    
    Please use the following invite token to set up your account:
    {raw_token}
    
    This token will expire in 24 hours.
    ==================================================
    """
    # Print it out cleanly to the server console
    print(email_content)
    # Also log it
    logger.info(f"Invitation email sent to {email} for role {role}")
