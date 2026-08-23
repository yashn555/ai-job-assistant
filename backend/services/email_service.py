import os
import re
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Tuple, Dict, Any, Optional
from dotenv import load_dotenv

from backend.services.resume_service import get_resume_path

load_dotenv()
logger = logging.getLogger(__name__)

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


def validate_email_send_request(
    recipient_email: Optional[str],
    company_name: Optional[str],
    role: Optional[str],
    subject: Optional[str],
    body: Optional[str],
    resume_filename: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Validates all required fields before attempting to send an application email.
    """
    if not recipient_email or not recipient_email.strip():
        return False, "Cannot send application: recipient email was not detected or is empty."

    recipient = recipient_email.strip()
    if not re.match(EMAIL_REGEX, recipient):
        return False, f"Cannot send application: invalid recipient email format '{recipient}'."

    if not company_name or not company_name.strip():
        return False, "Cannot send application: missing company name."

    if not role or not role.strip():
        return False, "Cannot send application: missing job role."

    if not subject or not subject.strip():
        return False, "Cannot send application: missing email subject."

    if not body or not body.strip():
        return False, "Cannot send application: missing email body."

    return True, ""


def send_application_email(
    recipient_email: str,
    subject: str,
    body: str,
    resume_filename: Optional[str] = None,
    smtp_settings: Optional[Dict[str, Any]] = None
) -> Tuple[bool, str]:
    """
    Sends the email with optional attached resume using Python smtplib.
    Uses ONLY user-configured SMTP credentials without env fallback.
    """
    if not smtp_settings:
        return False, "SMTP configuration missing for current user."

    smtp_host = smtp_settings.get("smtp_host") or "smtp.gmail.com"
    smtp_port = int(smtp_settings.get("smtp_port") or 587)
    smtp_user = smtp_settings.get("smtp_username")
    smtp_pass = smtp_settings.get("smtp_password")
    sender_email = smtp_settings.get("sender_email") or smtp_user

    if not smtp_user or not smtp_pass:
        return False, "Gmail Email or App Password is not configured for your user account. Please update App Settings."

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach email body text
        msg.attach(MIMEText(body, 'plain'))

        # Attach Resume File if specified and exists
        if resume_filename:
            resume_path = get_resume_path(resume_filename)
            if resume_path and os.path.exists(resume_path):
                attach_name = os.path.basename(resume_path)
                with open(resume_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=attach_name)
                    part['Content-Disposition'] = f'attachment; filename="{attach_name}"'
                    msg.attach(part)
            else:
                logger.warning(f"Resume file '{resume_filename}' not found on server. Sending email without attachment.")

        logger.info(f"Connecting to SMTP server {smtp_host}:{smtp_port} for user {smtp_user}...")

        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
            server.ehlo()
            server.starttls()
            server.ehlo()

        server.login(smtp_user, smtp_pass)
        server.sendmail(sender_email, [recipient_email], msg.as_string())
        server.quit()

        logger.info(f"Email successfully sent from {sender_email} to {recipient_email}")
        return True, "Email sent successfully."

    except smtplib.SMTPAuthenticationError:
        return False, "SMTP Authentication Failed: Please verify your Email and 16-character Gmail App Password (generated at myaccount.google.com/apppasswords)."
    except smtplib.SMTPConnectError:
        return False, f"SMTP Connection Failed: Could not connect to {smtp_host}:{smtp_port}."
    except Exception as e:
        logger.error(f"Error sending email via smtplib: {e}")
        return False, f"Failed to send email: {str(e)}"
