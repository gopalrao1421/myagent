"""
Tests for the memory module
"""

import os
import sys
import unittest
import tempfile
import json
from unittest.mock import patch

# Add the project root to the path so we can import ultron modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ultron.memory import Memory

class TestMemory(unittest.TestCase):
    """Test cases for Memory class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary file for long-term memory
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.memory = Memory(long_term_file=self.temp_file.name)

    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_memory_initialization(self):
        """Test that memory initializes correctly"""
        self.assertEqual(self.memory.short_term_memory, [])
        self.assertIsInstance(self.memory.long_term_memory, dict)

    def test_add_short_term_memory(self):
        """Test adding to short-term memory"""
        self.memory.add_short_term_memory("user", "Hello")
        self.memory.add_short_term_memory("assistant", "Hi there!")

        self.assertEqual(len(self.memory.short_term_memory), 2)
        self.assertEqual(self.memory.short_term_memory[0]["role"], "user")
        self.assertEqual(self.memory.short_term_memory[0]["content"], "Hello")
        self.assertEqual(self.memory.short_term_memory[1]["role"], "assistant")
        self.assertEqual(self.memory.short_term_memory[1]["content"], "Hi there!")

    def test_get_short_term_memory(self):
        """Test getting short-term memory"""
        self.memory.add_short_term_memory("user", "Test")
        copied_memory = self.memory.get_short_term_memory()

        # Should be a copy, not the same object
        self.assertEqual(copied_memory, self.memory.short_term_memory)
        self.assertIsNot(copied_memory, self.memory.short_term_memory)

    def test_clear_short_term_memory(self):
        """Test clearing short-term memory"""
        self.memory.add_short_term_memory("user", "Test")
        self.assertEqual(len(self.memory.short_term_memory), 1)

        self.memory.clear_short_term_memory()
        self.assertEqual(len(self.memory.short_term_memory), 0)

    def test_get_recent_messages(self):
        """Test getting recent messages"""
        # Add multiple messages
        for i in range(5):
            self.memory.add_short_term_memory("user", f"Message {i}")

        recent = self.memory.get_recent_messages(3)
        self.assertEqual(len(recent), 3)
        self.assertEqual(recent[-1]["content"], "Message 4")  # Most recent

    def test_remember_and_recall(self):
        """Test storing and recalling from long-term memory"""
        self.memory.remember("name", "Gopal")
        self.memory.remember("preference", {"language": "Telugu"})

        # Test recall
        name = self.memory.recall("name")
        self.assertEqual(name, "Gopal")

        preference = self.memory.recall("preference")
        self.assertEqual(preference, {"language": "Telugu"})

        # Test recalling non-existent key
        non_existent = self.memory.recall("nonexistent")
        self.assertIsNone(non_existent)

    def test_forget(self):
        """Test forgetting information"""
        self.memory.remember("test_key", "test_value")
        self.assertTrue(self.memory.recall("test_key") == "test_value")

        result = self.memory.forget("test_key")
        self.assertTrue(result)
        self.assertIsNone(self.memory.recall("test_key"))

        # Try to forget non-existent key
        result = self.memory.forget("nonexistent")
        self.assertFalse(result)

    def test_what_do_you_remember(self):
        """Test getting all remembered information"""
        self.memory.remember("name", "Gopal")
        self.memory.remember("language_preference", "Telugu")
        self.memory.remember("api_key", "should_be_filtered")  # This should be filtered

        remembered = self.memory.what_do_you_remember()

        # Should contain non-sensitive data
        self.assertIn("name", remembered)
        self.assertIn("language_preference", remembered)
        self.assertEqual(remembered["name"], "Gopal")
        self.assertEqual(remembered["language_preference"], "Telugu")

        # Should NOT contain sensitive data
        self.assertNotIn("api_key", remembered)

    def test_sensitive_data_filtering(self):
        """Test that sensitive data is filtered from memory"""
        # Test various sensitive key names
        sensitive_data = [
            ("password", "secret123"),
            ("api_key", "key123"),
            ("token", "token123"),
            ("secret_key", "secret456"),
            ("auth_token", "auth789")
        ]

        for key, value in sensitive_data:
            self.memory.remember(key, value)
            # Should not be stored in long-term memory
            recalled = self.memory.recall(key)
            self.assertIsNone(recalled, f"Sensitive data {key} should not be stored")

        # Test non-sensitive data is stored
        self.memory.remember("user_name", "Gopal")
        self.assertEqual(self.memory.recall("user_name"), "Gopal")

    def test_long_term_memory_persistence(self):
        """Test that long-term memory persists to file"""
        # Store some data
        self.memory.remember("persistent_key", "persistent_value")
        self.memory.remember("number", 42)

        # Create new memory instance with same file
        memory2 = Memory(long_term_file=self.temp_file.name)

        # Should be able to recall the data
        self.assertEqual(memory2.recall("persistent_key"), "persistent_value")
        self.assertEqual(memory2.recall("number"), 42)

if __name__ == '__main__':
    unittest.main()