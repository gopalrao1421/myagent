# ULTRON - Advanced Personal AI Assistant

## Project Overview
ULTRON is an advanced personal AI assistant designed to be a futuristic, highly capable companion for Gopal. It combines voice and chat interfaces with natural language understanding in English, Telugu, Telugish, and mixed languages.

## Stage 1: Project Foundation (Current Stage)
This stage establishes the core modular architecture of ULTRON as a Python 3.11 application.

### Components Created:
- **ultron/config.py**: Handles environment variable loading (NVIDIA_API_KEY) and configuration
- **ultron/ai_client.py**: Manages chat requests to NVIDIA API with retry logic and error handling
- **ultron/memory.py**: Provides short-term conversation history and long-term JSON file storage
- **ultron/prompts.py**: Contains ULTRON's system prompt and prompt management
- **ultron/main.py**: Simple terminal chat loop for testing the AI brain
- **tests/**: Unit tests for config and memory modules
- **requirements.txt**: Python dependencies
- **README.md**: This file
- **PROGRESS.md**: Progress tracking (see below)

### Key Features of Stage 1:
- Modular, well-commented code suitable for BTech 2nd year students
- Environment variable-based configuration (no hardcoded secrets)
- Robust error handling with retry logic
- Memory system that never stores passwords, API keys, or tokens
- System prompt that enforces honesty and proper behavior
- Terminal-based interface for testing and development

### How to Run:
1. Install dependencies: `pip install -r requirements.txt`
2. Set your NVIDIA API key: `export NVIDIA_API_KEY=your_key_here` (Linux/Mac) or `set NVIDIA_API_KEY=your_key_here` (Windows)
3. Run the assistant: `python -m ultron.main`

## Stage 2: Planned Enhancements
In Stage 2, we will build upon this foundation to add:

### Voice Interface:
- Wake word detection ("Hey Ultron")
- Speech-to-text and text-to-speech capabilities
- Voice activity detection and noise handling
- Interruptible voice responses

### Chat Interface:
- Graphical chat UI with modern design
- Message history and conversation management
- File and image upload capabilities

### Enhanced Features:
- Tool system for computer control (opening apps, file operations, web search)
- Context sharing between voice and chat modes
- Improved memory system with voice command support
- Error recovery and graceful degradation
- Logging and diagnostics

### Platform Targets:
- Windows desktop application (ULTRON.exe)
- Android mobile application (ULTRON.apk)

## Architecture Overview
ULTRON follows a modular architecture:
- **Config**: Manages settings and environment variables
- **AI Client**: Handles communication with AI APIs
- **Memory**: Manages short-term and long-term memory
- **Prompts**: Controls AI behavior through system prompts
- **Main**: Entry point and conversation loop

Each component is designed to be replaceable and testable, following the development principle of not building everything as one huge file.

---
*ULTRON ONLINE.*