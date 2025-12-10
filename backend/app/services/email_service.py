"""
Email service for fetching and sending emails.
Handles POP3/IMAP for receiving and SMTP for sending Santa's replies.
"""
import os
import poplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr
import hashlib
import logging
from typing import List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class IncomingEmail:
    """Represents an incoming email from a child."""
    message_id: str
    from_email: str
    from_name: Optional[str]
    to_email: str  # Recipient address (for extracting family code)
    subject: str
    body_text: str
    body_html: Optional[str]
    received_at: datetime
    raw_message: email.message.Message


class EmailService:
    """Handles email fetching and sending."""
    
    def __init__(self):
        self.pop3_server = settings.pop3_server
        self.pop3_port = settings.pop3_port
        self.pop3_use_ssl = settings.pop3_use_ssl
        self.pop3_username = settings.pop3_username
        self.pop3_password = settings.pop3_password
        
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_use_tls = settings.smtp_use_tls
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.santa_email = settings.santa_email_address
        self.santa_name = settings.santa_display_name
    
    @staticmethod
    def hash_email(email_address: str) -> str:
        """Hash an email address using SHA-256 for privacy."""
        return hashlib.sha256(email_address.lower().strip().encode()).hexdigest()
    
    def _extract_body(self, msg: email.message.Message) -> Tuple[str, Optional[str]]:
        """Extract plain text and HTML body from email message."""
        body_text = ""
        body_html = None
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        text = payload.decode(charset, errors="replace")
                        
                        if content_type == "text/plain":
                            body_text = text
                        elif content_type == "text/html":
                            body_html = text
                except Exception as e:
                    logger.warning(f"Error extracting email part: {e}")
        else:
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or "utf-8"
                    body_text = payload.decode(charset, errors="replace")
            except Exception as e:
                logger.warning(f"Error extracting email body: {e}")
        
        return body_text, body_html
    
    def fetch_new_emails(self, delete_after_fetch: bool = False) -> List[IncomingEmail]:
        """
        Fetch new emails from the POP3 inbox.
        
        Args:
            delete_after_fetch: If True, mark emails for deletion after fetching.
            
        Returns:
            List of IncomingEmail objects.
        """
        if not self.pop3_server or not self.pop3_username:
            logger.warning("POP3 not configured, skipping email fetch")
            return []
        
        emails = []
        
        try:
            # Connect to POP3 server
            if self.pop3_use_ssl:
                pop3 = poplib.POP3_SSL(self.pop3_server, self.pop3_port)
            else:
                pop3 = poplib.POP3(self.pop3_server, self.pop3_port)
            
            pop3.user(self.pop3_username)
            pop3.pass_(self.pop3_password)
            
            # Get message count
            num_messages = len(pop3.list()[1])
            logger.info(f"Found {num_messages} emails in inbox")
            
            for i in range(1, num_messages + 1):
                try:
                    # Fetch message
                    raw_email = b"\n".join(pop3.retr(i)[1])
                    msg = email.message_from_bytes(raw_email)
                    
                    # Extract headers
                    message_id = msg.get("Message-ID", f"unknown-{i}-{datetime.utcnow().timestamp()}")
                    from_header = msg.get("From", "")
                    from_name, from_email_addr = parseaddr(from_header)
                    to_header = msg.get("To", "")
                    _, to_email_addr = parseaddr(to_header)
                    subject = msg.get("Subject", "(No Subject)")
                    
                    # Try to get date
                    date_str = msg.get("Date")
                    if date_str:
                        try:
                            received_at = email.utils.parsedate_to_datetime(date_str)
                        except Exception:
                            received_at = datetime.utcnow()
                    else:
                        received_at = datetime.utcnow()
                    
                    # Extract body
                    body_text, body_html = self._extract_body(msg)
                    
                    incoming = IncomingEmail(
                        message_id=message_id,
                        from_email=from_email_addr,
                        from_name=from_name if from_name else None,
                        to_email=to_email_addr,
                        subject=subject,
                        body_text=body_text,
                        body_html=body_html,
                        received_at=received_at,
                        raw_message=msg
                    )
                    emails.append(incoming)
                    
                    if delete_after_fetch:
                        pop3.dele(i)
                        
                except Exception as e:
                    logger.error(f"Error processing email {i}: {e}")
            
            pop3.quit()
            
        except Exception as e:
            logger.error(f"Error connecting to POP3 server: {e}")
        
        return emails
    
    def send_santa_reply(
        self,
        to_email: str,
        to_name: Optional[str],
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        in_reply_to: Optional[str] = None
    ) -> bool:
        """
        Send an email reply from Santa.
        
        Args:
            to_email: Recipient email address
            to_name: Recipient name (child's name)
            subject: Email subject
            body_text: Plain text body
            body_html: Optional HTML body
            in_reply_to: Optional Message-ID to reply to
            
        Returns:
            True if sent successfully, False otherwise.
        """
        if not self.smtp_server or not self.smtp_username:
            logger.error("SMTP not configured, cannot send email")
            return False
        
        logger.info(f"Attempting to send email to {to_email}")
        logger.info(f"SMTP server: {self.smtp_server}:{self.smtp_port}, SSL: {self.smtp_use_tls}")
        logger.info(f"From: {self.santa_name} <{self.santa_email}>")
        
        try:
            # Create message
            if body_html:
                msg = MIMEMultipart("alternative")
                msg.attach(MIMEText(body_text, "plain", "utf-8"))
                msg.attach(MIMEText(body_html, "html", "utf-8"))
            else:
                msg = MIMEText(body_text, "plain", "utf-8")
            
            msg["From"] = formataddr((self.santa_name, self.santa_email))
            msg["To"] = formataddr((to_name or "", to_email))
            msg["Subject"] = subject
            
            if in_reply_to:
                msg["In-Reply-To"] = in_reply_to
                msg["References"] = in_reply_to
            
            # Send - use SSL for port 465, STARTTLS for port 587
            logger.info("Connecting to SMTP server...")
            if self.smtp_port == 465 or self.smtp_use_tls:
                # SSL connection (port 465)
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30) as server:
                    logger.info(f"Logging in as {self.smtp_username}...")
                    server.login(self.smtp_username, self.smtp_password)
                    logger.info("Sending message...")
                    server.send_message(msg)
            else:
                # STARTTLS connection (port 587)
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                    server.ehlo()
                    logger.info("Starting TLS...")
                    server.starttls()
                    server.ehlo()
                    logger.info(f"Logging in as {self.smtp_username}...")
                    server.login(self.smtp_username, self.smtp_password)
                    logger.info("Sending message...")
                    server.send_message(msg)
            
            logger.info(f"Successfully sent Santa reply to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def send_rich_email(
        self,
        to_email: str,
        to_name: Optional[str],
        subject: str,
        body_text: str,
        body_html: str,
        images_used: List[str],
        in_reply_to: Optional[str] = None
    ) -> bool:
        """
        Send a rich HTML email with embedded CID images.
        
        Args:
            to_email: Recipient email address
            to_name: Recipient name
            subject: Email subject
            body_text: Plain text body (fallback)
            body_html: HTML body with cid: image references
            images_used: List of CID names (e.g., ["santa_sleigh", "elf_letter"])
            in_reply_to: Optional Message-ID to reply to
            
        Returns:
            True if sent successfully, False otherwise.
        """
        from email.mime.image import MIMEImage
        from app.email_templates.image_catalog import get_image_path, get_image_by_cid
        
        if not self.smtp_server or not self.smtp_username:
            logger.error("SMTP not configured, cannot send email")
            return False
        
        logger.info(f"Sending rich email to {to_email} with {len(images_used)} images")
        
        try:
            # Create the root message as 'related' for embedded images
            msg_root = MIMEMultipart("related")
            msg_root["From"] = formataddr((self.santa_name, self.santa_email))
            msg_root["To"] = formataddr((to_name or "", to_email))
            msg_root["Subject"] = subject
            
            if in_reply_to:
                msg_root["In-Reply-To"] = in_reply_to
                msg_root["References"] = in_reply_to
            
            # Create alternative part for text/html
            msg_alternative = MIMEMultipart("alternative")
            msg_root.attach(msg_alternative)
            
            # Attach plain text version
            msg_alternative.attach(MIMEText(body_text, "plain", "utf-8"))
            
            # Wrap HTML in full document structure
            full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A Letter from Santa</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: Georgia, 'Times New Roman', serif;">
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f4f4f4;">
        <tr>
            <td align="center" style="padding: 20px 0;">
                {body_html}
            </td>
        </tr>
    </table>
</body>
</html>"""
            
            msg_alternative.attach(MIMEText(full_html, "html", "utf-8"))
            
            # Attach images
            for cid in images_used:
                image_path = get_image_path(cid)
                if image_path and os.path.exists(image_path):
                    img_info = get_image_by_cid(cid)
                    with open(image_path, "rb") as img_file:
                        img_data = img_file.read()
                        
                        # Determine image type from extension
                        ext = os.path.splitext(image_path)[1].lower()
                        img_type = "png" if ext == ".png" else "jpeg"
                        
                        mime_img = MIMEImage(img_data, _subtype=img_type)
                        mime_img.add_header("Content-ID", f"<{cid}>")
                        mime_img.add_header("Content-Disposition", "inline", filename=img_info.filename if img_info else f"{cid}.png")
                        msg_root.attach(mime_img)
                        logger.debug(f"Attached image: {cid}")
                else:
                    logger.warning(f"Image not found for CID: {cid}")
            
            # Send
            logger.info("Connecting to SMTP server...")
            if self.smtp_port == 465 or self.smtp_use_tls:
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30) as server:
                    logger.info(f"Logging in as {self.smtp_username}...")
                    server.login(self.smtp_username, self.smtp_password)
                    logger.info("Sending rich message...")
                    server.send_message(msg_root)
            else:
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                    server.ehlo()
                    logger.info("Starting TLS...")
                    server.starttls()
                    server.ehlo()
                    logger.info(f"Logging in as {self.smtp_username}...")
                    server.login(self.smtp_username, self.smtp_password)
                    logger.info("Sending rich message...")
                    server.send_message(msg_root)
            
            logger.info(f"Successfully sent rich email to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending rich email to {to_email}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get the email service singleton."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
