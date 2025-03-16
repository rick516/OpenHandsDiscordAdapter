"""Pytest configuration and fixtures."""

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_discord_context():
    """Create a mock Discord context for testing."""
    context = MagicMock()
    context.send = AsyncMock()
    context.author = MagicMock()
    context.author.id = "123456789"
    context.message = MagicMock()
    context.message.content = "Test message"
    return context


@pytest.fixture
def mock_discord_interaction():
    """Create a mock Discord interaction for testing."""
    interaction = MagicMock()
    interaction.response = MagicMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    interaction.user = MagicMock()
    interaction.user.id = "123456789"
    return interaction


@pytest.fixture
def mock_openhands_adapter():
    """Create a mock OpenHands adapter for testing."""
    adapter = MagicMock()
    adapter.create_task = AsyncMock()
    adapter.get_task_status = AsyncMock()
    adapter.get_user_tasks = AsyncMock()
    adapter.chat = AsyncMock()
    adapter.start = AsyncMock()
    adapter.stop = AsyncMock()
    return adapter
