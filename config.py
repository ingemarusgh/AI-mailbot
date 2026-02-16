"""Configuration module for mailbot."""
import json
import os
from typing import Dict, Any


class Config:
    """Handles configuration loading and access."""
    
    def __init__(self, config_file: str = "config.json"):
        """Load configuration from file."""
        self.config_file = config_file
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"Config file '{self.config_file}' not found. "
                "Please create it from config.json.example"
            )
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _validate_config(self):
        """Validate required configuration fields."""
        required_sections = ['company', 'mail_server', 'ai', 'bot', 'storage']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required config section: {section}")
        
        # Validate company section
        if 'name' not in self.config['company']:
            raise ValueError("Missing company.name in config")
        
        # Validate mail_server section
        mail_config = self.config['mail_server']
        if mail_config.get('type') == 'imap':
            required = ['imap_host', 'imap_port', 'smtp_host', 'smtp_port', 'username', 'password']
            for field in required:
                if field not in mail_config:
                    raise ValueError(f"Missing mail_server.{field} in config")
    
    def get(self, *keys, default=None):
        """Get a configuration value by path.
        
        Example:
            config.get('company', 'name')
            config.get('ai', 'model', default='gpt-3.5-turbo')
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    @property
    def company_name(self) -> str:
        """Get company name."""
        return self.get('company', 'name')
    
    @property
    def company_email(self) -> str:
        """Get company email."""
        return self.get('company', 'email')
    
    @property
    def signature(self) -> str:
        """Get email signature."""
        return self.get('company', 'signature', default='')
    
    @property
    def ai_prompt_template(self) -> str:
        """Get AI prompt template."""
        return self.get('ai', 'prompt_template')
    
    @property
    def check_interval(self) -> int:
        """Get check interval in seconds."""
        return self.get('bot', 'check_interval', default=60)
    
    @property
    def max_messages(self) -> int:
        """Get max messages per check."""
        return self.get('bot', 'max_messages_per_check', default=5)
