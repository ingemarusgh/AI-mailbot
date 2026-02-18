"""
Supabase Client Module
Handles database connection and operations
"""
import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class SupabaseClient:
    """Singleton Supabase client for database operations"""
    
    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            url = os.getenv("SUPABASE_URL")
            # Backend uses service_role key to bypass RLS
            key = os.getenv("SUPABASE_SERVICE_KEY")
            
            if not url or not key:
                raise ValueError(
                    "Missing Supabase credentials. Set SUPABASE_URL and "
                    "SUPABASE_SERVICE_KEY in .env file"
                )
            
            self._client = create_client(url, key)
    
    @property
    def client(self) -> Client:
        """Get Supabase client instance"""
        return self._client
    
    # ===== Company Operations =====
    
    def get_active_companies(self) -> List[Dict[str, Any]]:
        """Get all active companies for processing"""
        response = self._client.table('companies')\
            .select('*')\
            .eq('status', 'active')\
            .execute()
        
        return response.data
    
    def get_company(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get single company by ID"""
        response = self._client.table('companies')\
            .select('*')\
            .eq('id', company_id)\
            .single()\
            .execute()
        
        return response.data
    
    # ===== Mail Config Operations =====
    
    def get_mail_config(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get mail configuration for a company"""
        response = self._client.table('mail_configs')\
            .select('*')\
            .eq('company_id', company_id)\
            .single()\
            .execute()
        
        return response.data
    
    # ===== AI Config Operations =====
    
    def get_ai_config(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get AI configuration for a company"""
        response = self._client.table('ai_configs')\
            .select('*')\
            .eq('company_id', company_id)\
            .single()\
            .execute()
        
        return response.data
    
    # ===== Processed Emails Operations =====
    
    def is_email_processed(self, company_id: str, message_hash: str) -> bool:
        """Check if email has already been processed (duplicate prevention)"""
        response = self._client.table('processed_emails')\
            .select('id')\
            .eq('company_id', company_id)\
            .eq('message_hash', message_hash)\
            .execute()
        
        return len(response.data) > 0
    
    def mark_email_processed(
        self, 
        company_id: str, 
        message_hash: str,
        thread_hash: Optional[str] = None
    ) -> None:
        """Mark email as processed"""
        self._client.table('processed_emails')\
            .insert({
                'company_id': company_id,
                'message_hash': message_hash,
                'thread_hash': thread_hash
            })\
            .execute()
    
    # ===== Email Stats Operations =====
    
    def increment_stat(
        self, 
        company_id: str, 
        stat_type: str,
        date: str = None
    ) -> None:
        """
        Increment a statistic counter for today
        stat_type: 'emails_processed', 'drafts_created', or 'errors'
        """
        from datetime import date as dt_date
        
        if date is None:
            date = dt_date.today().isoformat()
        
        # Try to update existing record
        response = self._client.table('email_stats')\
            .select('*')\
            .eq('company_id', company_id)\
            .eq('date', date)\
            .execute()
        
        if response.data:
            # Update existing
            current = response.data[0]
            self._client.table('email_stats')\
                .update({stat_type: current[stat_type] + 1})\
                .eq('id', current['id'])\
                .execute()
        else:
            # Insert new
            self._client.table('email_stats')\
                .insert({
                    'company_id': company_id,
                    'date': date,
                    stat_type: 1
                })\
                .execute()
    
    def get_stats(
        self, 
        company_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get email statistics for last N days"""
        from datetime import date, timedelta
        
        start_date = (date.today() - timedelta(days=days)).isoformat()
        
        response = self._client.table('email_stats')\
            .select('*')\
            .eq('company_id', company_id)\
            .gte('date', start_date)\
            .order('date', desc=True)\
            .execute()
        
        return response.data


# Global instance
_supabase = None


def get_supabase() -> SupabaseClient:
    """Get global Supabase client instance"""
    global _supabase
    if _supabase is None:
        _supabase = SupabaseClient()
    return _supabase
