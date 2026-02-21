"""
OAuth2 Handler for Azure AD / Microsoft 365
Handles token refresh and IMAP/SMTP authentication
"""
import os
import time
import base64
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import requests
from supabase_client import get_supabase

logger = logging.getLogger(__name__)


class OAuth2Handler:
    """Handles OAuth2 token management for Microsoft 365"""
    
    def __init__(self):
        """Initialize OAuth2 handler with Azure AD credentials"""
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        self.tenant_id = os.getenv('AZURE_TENANT_ID', 'common')
        
        if not self.client_id or not self.client_secret:
            logger.warning("Azure OAuth2 credentials not configured")
        
        # Microsoft OAuth2 endpoints
        self.token_url = f'https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token'
        
        # OAuth2 scopes for IMAP/SMTP
        self.scopes = [
            'https://outlook.office365.com/IMAP.AccessAsUser.All',
            'https://outlook.office365.com/SMTP.Send',
            'offline_access'
        ]
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: OAuth2 refresh token
            
        Returns:
            Dict with new tokens or None if failed
        """
        try:
            logger.info("Refreshing OAuth2 access token...")
            
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token',
                'scope': ' '.join(self.scopes)
            }
            
            response = requests.post(self.token_url, data=data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Calculate expiry time
                expires_in = token_data.get('expires_in', 3600)
                expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                
                result = {
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data.get('refresh_token', refresh_token),
                    'expires_at': expires_at.isoformat()
                }
                
                logger.info("✓ Access token refreshed successfully")
                return result
            else:
                logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None
    
    def get_valid_access_token(self, company_id: str) -> Optional[str]:
        """
        Get valid access token for company, refresh if needed
        
        Args:
            company_id: Company UUID
            
        Returns:
            Valid access token or None
        """
        try:
            supabase = get_supabase()
            
            # Get mail config with OAuth tokens
            mail_config = supabase.get_mail_config(company_id)
            
            if not mail_config:
                logger.error(f"No mail config found for company {company_id}")
                return None
            
            # Check if using OAuth2
            if mail_config.get('oauth_provider') != 'azure':
                logger.debug("Company not using OAuth2, skipping token check")
                return None
            
            access_token = mail_config.get('access_token')
            refresh_token = mail_config.get('refresh_token')
            expires_at_str = mail_config.get('token_expires_at')
            
            if not access_token or not refresh_token:
                logger.error("Missing OAuth2 tokens in mail config")
                return None
            
            # Check if token is still valid (with 5 minute buffer)
            if expires_at_str:
                expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
                buffer_time = datetime.utcnow() + timedelta(minutes=5)
                
                if expires_at > buffer_time:
                    logger.debug("Access token still valid")
                    return access_token
            
            # Token expired or about to expire - refresh it
            logger.info("Access token expired, refreshing...")
            new_tokens = self.refresh_access_token(refresh_token)
            
            if not new_tokens:
                logger.error("Failed to refresh access token")
                return None
            
            # Update tokens in database
            try:
                response = supabase._client.table('mail_configs')\
                    .update({
                        'access_token': new_tokens['access_token'],
                        'refresh_token': new_tokens['refresh_token'],
                        'token_expires_at': new_tokens['expires_at']
                    })\
                    .eq('company_id', company_id)\
                    .execute()
                
                logger.info("✓ Tokens updated in database")
                return new_tokens['access_token']
                
            except Exception as e:
                logger.error(f"Failed to update tokens in database: {e}")
                # Return new token anyway (will work for this session)
                return new_tokens['access_token']
                
        except Exception as e:
            logger.error(f"Error getting valid access token: {e}")
            return None
    
    def generate_oauth2_string(self, user_email: str, access_token: str) -> str:
        """
        Generate OAuth2 authentication string for IMAP/SMTP
        
        Args:
            user_email: User's email address
            access_token: Valid OAuth2 access token
            
        Returns:
            Base64-encoded OAuth2 auth string
        """
        auth_string = f'user={user_email}\x01auth=Bearer {access_token}\x01\x01'
        return base64.b64encode(auth_string.encode()).decode()
    
    def test_token(self, access_token: str) -> bool:
        """
        Test if access token is valid by calling Microsoft Graph
        
        Args:
            access_token: Access token to test
            
        Returns:
            True if valid, False otherwise
        """
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(
                'https://graph.microsoft.com/v1.0/me',
                headers=headers,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


# Singleton instance
_oauth_handler = None

def get_oauth_handler() -> OAuth2Handler:
    """Get OAuth2 handler singleton"""
    global _oauth_handler
    if _oauth_handler is None:
        _oauth_handler = OAuth2Handler()
    return _oauth_handler
