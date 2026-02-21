"""
Supabase-based Configuration Module
Replaces config.py - loads configuration from Supabase database
"""
from typing import Dict, Any
from supabase_client import get_supabase


class CompanyConfig:
    """Configuration for a single company loaded from Supabase"""
    
    def __init__(self, company_id: str):
        self.company_id = company_id
        self._supabase = get_supabase()
        self._load_config()
    
    def _load_config(self):
        """Load all configuration from Supabase"""
        # Get company info
        self._company = self._supabase.get_company(self.company_id)
        if not self._company:
            raise ValueError(f"Company {self.company_id} not found")
        
        # Get mail config
        self._mail_config = self._supabase.get_mail_config(self.company_id)
        if not self._mail_config:
            raise ValueError(f"Mail config not found for company {self.company_id}")
        
        # Get AI config
        self._ai_config = self._supabase.get_ai_config(self.company_id)
        if not self._ai_config:
            raise ValueError(f"AI config not found for company {self.company_id}")
    
    # ===== Company Properties =====
    
    @property
    def company_name(self) -> str:
        return self._company['name']
    
    @property
    def company_email(self) -> str:
        return self._company['email']
    
    @property
    def status(self) -> str:
        return self._company['status']
    
    # ===== Mail Config Properties =====
    
    @property
    def imap_host(self) -> str:
        return self._mail_config['imap_host']
    
    @property
    def imap_port(self) -> int:
        return self._mail_config['imap_port']
    
    @property
    def imap_use_ssl(self) -> bool:
        return self._mail_config['imap_use_ssl']
    
    @property
    def smtp_host(self) -> str:
        return self._mail_config['smtp_host']
    
    @property
    def smtp_port(self) -> int:
        return self._mail_config['smtp_port']
    
    @property
    def smtp_use_tls(self) -> bool:
        return self._mail_config['smtp_use_tls']
    
    @property
    def email_address(self) -> str:
        return self._mail_config['email_address']
    
    @property
    def email_password(self) -> str:
        return self._mail_config.get('email_password', '')
    
    @property
    def oauth_provider(self) -> str:
        """OAuth2 provider (azure, google) or None for password auth"""
        return self._mail_config.get('oauth_provider')
    
    @property
    def access_token(self) -> str:
        """OAuth2 access token"""
        return self._mail_config.get('access_token', '')
    
    @property
    def refresh_token(self) -> str:
        """OAuth2 refresh token"""
        return self._mail_config.get('refresh_token', '')
    
    @property
    def token_expires_at(self) -> str:
        """OAuth2 token expiry timestamp"""
        return self._mail_config.get('token_expires_at')
    
    @property
    def inbox_folder(self) -> str:
        return self._mail_config['inbox_folder']
    
    # ===== AI Config Properties =====
    
    @property
    def ai_provider(self) -> str:
        return self._ai_config['provider']
    
    @property
    def ai_model(self) -> str:
        return self._ai_config['model']
    
    @property
    def prompt_template(self) -> str:
        return self._ai_config['prompt_template']
    
    @property
    def signature(self) -> str:
        return self._ai_config['signature']
    
    @property
    def check_interval(self) -> int:
        return self._ai_config['check_interval']
    
    @property
    def max_messages_per_check(self) -> int:
        return self._ai_config['max_messages_per_check']
    
    @property
    def create_drafts(self) -> bool:
        return self._ai_config['create_drafts']
    
    @property
    def auto_send(self) -> bool:
        return self._ai_config['auto_send']
    
    def to_dict(self) -> Dict[str, Any]:
        """Get all config as dictionary (for logging/debugging)"""
        return {
            'company': {
                'id': self.company_id,
                'name': self.company_name,
                'email': self.company_email,
                'status': self.status
            },
            'mail_server': {
                'imap_host': self.imap_host,
                'imap_port': self.imap_port,
                'smtp_host': self.smtp_host,
                'smtp_port': self.smtp_port,
                'email_address': self.email_address,
                'oauth_provider': self.oauth_provider
            },
            'ai': {
                'provider': self.ai_provider,
                'model': self.ai_model,
                'prompt_template': self.prompt_template,
                'signature': self.signature
            },
            'bot': {
                'check_interval': self.check_interval,
                'max_messages_per_check': self.max_messages_per_check,
                'create_drafts': self.create_drafts,
                'auto_send': self.auto_send
            }
        }
    
    def get(self, section: str, key: str, default=None):
        """
        Get configuration value (for backwards compatibility with Config class)
        
        Args:
            section: Config section (mail_server, ai, bot)
            key: Config key
            default: Default value if not found
            
        Returns:
            Config value or default
        """
        mapping = {
            'mail_server': {
                'imap_host': self.imap_host,
                'imap_port': self.imap_port,
                'smtp_host': self.smtp_host,
                'smtp_port': self.smtp_port,
                'username': self.email_address,
                'password': self.email_password,
                'use_ssl': self.imap_use_ssl,
                'oauth_provider': self.oauth_provider,
                'drafts_folder': 'Drafts'
            },
            'ai': {
                'provider': self.ai_provider,
                'model': self.ai_model,
                'prompt_template': self.prompt_template,
                'signature': self.signature
            },
            'bot': {
                'check_interval': self.check_interval,
                'max_messages_per_check': self.max_messages_per_check,
                'create_drafts': self.create_drafts,
                'auto_send': self.auto_send
            }
        }
        
        if section in mapping and key in mapping[section]:
            return mapping[section][key]
        return default
