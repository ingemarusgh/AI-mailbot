"""Storage module for tracking processed emails."""
import json
import os
from typing import Set, Tuple
from config import Config


class Storage:
    """Handles storage of processed email IDs to prevent duplicates."""
    
    def __init__(self, config: Config):
        """Initialize storage with configuration."""
        self.config = config
        storage_file = config.get('storage', 'file', default='sent_drafts.json')
        
        # Use data directory if it exists (for Docker persistence)
        data_dir = '/app/data' if os.path.exists('/app/data') else 'data'
        if os.path.exists(data_dir) and os.path.isdir(data_dir):
            self.storage_file = os.path.join(data_dir, os.path.basename(storage_file))
        else:
            self.storage_file = storage_file
        
        self.processed_pairs: Set[Tuple[str, str]] = self._load()
    
    def _load(self) -> Set[Tuple[str, str]]:
        """Load processed email pairs from storage file."""
        print(f"[DEBUG] Loading storage from: {os.path.abspath(self.storage_file)}")
        
        if not os.path.exists(self.storage_file):
            print(f"[DEBUG] Creating new storage file: {self.storage_file}")
            self._save(set())
            return set()
        
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                pairs = set(tuple(x) for x in data)
            print(f"[DEBUG] Loaded {len(pairs)} processed email pairs")
            return pairs
        except Exception as e:
            print(f"[ERROR] Failed to load storage: {e}")
            return set()
    
    def _save(self, pairs: Set[Tuple[str, str]]):
        """Save processed email pairs to storage file."""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump([list(x) for x in pairs], f, indent=2)
            print(f"[DEBUG] Saved {len(pairs)} pairs to storage")
        except Exception as e:
            print(f"[ERROR] Failed to save storage: {e}")
    
    def is_processed(self, message_id: str, thread_id: str) -> bool:
        """Check if an email has already been processed.
        
        Args:
            message_id: The email message ID
            thread_id: The email thread ID
            
        Returns:
            True if already processed, False otherwise
        """
        pair = (message_id, thread_id)
        return pair in self.processed_pairs
    
    def mark_processed(self, message_id: str, thread_id: str):
        """Mark an email as processed.
        
        Args:
            message_id: The email message ID
            thread_id: The email thread ID
        """
        pair = (message_id, thread_id)
        if pair not in self.processed_pairs:
            self.processed_pairs.add(pair)
            self._save(self.processed_pairs)
            print(f"[DEBUG] Marked as processed: {message_id[:8]}... / {thread_id[:8]}...")
    
    def get_count(self) -> int:
        """Get the number of processed emails."""
        return len(self.processed_pairs)
