"""
Supabase-based Storage Module
Replaces storage.py - uses database instead of JSON files
Privacy-first: Only stores SHA256 hashes, no email content
"""
import hashlib
from typing import Optional
from supabase_client import get_supabase


class SupabaseStorage:
    """
    Storage handler using Supabase database
    Privacy-first: Only SHA256 hashes stored, no email content
    """
    
    def __init__(self, company_id: str):
        self.company_id = company_id
        self._supabase = get_supabase()
    
    def _hash_id(self, message_id: str) -> str:
        """Generate SHA256 hash of message ID"""
        return hashlib.sha256(message_id.encode()).hexdigest()
    
    def is_processed(
        self, 
        message_id: str, 
        thread_id: Optional[str] = None
    ) -> bool:
        """
        Check if email has been processed before
        
        Args:
            message_id: Email message ID
            thread_id: Email thread ID (optional)
            
        Returns:
            True if already processed, False otherwise
        """
        message_hash = self._hash_id(message_id)
        return self._supabase.is_email_processed(self.company_id, message_hash)
    
    def mark_processed(
        self, 
        message_id: str, 
        thread_id: Optional[str] = None
    ) -> None:
        """
        Mark email as processed
        
        Args:
            message_id: Email message ID
            thread_id: Email thread ID (optional)
        """
        message_hash = self._hash_id(message_id)
        thread_hash = self._hash_id(thread_id) if thread_id else None
        
        self._supabase.mark_email_processed(
            self.company_id, 
            message_hash,
            thread_hash
        )
        
        # Increment processed counter in stats
        self._supabase.increment_stat(self.company_id, 'emails_processed')
    
    def increment_drafts_created(self) -> None:
        """Increment draft created counter"""
        self._supabase.increment_stat(self.company_id, 'drafts_created')
    
    def increment_errors(self) -> None:
        """Increment error counter"""
        self._supabase.increment_stat(self.company_id, 'errors')
