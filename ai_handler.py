"""AI handler module for generating email replies."""
import openai
import os
from dotenv import load_dotenv
from config import Config


class AIHandler:
    """Handles AI-powered email reply generation."""
    
    def __init__(self, config: Config):
        """Initialize AI handler with configuration."""
        self.config = config
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    def generate_reply(self, email_snippet: str) -> str:
        """Generate an AI reply for an email.
        
        Args:
            email_snippet: The content of the email to reply to
            
        Returns:
            Generated reply text
        """
        prompt = self._build_prompt(email_snippet)
        
        try:
            response = openai.chat.completions.create(
                model=self.config.get('ai', 'model', default='gpt-3.5-turbo'),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config.get('ai', 'max_tokens', default=200)
            )
            reply = response.choices[0].message.content.strip()
            
            # Add signature if configured
            if self.config.signature:
                reply = f"{reply}\n\n{self.config.signature}"
            
            return reply
            
        except Exception as e:
            print(f"[ERROR] AI reply generation failed: {e}")
            # Fallback reply
            fallback = "Hej! Detta är ett automatiskt svar på ditt mail."
            if self.config.signature:
                fallback = f"{fallback}\n\n{self.config.signature}"
            return fallback
    
    def _build_prompt(self, email_snippet: str) -> str:
        """Build the AI prompt from template and email content.
        
        Args:
            email_snippet: The email content
            
        Returns:
            Formatted prompt
        """
        template = self.config.ai_prompt_template
        
        # Replace template variables
        prompt = template.format(
            company_name=self.config.company_name
        )
        
        # Add email content
        prompt = f"{prompt}\n\nMail: {email_snippet}\n\nSvar:"
        
        return prompt
