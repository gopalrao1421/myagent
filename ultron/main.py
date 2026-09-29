"""
Main module for ULTRON
Simple terminal chat loop to test the AI brain
"""

import sys
import os
from typing import Optional

# Add the project root to the Python path so we can import ultron modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ultron.config import config
from ultron.ai_client import ai_client
from ultron.memory import memory
from ultron.prompts import Prompts
from ultron.tools import open_app  # Import the app opening function


def print_welcome():
    """Print welcome message"""
    print("=" * 50)
    print(f"{config.assistant_name} - Personal AI Assistant")
    print(f"User: {config.user_name}")
    print("=" * 50)
    print("Type 'exit' or 'quit' to end the conversation")
    print("Type 'clear' to clear conversation history")
    print("Type 'memory' to see what I remember")
    print("-" * 50)


def get_user_input() -> Optional[str]:
    """Get input from user"""
    try:
        user_input = input(f"\n{config.user_name}: ").strip()
        return user_input if user_input else None
    except (EOFError, KeyboardInterrupt):
        return None


def process_user_input(user_input: str) -> bool:
    """
    Process user input and generate response
    Returns False if user wants to exit, True otherwise
    """
    # Handle special commands
    if user_input.lower() in ['exit', 'quit']:
        print(f"\n{config.assistant_name}: Goodbye, {config.user_name}!")
        return False

    if user_input.lower() == 'clear':
        memory.clear_short_term_memory()
        print(f"{config.assistant_name}: Conversation history cleared, {config.user_name}.")
        return True

    if user_input.lower() == 'memory':
        remembered = memory.what_do_you_remember()
        if remembered:
            print(f"{config.assistant_name}: Here's what I remember, {config.user_name}:")
            for key, value in remembered.items():
                print(f"  • {key}: {value}")
        else:
            print(f"{config.assistant_name}: I don't have anything stored in memory yet, {config.user_name}.")
        return True

    # Check for app opening request (only if message starts with "open ")
    app_name = None
    stripped = user_input.strip()
    if stripped.lower().startswith("open "):
        # Take everything after "open " as the app name
        app_name = stripped[5:].strip()  # remove the first 5 characters ("open ") and strip extra spaces

    if app_name is not None:
        # User wants to open an app
        result = open_app(app_name)
        print(f"{config.assistant_name}: {result['message']}")
        # Remember the interaction
        memory.add_short_term_memory("assistant", result['message'])
        return True

    # Add user message to short-term memory
    memory.add_short_term_memory("user", user_input)

    # Get conversation history for context
    recent_messages = memory.get_recent_messages(10)  # Last 10 messages

    # Convert to format expected by AI client
    messages = []
    for msg in recent_messages:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Get AI response
    print(f"\n{config.assistant_name}: ", end="", flush=True)

    # Prepare prompt with system message
    prompted_messages = Prompts.get_conversation_prompt(messages)

    # Get streaming response from AI
    response_chunks = []
    try:
        for chunk in ai_client.chat_completion_stream(prompted_messages):
            print(chunk, end="", flush=True)
            response_chunks.append(chunk)
        response = ''.join(response_chunks)
    except Exception as e:
        # Fallback to non-streaming if streaming fails
        response = ai_client.chat_completion(prompted_messages)
        if response is None:
            raise e  # Re-raise if both fail

    if response:
        # Add assistant response to memory
        memory.add_short_term_memory("assistant", response)
    else:
        # Fallback response if AI fails
        fallback_responses = [
            f"I'm having trouble connecting to my AI services right now, {config.user_name}.",
            f"My AI brain seems to be offline, {config.user_name}. Please try again in a moment.",
            f"I apologize, {config.user_name}, but I'm experiencing technical difficulties."
        ]
        import random
        fallback = random.choice(fallback_responses)
        print(fallback)
        memory.add_short_term_memory("assistant", fallback)

    return True


def main():
    """Main chat loop"""
    print_welcome()

    # Check if API is configured
    if not config.is_configured():
        print(f"⚠️  Warning: NVIDIA API key not found in environment variables.")
        print(f"   Please set NVIDIA_API_KEY to use the AI features.")
        print(f"   The system will run in limited mode.\n")

    # Main conversation loop
    while True:
        user_input = get_user_input()
        if user_input is None:  # EOF or Ctrl+C
            print(f"\n\n{config.assistant_name}: Goodbye, {config.user_name}!")
            break

        if not process_user_input(user_input):
            break


if __name__ == "__main__":
    main()