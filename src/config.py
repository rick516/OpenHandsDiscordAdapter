"""
Configuration module for OpenHands Discord Integration.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Discord Bot Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!oh ")

# OpenHands Configuration
OPENHANDS_CLI_PATH = os.getenv("OPENHANDS_CLI_PATH", "openhands.core.cli")
OPENHANDS_WORKDIR = os.getenv("OPENHANDS_WORKDIR", "./openhands_workspace")

# Ensure workspace directory exists
WORKSPACE_PATH = Path(OPENHANDS_WORKDIR)
WORKSPACE_PATH.mkdir(parents=True, exist_ok=True)

# LLM Configuration
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-3-sonnet-20240229")

# Runtime Configuration
SANDBOX_RUNTIME_CONTAINER_IMAGE = os.getenv(
    "SANDBOX_RUNTIME_CONTAINER_IMAGE",
    "docker.all-hands.dev/all-hands-ai/runtime:0.28-nikolaik",
)

# Channel Configuration
OPENHANDS_CHAT_CHANNEL = os.getenv("OPENHANDS_CHAT_CHANNEL", "openhands-chat")

# Task Configuration
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "5"))
TASK_TIMEOUT_SECONDS = int(os.getenv("TASK_TIMEOUT_SECONDS", "300"))  # 5 minutes


# Validate required environment variables
def validate_config():
    """Validate that all required environment variables are set."""
    missing_vars = []

    if not DISCORD_TOKEN:
        missing_vars.append("DISCORD_TOKEN")

    if not LLM_API_KEY:
        missing_vars.append("LLM_API_KEY")

    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )


# Call validation function
validate_config()
