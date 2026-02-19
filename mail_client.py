"""Mail client module for IMAP/SMTP email handling."""
import imaplib
import smtplib
import email
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from typing import List, Dict, Tuple, Optional, Callable
from config import Config


class MailClient:
    """Handles IMAP/SMTP email operations."""
    
    def __init__(self, config: Config):
        """Initialize mail client with configuration."""
        self.config = config
        self.imap_host = config.get('mail_server', 'imap_host')
        self.imap_port = config.get('mail_server', 'imap_port', default=993)
        self.smtp_host = config.get('mail_server', 'smtp_host')
        self.smtp_port = config.get('mail_server', 'smtp_port', default=587)
        self.username = config.get('mail_server', 'username')
        self.password = config.get('mail_server', 'password')
        self.imap = None
        self.use_ssl = config.get('mail_server', 'use_ssl', default=True)
    
    def connect_imap(self):
        """Connect to IMAP server."""
        try:
            if self.use_ssl:
                self.imap = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            else:
                self.imap = imaplib.IMAP4(self.imap_host, self.imap_port)
            
            self.imap.login(self.username, self.password)
            print(f"[INFO] Connected to IMAP: {self.imap_host}")
            return True
        except Exception as e:
            print(f"[ERROR] IMAP connection failed: {e}")
            return False
    
    def disconnect_imap(self):
        """Disconnect from IMAP server."""
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
                print("[INFO] Disconnected from IMAP")
            except:
                pass
    
    def idle_wait(self, callback: Callable[[], None], timeout: int = 1740) -> None:
        """
        Wait for new emails using IMAP IDLE.
        Calls callback when new emails arrive.
        
        Args:
            callback: Function to call when new emails arrive
            timeout: IDLE timeout in seconds (max 29 minutes per RFC 2177)
        
        Note:
            This is a blocking call. Run in a separate thread for multi-tenant.
        """
        if not self.imap:
            if not self.connect_imap():
                raise ConnectionError("Failed to connect to IMAP")
        
        try:
            # Select INBOX
            self.imap.select('INBOX')
            print("[INFO] Starting IMAP IDLE mode...")
            
            while True:
                # Enter IDLE mode
                tag = self.imap._new_tag().decode()
                self.imap.send(f'{tag} IDLE\r\n'.encode())
                
                # Wait for server acknowledgment
                response = self.imap.readline()
                if b'idling' not in response.lower() and b'+' not in response:
                    print(f"[WARN] IDLE not supported by server, falling back to polling")
                    # Fallback to polling if IDLE not supported
                    time.sleep(60)
                    callback()
                    continue
                
                print("[DEBUG] IDLE mode active, waiting for new emails...")
                
                # Wait for notification or timeout
                start_time = time.time()
                email_detected = False
                
                while time.time() - start_time < timeout:
                    try:
                        # Read with timeout (non-blocking on most systems)
                        response = self.imap.readline()
                        
                        if response:
                            print(f"[DEBUG] IDLE response: {response}")
                            
                            if b'EXISTS' in response or b'RECENT' in response:
                                email_detected = True
                                break
                    except:
                        # No data available, sleep briefly
                        time.sleep(1)
                
                # Exit IDLE mode
                try:
                    self.imap.send(b'DONE\r\n')
                    self.imap.readline()  # Read IDLE completion
                except:
                    pass
                
                if email_detected:
                    print("[INFO] New email detected! Processing...")
                    callback()
                else:
                    print("[DEBUG] IDLE timeout, restarting...")
                    
        except Exception as e:
            print(f"[ERROR] IDLE mode error: {e}")
            raise
    
    def get_unread_messages(self, max_messages: Optional[int] = None) -> List[Dict]:
        """Get unread messages from inbox.
        
        Args:
            max_messages: Maximum number of messages to retrieve
            
        Returns:
            List of message dictionaries with id, thread_id, from, subject, snippet
        """
        if not self.imap:
            if not self.connect_imap():
                return []
        
        try:
            # Select inbox
            self.imap.select('INBOX')
            
            # Search for unseen messages
            status, message_ids = self.imap.search(None, 'UNSEEN')
            
            if status != 'OK':
                print("[ERROR] Failed to search for unread messages")
                return []
            
            # Get message IDs
            id_list = message_ids[0].split()
            
            if not id_list:
                print("[DEBUG] No unread messages found")
                return []
            
            # Limit number of messages
            if max_messages:
                id_list = id_list[-max_messages:]
            
            messages = []
            for msg_id in id_list:
                msg_data = self._fetch_message(msg_id)
                if msg_data:
                    messages.append(msg_data)
            
            print(f"[INFO] Retrieved {len(messages)} unread messages")
            return messages
            
        except Exception as e:
            print(f"[ERROR] Failed to get unread messages: {e}")
            return []
    
    def _fetch_message(self, msg_id: bytes) -> Optional[Dict]:
        """Fetch and parse a single message.
        
        Args:
            msg_id: IMAP message ID
            
        Returns:
            Dictionary with message data
        """
        try:
            # Fetch message
            status, msg_data = self.imap.fetch(msg_id, '(RFC822)')
            
            if status != 'OK':
                return None
            
            # Parse email
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # Extract headers
            subject = self._decode_header(email_message.get('Subject', ''))
            from_addr = self._decode_header(email_message.get('From', ''))
            message_id_header = email_message.get('Message-ID', '')
            in_reply_to = email_message.get('In-Reply-To', '')
            
            # Get message body
            body = self._get_email_body(email_message)
            
            # Create snippet (first 200 chars of body)
            snippet = body[:200] if body else ''
            
            # Use Message-ID as unique identifier
            # Thread ID is the In-Reply-To header if exists, otherwise Message-ID
            thread_id = in_reply_to if in_reply_to else message_id_header
            
            return {
                'id': message_id_header,
                'imap_id': msg_id.decode(),
                'thread_id': thread_id,
                'from': from_addr,
                'subject': subject,
                'snippet': snippet,
                'body': body
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch message {msg_id}: {e}")
            return None
    
    def _decode_header(self, header: str) -> str:
        """Decode email header."""
        if not header:
            return ''
        
        decoded_parts = decode_header(header)
        decoded_str = ''
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_str += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_str += part
        
        return decoded_str
    
    def _get_email_body(self, email_message) -> str:
        """Extract email body from message."""
        body = ''
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                disposition = str(part.get('Content-Disposition', ''))
                
                # Skip attachments
                if 'attachment' in disposition:
                    continue
                
                # Get text/plain parts
                if content_type == 'text/plain':
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode('utf-8', errors='ignore')
                    except:
                        pass
        else:
            try:
                payload = email_message.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
            except:
                pass
        
        return body.strip()
    
    def create_draft(self, to: str, subject: str, body: str, 
                    in_reply_to: Optional[str] = None) -> bool:
        """Create a draft email (or send if auto_send is enabled).
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            in_reply_to: Message-ID to reply to (for threading)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to
            msg['Subject'] = subject
            
            if in_reply_to:
                msg['In-Reply-To'] = in_reply_to
                msg['References'] = in_reply_to
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Check if we should auto-send or save as draft
            auto_send = self.config.get('bot', 'auto_send', default=False)
            
            if auto_send:
                return self._send_email(msg)
            else:
                return self._save_draft(msg)
                
        except Exception as e:
            print(f"[ERROR] Failed to create draft: {e}")
            return False
    
    def _send_email(self, msg: MIMEMultipart) -> bool:
        """Send an email via SMTP."""
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            print(f"[INFO] Email sent to {msg['To']}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to send email: {e}")
            return False
    
    def _save_draft(self, msg: MIMEMultipart) -> bool:
        """Save email as draft in IMAP Drafts folder."""
        if not self.imap:
            if not self.connect_imap():
                return False
        
        try:
            # Get or create Drafts folder
            drafts_folder = self.config.get('mail_server', 'drafts_folder', default='Drafts')
            
            # Append message to Drafts folder
            self.imap.append(
                drafts_folder,
                '\\Draft',
                None,
                msg.as_bytes()
            )
            
            print(f"[INFO] Draft saved for {msg['To']}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to save draft: {e}")
            return False
