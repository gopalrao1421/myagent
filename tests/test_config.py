"""
Tests for the config module
"""

import os
import sys
import unittest
from unittest.mock import patch

# Add the project root to the path so we can import ultron modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ultron.config import Config

class TestConfig(unittest.TestCase):
    """Test cases for Config class"""

    def setUp(self):
        """Set up test fixtures"""
        pass

    def test_config_initialization(self):
        """Test that config initializes with default values"""
        config = Config()
        self.assertEqual(config.model_name, "nvidia/nemotron-3-super-120b-a12b")
        self.assertEqual(config.assistant_name, "ULTRON")
        self.assertEqual(config.user_name, "Gopal")
        self.assertEqual(config.api_base_url, "https://integrate.api.nvidia.com/v1")

    @patch.dict(os.environ, {'NVIDIA_API_KEY': 'test_key_123'})
    def test_config_with_api_key(self):
        """Test config loads API key from environment"""
        config = Config()
        self.assertEqual(config.nvidia_api_key, 'test_key_123')
        self.assertTrue(config.is_configured())

    @patch.dict(os.environ, {}, clear=True)
    def test_config_without_api_key(self):
        """Test config handles missing API key gracefully"""
        config = Config()
        self.assertIsNone(config.nvidia_api_key)
        self.assertFalse(config.is_configured())

    def test_get_api_headers(self):
        """Test API headers generation"""
        # Test with no API key
        config = Config()
        config.nvidia_api_key = None
        headers = config.get_api_headers()
        self.assertEqual(headers, {})

        # Test with API key
        config.nvidia_api_key = 'test_key'
        headers = config.get_api_headers()
        self.assertIn('Authorization', headers)
        self.assertEqual(headers['Authorization'], 'Bearer test_key')
        self.assertEqual(headers['Content-Type'], 'application/json')

if __name__ == '__main__':
    unittest.main()