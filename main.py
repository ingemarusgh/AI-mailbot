"""Main mailbot application using modular architecture."""
import time
import sys
from config import Config
from mail_client import MailClient
from ai_handler import AIHandler
from storage import Storage


def process_emails(config: Config, mail_client: MailClient, 
                   ai_handler: AIHandler, storage: Storage):
    """Process unread emails and create draft replies.
    
    Args:
        config: Configuration object
        mail_client: Mail client instance
        ai_handler: AI handler instance
        storage: Storage instance
    """
    # Get unread messages
    messages = mail_client.get_unread_messages(max_messages=config.max_messages)
    
    if not messages:
        print('[DEBUG] No unread messages found')
        return
    
    print(f'[INFO] Processing {len(messages)} unread messages')
    
    for msg in messages:
        msg_id = msg['id']
        thread_id = msg['thread_id']
        from_addr = msg['from']
        subject = msg['subject']
        snippet = msg['snippet']
        
        print(f"[DEBUG] Processing message: {msg_id[:20]}...")
        
        # Check if already processed
        if storage.is_processed(msg_id, thread_id):
            print(f"[DEBUG] Already processed, skipping: {msg_id[:20]}...")
            continue
        
        # Generate AI reply
        print(f"[INFO] Generating reply for: {from_addr} - {subject}")
        ai_reply = ai_handler.generate_reply(snippet)
        
        # Create draft (or send if auto_send is enabled)
        subject_prefix = "Re: " if not subject.startswith("Re:") else ""
        success = mail_client.create_draft(
            to=from_addr,
            subject=f"{subject_prefix}{subject}",
            body=ai_reply,
            in_reply_to=msg_id
        )
        
        if success:
            # Mark as processed
            storage.mark_processed(msg_id, thread_id)
            print(f"[SUCCESS] Draft created for: {from_addr}")
        else:
            print(f"[ERROR] Failed to create draft for: {from_addr}")


def main():
    """Main application loop."""
    print("=" * 60)
    print("AI Mailbot - Generell Företagslösning")
    print("=" * 60)
    
    try:
        # Load configuration
        print("[INFO] Loading configuration...")
        config = Config('config.json')
        print(f"[INFO] Company: {config.company_name}")
        print(f"[INFO] Email: {config.company_email}")
        
        # Initialize components
        print("[INFO] Initializing components...")
        mail_client = MailClient(config)
        ai_handler = AIHandler(config)
        storage = Storage(config)
        
        print(f"[INFO] Storage contains {storage.get_count()} processed emails")
        print(f"[INFO] Check interval: {config.check_interval} seconds")
        print("=" * 60)
        
        # Main loop
        iteration = 0
        while True:
            iteration += 1
            print(f"\n[LOOP {iteration}] Checking for new emails...")
            
            try:
                process_emails(config, mail_client, ai_handler, storage)
            except Exception as e:
                print(f"[ERROR] Error during email processing: {e}")
            
            # Disconnect IMAP between checks to avoid timeout
            mail_client.disconnect_imap()
            
            # Wait before next check
            print(f"[INFO] Waiting {config.check_interval} seconds before next check...")
            time.sleep(config.check_interval)
            
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down gracefully...")
        if 'mail_client' in locals():
            mail_client.disconnect_imap()
        sys.exit(0)
        
    except Exception as e:
        print(f"[FATAL] Application error: {e}")
        if 'mail_client' in locals():
            mail_client.disconnect_imap()
        sys.exit(1)


if __name__ == '__main__':
    main()
