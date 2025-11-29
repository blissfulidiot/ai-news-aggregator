"""SMTP email service for sending emails via Gmail SMTP with app password"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv

# Load .env file
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"
if not env_file.exists():
    env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file if env_file.exists() else None)


class SMTPService:
    """
    Service for sending emails via Gmail SMTP using app password.
    
    Requires:
    - Gmail account with 2-factor authentication enabled
    - App password generated from Google Account settings
    - SMTP credentials in .env file
    """
    
    # Gmail SMTP settings
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    
    def __init__(self, smtp_host: Optional[str] = None, smtp_port: Optional[int] = None,
                 smtp_username: Optional[str] = None, smtp_password: Optional[str] = None,
                 from_email: Optional[str] = None):
        """
        Initialize SMTP service
        
        Args:
            smtp_host: SMTP server host (defaults to Gmail: smtp.gmail.com)
            smtp_port: SMTP server port (defaults to 587)
            smtp_username: SMTP username (Gmail address, defaults to SMTP_USERNAME env var)
            smtp_password: SMTP password (Gmail app password, defaults to SMTP_PASSWORD env var)
            from_email: From email address (defaults to smtp_username)
        """
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", self.SMTP_SERVER)
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", self.SMTP_PORT))
        self.smtp_username = smtp_username or os.getenv("SMTP_USERNAME")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        self.from_email = from_email or os.getenv("FROM_EMAIL") or self.smtp_username
        
        if not self.smtp_username or not self.smtp_password:
            raise ValueError(
                "SMTP credentials required. Set SMTP_USERNAME and SMTP_PASSWORD "
                "environment variables or pass them to the constructor."
            )
    
    def create_message(self, to: str, subject: str, body_text: str,
                      body_html: Optional[str] = None) -> MIMEMultipart:
        """
        Create a multipart email message
        
        Args:
            to: Recipient email address
            subject: Email subject
            body_text: Plain text body
            body_html: Optional HTML body
            
        Returns:
            MIMEMultipart message object
        """
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = to
        
        # Add plain text part
        text_part = MIMEText(body_text, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # Add HTML part if provided
        if body_html:
            html_part = MIMEText(body_html, 'html', 'utf-8')
            msg.attach(html_part)
        
        return msg
    
    def send_email(self, to: str, subject: str, body_text: str,
                   body_html: Optional[str] = None) -> bool:
        """
        Send an email via SMTP
        
        Args:
            to: Recipient email address
            subject: Email subject
            body_text: Plain text body
            body_html: Optional HTML body
            
        Returns:
            True if email sent successfully
            
        Raises:
            smtplib.SMTPException: If email sending fails
        """
        try:
            # Create message
            msg = self.create_message(to, subject, body_text, body_html)
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()  # Enable encryption
            server.login(self.smtp_username, self.smtp_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.from_email, to, text)
            server.quit()
            
            return True
            
        except smtplib.SMTPException as e:
            raise Exception(f"Failed to send email: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error sending email: {e}")
    
    def send_bulk_emails(self, recipients: List[str], subject: str, body_text: str,
                         body_html: Optional[str] = None) -> dict:
        """
        Send emails to multiple recipients
        
        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            body_text: Plain text body
            body_html: Optional HTML body
            
        Returns:
            Dictionary with success count and failed recipients
        """
        results = {
            "success_count": 0,
            "failed_count": 0,
            "failed_recipients": []
        }
        
        for recipient in recipients:
            try:
                self.send_email(recipient, subject, body_text, body_html)
                results["success_count"] += 1
            except Exception as e:
                results["failed_count"] += 1
                results["failed_recipients"].append({
                    "email": recipient,
                    "error": str(e)
                })
        
        return results


def send_email_via_smtp(to: str, subject: str, body_text: str,
                        body_html: Optional[str] = None) -> bool:
    """
    Convenience function to send email via SMTP
    
    Args:
        to: Recipient email address
        subject: Email subject
        body_text: Plain text body
        body_html: Optional HTML body
        
    Returns:
        True if email sent successfully
    """
    service = SMTPService()
    return service.send_email(to, subject, body_text, body_html)

