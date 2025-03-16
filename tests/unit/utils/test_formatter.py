"""Tests for the formatter module."""

import pytest
import discord
from src.utils.formatter import format_help, format_status, format_tasks_list


def test_format_help():
    """Test the format_help function."""
    # Given
    command_prefix = "!oh"
    
    # When
    result = format_help(command_prefix)
    
    # Then
    assert isinstance(result, str)
    assert command_prefix in result
    assert "task" in result
    assert "status" in result
    assert "help" in result


def test_format_status():
    """Test the format_status function."""
    # Given
    status = {
        "task_id": "test-123",
        "status": "completed",
        "description": "Test task",
        "created_at": "2023-01-01T12:00:00Z",
        "updated_at": "2023-01-01T12:05:00Z",
        "result": "Task completed successfully"
    }
    
    # When
    result = format_status(status)
    
    # Then
    assert isinstance(result, discord.Embed)
    assert result.title == "Task Status"
    assert "test-123" in result.description
    assert "completed" in result.description
    assert "Test task" in result.description


def test_format_tasks_list_empty():
    """Test the format_tasks_list function with empty list."""
    # Given
    tasks = []
    
    # When
    result = format_tasks_list(tasks)
    
    # Then
    assert isinstance(result, discord.Embed)
    assert result.title == "Your Tasks"
    assert "No tasks found" in result.description


def test_format_tasks_list():
    """Test the format_tasks_list function with tasks."""
    # Given
    tasks = [
        {
            "task_id": "test-123",
            "status": "completed",
            "description": "Test task 1",
            "created_at": "2023-01-01T12:00:00Z"
        },
        {
            "task_id": "test-456",
            "status": "in_progress",
            "description": "Test task 2",
            "created_at": "2023-01-01T13:00:00Z"
        }
    ]
    
    # When
    result = format_tasks_list(tasks)
    
    # Then
    assert isinstance(result, discord.Embed)
    assert result.title == "Your Tasks"
    assert "test-123" in result.description
    assert "test-456" in result.description
    assert "completed" in result.description
    assert "in_progress" in result.description 