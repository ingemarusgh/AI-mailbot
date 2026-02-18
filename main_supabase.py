"""
Multi-tenant AI Mailbot - Railway Deployment
Processes emails for all active companies from Supabase
"""
import time
import sys
import logging
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
                success = mail_client.create_draft(
                    to=from_addr,
                    subject=f"{subject_prefix}{subject}",
                    body=ai_reply,
                    in_reply_to=msg_id,
                    auto_send=config.auto_send
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
                logger.error(f"Error processing message {msg_id[:20]}: {e}")
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


def main():
    """Main application loop - processes all active companies"""
    logger.info("=" * 70)
    logger.info("AI Mailbot - Multi-Tenant Railway Deployment")
    logger.info("=" * 70)
    
    try:
        # Initialize Supabase connection
        logger.info("Connecting to Supabase...")
        supabase = get_supabase()
        logger.info("✓ Supabase connected")
        
        iteration = 0
        
        while True:
            iteration += 1
            logger.info(f"\n{'=' * 70}")
            logger.info(f"LOOP {iteration} - Checking all active companies")
            logger.info(f"{'=' * 70}")
            
            try:
                # Get all active companies
                companies = supabase.get_active_companies()
                logger.info(f"Found {len(companies)} active companies")
                
                if not companies:
                    logger.warning("No active companies found in database")
                else:
                    # Process each company
                    success_count = 0
                    error_count = 0
                    
                    for company in companies:
                        company_id = company['id']
                        company_name = company['name']
                        
                        logger.info(f"\n--- Processing: {company_name} ---")
                        
                        if process_company_emails(company_id):
                            success_count += 1
                        else:
                            error_count += 1
                    
                    logger.info(f"\n✓ Processed {success_count} companies successfully")
                    if error_count > 0:
                        logger.warning(f"✗ {error_count} companies had errors")
                
                # Get check interval
                check_interval = get_check_interval(companies)
                logger.info(f"\nWaiting {check_interval} seconds before next check...")
                time.sleep(check_interval)
                
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
