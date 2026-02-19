"""
Multi-tenant AI Mailbot - Railway Deployment (IDLE Mode)
Uses IMAP IDLE for real-time email processing with minimal CPU usage
"""
import time
import sys
import logging
import threading
from typing import List, Dict, Any
from supabase_client import get_supabase
from supabase_config import CompanyConfig
from supabase_storage import SupabaseStorage
from mail_client import MailClient
from ai_handler import AIHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def process_company_emails(company_id: str) -> bool:
    """
    Process emails for a single company
    
    Args:
        company_id: Company UUID from Supabase
        
    Returns:
        True if successful, False if error
    """
    try:
        # Load company configuration from Supabase
        config = CompanyConfig(company_id)
        logger.info(f"Processing company: {config.company_name} ({config.company_email})")
        
        # Initialize components
        storage = SupabaseStorage(company_id)
        mail_client = MailClient(config)
        ai_handler = AIHandler(config)
        
        # Get unread messages
        messages = mail_client.get_unread_messages(
            max_messages=config.max_messages_per_check
        )
        
        if not messages:
            logger.debug(f"No unread messages for {config.company_name}")
            mail_client.disconnect_imap()
            return True
        
        logger.info(f"Found {len(messages)} unread messages for {config.company_name}")
        
        # Process each message
        for msg in messages:
            try:
                msg_id = msg['id']
                thread_id = msg['thread_id']
                from_addr = msg['from']
                subject = msg['subject']
                snippet = msg['snippet']
                
                # Check if already processed (duplicate prevention)
                if storage.is_processed(msg_id, thread_id):
                    logger.debug(f"Already processed, skipping: {msg_id[:20]}...")
                    continue
                
                # Generate AI reply
                logger.info(f"Generating reply for: {from_addr} - {subject}")
                ai_reply = ai_handler.generate_reply(snippet)
                
                # Create draft (or send if auto_send is enabled)
                subject_prefix = "Re: " if not subject.startswith("Re:") else ""
                
                # Create draft or send email based on config
                if config.auto_send:
                    # TODO: Implement auto-send via SMTP
                    success = mail_client.create_draft(
                        to=from_addr,
                        subject=f"{subject_prefix}{subject}",
                        body=ai_reply,
                        in_reply_to=msg_id
                    )
                else:
                    success = mail_client.create_draft(
                        to=from_addr,
                        subject=f"{subject_prefix}{subject}",
                        body=ai_reply,
                        in_reply_to=msg_id
                    )
                
                if success:
                    # Mark as processed and increment stats
                    storage.mark_processed(msg_id, thread_id)
                    storage.increment_drafts_created()
                    
                    action = "sent" if config.auto_send else "draft created"
                    logger.info(f"✓ Email {action} for: {from_addr}")
                else:
                    logger.error(f"✗ Failed to create draft for: {from_addr}")
                    storage.increment_errors()
                    
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                storage.increment_errors()
                continue
        
        # Cleanup
        mail_client.disconnect_imap()
        return True
        
    except Exception as e:
        logger.error(f"Error processing company {company_id}: {e}")
        try:
            # Try to increment error counter
            storage = SupabaseStorage(company_id)
            storage.increment_errors()
        except:
            pass
        return False


def get_check_interval(companies: List[Dict[str, Any]]) -> int:
    """
    Get check interval - use minimum from all companies
    Default to 300 seconds (5 minutes) if no configs found
    """
    supabase = get_supabase()
    intervals = []
    
    for company in companies:
        try:
            ai_config = supabase.get_ai_config(company['id'])
            if ai_config and 'check_interval' in ai_config:
                intervals.append(ai_config['check_interval'])
        except:
            continue
    
    return min(intervals) if intervals else 300


def company_idle_worker(company_id: str, company_name: str):
    """
    IDLE worker for a single company.
    Runs in its own thread and processes emails in real-time.
    
    Args:
        company_id: Company UUID
        company_name: Company name (for logging)
    """
    logger.info(f"[{company_name}] Starting IDLE worker thread")
    
    def process_emails():
        """Callback function when new emails arrive"""
        try:
            logger.info(f"[{company_name}] New email(s) detected!")
            success = process_company_emails(company_id)
            
            if success:
                logger.info(f"[{company_name}] ✓ Emails processed")
            else:
                logger.error(f"[{company_name}] ✗ Error processing emails")
                
        except Exception as e:
            logger.error(f"[{company_name}] Error in process callback: {e}")
    
    try:
        # Load configuration
        config = CompanyConfig(company_id)
        mail_client = MailClient(config)
        
        # Start IDLE mode (blocking call)
        logger.info(f"[{company_name}] Entering IDLE mode...")
        mail_client.idle_wait(callback=process_emails, timeout=1740)
        
    except Exception as e:
        logger.error(f"[{company_name}] IDLE worker crashed: {e}")
        logger.info(f"[{company_name}] Restarting in 60 seconds...")
        time.sleep(60)
        # Restart worker
        company_idle_worker(company_id, company_name)


def main():
    """Main application - spawns IDLE worker threads for each company"""
    logger.info("=" * 70)
    logger.info("AI Mailbot - Multi-Tenant IDLE Mode")
    logger.info("=" * 70)
def main():
    """Main application - spawns IDLE worker threads for each company"""
    logger.info("=" * 70)
    logger.info("AI Mailbot - Multi-Tenant IDLE Mode")
    logger.info("=" * 70)
    
    try:
        # Initialize Supabase connection
        logger.info("Connecting to Supabase...")
        supabase = get_supabase()
        logger.info("✓ Supabase connected")
        
        # Track active threads
        active_threads = {}
        
        while True:
            try:
                # Get all active companies
                companies = supabase.get_active_companies()
                logger.info(f"\nFound {len(companies)} active companies")
                
                if not companies:
                    logger.warning("No active companies found. Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                
                # Start/update threads for each company
                current_company_ids = {c['id'] for c in companies}
                
                # Start new threads for new companies
                for company in companies:
                    company_id = company['id']
                    company_name = company['name']
                    
                    # Check if thread already exists and is alive
                    if company_id in active_threads:
                        thread = active_threads[company_id]
                        if thread.is_alive():
                            continue  # Thread already running
                        else:
                            logger.warning(f"[{company_name}] Thread died, restarting...")
                    
                    # Start new thread
                    logger.info(f"[{company_name}] Starting IDLE thread...")
                    thread = threading.Thread(
                        target=company_idle_worker,
                        args=(company_id, company_name),
                        name=f"IDLE-{company_name}",
                        daemon=True
                    )
                    thread.start()
                    active_threads[company_id] = thread
                
                # Remove threads for inactive companies
                inactive_ids = set(active_threads.keys()) - current_company_ids
                for company_id in inactive_ids:
                    logger.info(f"Company {company_id} is no longer active")
                    del active_threads[company_id]
                
                # Check thread health every 5 minutes
                logger.info(f"\n✓ {len(active_threads)} IDLE threads running")
                logger.info("Threads will process emails in real-time when they arrive")
                logger.info("Checking for new companies in 300 seconds...\n")
                
                time.sleep(300)  # Check for new companies every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                logger.info("Waiting 60 seconds before retry...")
                time.sleep(60)
    
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 70)
        logger.info("Shutting down gracefully...")
        logger.info("=" * 70)
        sys.exit(0)
    
    except Exception as e:
        logger.critical(f"Fatal application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
