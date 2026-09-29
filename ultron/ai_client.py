"""
AI Client module for ULTRON
Handles chat requests to NVIDIA API with retry logic and error handling
"""

import json
import time
import logging
import os
import sys
from typing import Dict, List, Optional, Any
import requests

# Add the project root to the Python path so we can import ultron modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ultron.config import config

# Set up logging for technical details (only goes to log file, not shown to user)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ultron.log'),
        logging.NullHandler()  # Don't show logs to user by default
    ]
)
logger = logging.getLogger(__name__)

class AIClient:
    """Handles communication with the NVIDIA AI API"""

    def __init__(self):
        self.config = config
        self.session = requests.Session()
        self.max_retries = 2  # One retry on timeout or error as specified
        self.timeout = 30  # seconds

    def chat_completion(self, messages: List[Dict[str, str]],
                       temperature: float = 0.7,
                       max_tokens: int = 1024) -> Optional[str]:
        """
        Send chat completion request to NVIDIA API

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response or None if failed
        """
        if not self.config.is_configured():
            logger.error("NVIDIA API key not configured")
            return None

        url = f"{self.config.api_base_url}/chat/completions"
        headers = self.config.get_api_headers()

        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
            "reasoning_effort": "none"
        }

        # Try initial request plus one retry
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"Sending AI request (attempt {attempt + 1})")
                response = self.session.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()

                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    logger.debug("AI request successful")
                    return content.strip()
                else:
                    logger.error("Unexpected response format from AI API")
                    return None

            except requests.exceptions.Timeout:
                logger.warning(f"AI request timeout (attempt {attempt + 1})")
                if attempt < self.max_retries:
                    # Exponential backoff: delay = 1 * 2^attempt seconds
                    delay = 2 ** attempt
                    time.sleep(delay)
                    continue
                else:
                    logger.error("AI request failed after retries due to timeout")
                    return None

            except requests.exceptions.RequestException as e:
                logger.warning(f"AI request error (attempt {attempt + 1}): {str(e)}")
                if attempt < self.max_retries:
                    # Exponential backoff: delay = 1 * 2^attempt seconds
                    delay = 2 ** attempt
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"AI request failed after retries: {str(e)}")
                    return None

            except (KeyError, json.JSONDecodeError) as e:
                logger.error(f"Failed to parse AI response: {str(e)}")
                return None

        return None

    def chat_completion_stream(self, messages: List[Dict[str, str]],
                              temperature: float = 0.7,
                              max_tokens: int = 1024):
        """
        Send streaming chat completion request to NVIDIA API

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Yields:
            String chunks of the generated response
        """
        if not self.config.is_configured():
            logger.error("NVIDIA API key not configured")
            return

        url = f"{self.config.api_base_url}/chat/completions"
        headers = self.config.get_api_headers()

        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
            "reasoning_effort": "none"
        }

        # Try initial request plus one retry
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"Sending AI streaming request (attempt {attempt + 1})")
                response = self.session.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                    stream=True  # Important for streaming
                )
                response.raise_for_status()

                # Process streaming response
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]  # Remove 'data: ' prefix
                            if data.strip() == '[DONE]':
                                break
                            try:
                                chunk = json.loads(data)
                                if 'choices' in chunk and len(chunk['choices']) > 0:
                                    delta = chunk['choices'][0].get('delta', {})
                                    content = delta.get('content')
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                # Skip invalid JSON lines
                                continue

                logger.debug("AI streaming request successful")
                return  # Success, exit retry loop

            except requests.exceptions.Timeout:
                logger.warning(f"AI request timeout (attempt {attempt + 1})")
                if attempt < self.max_retries:
                    # Exponential backoff: delay = 1 * 2^attempt seconds
                    delay = 2 ** attempt
                    time.sleep(delay)
                    continue
                else:
                    logger.error("AI request failed after retries due to timeout")
                    return None

            except requests.exceptions.RequestException as e:
                logger.warning(f"AI request error (attempt {attempt + 1}): {str(e)}")
                if attempt < self.max_retries:
                    # Exponential backoff: delay = 1 * 2^attempt seconds
                    delay = 2 ** attempt
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"AI request failed after retries: {str(e)}")
                    return None

            except (KeyError, json.JSONDecodeError) as e:
                logger.error(f"Failed to parse AI response: {str(e)}")
                return None

    def test_connection(self) -> bool:
        """
        Test the connection to the AI API

        Returns:
            True if connection is successful, False otherwise
        """
        test_messages = [
            {"role": "user", "content": "Hello"}
        ]
        response = self.chat_completion(test_messages, max_tokens=10)
        return response is not None

# Global AI client instance
ai_client = AIClient()