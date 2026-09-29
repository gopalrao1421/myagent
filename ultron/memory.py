"""
Memory module for ULTRON
Handles short-term conversation history and long-term memory storage
Never stores passwords, API keys or tokens as per requirements
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

class Memory:
    """Memory management for ULTRON"""

    def __init__(self, long_term_file: str = "ultron_long_term_memory.json"):
        # Short-term memory: current conversation history
        self.short_term_memory: List[Dict[str, str]] = []

        # Long-term memory: persistent storage
        self.long_term_file = long_term_file
        self.long_term_memory: Dict[str, Any] = self._load_long_term_memory()

    def _load_long_term_memory(self) -> Dict[str, Any]:
        """Load long-term memory from JSON file"""
        if os.path.exists(self.long_term_file):
            try:
                with open(self.long_term_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Ensure we don't load sensitive data by checking keys
                    return self._filter_sensitive_data(data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load long-term memory: {e}")
                return {}
        return {}

    def _save_long_term_memory(self) -> None:
        """Save long-term memory to JSON file"""
        try:
            # Filter out any sensitive data before saving
            filtered_data = self._filter_sensitive_data(self.long_term_memory)
            with open(self.long_term_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save long-term memory: {e}")

    def _filter_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from memory storage
        Never store passwords, API keys or tokens
        """
        sensitive_keys = {
            'password', 'pass', 'pwd', 'secret', 'key', 'token',
            'api_key', 'apikey', 'auth', 'credential', 'private'
        }

        filtered = {}
        for key, value in data.items():
            # Check if key contains sensitive terms
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                continue  # Skip sensitive data

            # Recursively filter nested dictionaries
            if isinstance(value, dict):
                filtered[key] = self._filter_sensitive_data(value)
            elif isinstance(value, list):
                filtered[key] = [
                    self._filter_sensitive_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                filtered[key] = value

        return filtered

    # Short-term memory methods
    def add_short_term_memory(self, role: str, content: str) -> None:
        """Add a message to short-term memory"""
        self.short_term_memory.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_short_term_memory(self) -> List[Dict[str, str]]:
        """Get copy of short-term memory"""
        return self.short_term_memory.copy()

    def clear_short_term_memory(self) -> None:
        """Clear short-term memory"""
        self.short_term_memory.clear()

    def get_recent_messages(self, count: int = 10) -> List[Dict[str, str]]:
        """Get recent messages from short-term memory"""
        return self.short_term_memory[-count:] if self.short_term_memory else []

    # Long-term memory methods
    def remember(self, key: str, value: Any) -> None:
        """Store information in long-term memory"""
        # Filter sensitive data before storing
        if isinstance(value, dict):
            value = self._filter_sensitive_data(value)
        elif isinstance(value, list):
            value = [
                self._filter_sensitive_data(item) if isinstance(item, dict) else item
                for item in value
            ]

        self.long_term_memory[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        self._save_long_term_memory()

    def recall(self, key: str) -> Optional[Any]:
        """Recall information from long-term memory"""
        if key in self.long_term_memory:
            return self.long_term_memory[key]["value"]
        return None

    def forget(self, key: str) -> bool:
        """Remove information from long-term memory"""
        if key in self.long_term_memory:
            del self.long_term_memory[key]
            self._save_long_term_memory()
            return True
        return False

    def what_do_you_remember(self) -> Dict[str, Any]:
        """Get all non-sensitive long-term memory"""
        # Return only the values, not the metadata
        result = {}
        for key, data in self.long_term_memory.items():
            result[key] = data["value"]
        return self._filter_sensitive_data(result)

# Global memory instance
memory = Memory()