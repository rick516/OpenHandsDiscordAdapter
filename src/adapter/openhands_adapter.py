"""
OpenHands Adapter Module

This module provides an adapter for interacting with OpenHands.
"""

import asyncio
import os
import uuid
from pathlib import Path
from typing import Any, Coroutine, Dict, List, Optional, Union, cast

from src.config import (
    LLM_API_KEY,
    LLM_MODEL,
    OPENHANDS_CLI_PATH,
    OPENHANDS_WORKDIR,
    SANDBOX_RUNTIME_CONTAINER_IMAGE,
    TASK_TIMEOUT_SECONDS,
)


class OpenHandsAdapter:
    """Adapter for interacting with OpenHands."""

    def __init__(self) -> None:
        """Initialize the OpenHands adapter."""
        self.active_sessions: Dict[str, dict] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self.task_processor: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the task processor."""
        self.running = True
        self.task_processor = asyncio.create_task(self.process_tasks())

    async def stop(self) -> None:
        """Stop the task processor."""
        self.running = False
        if self.task_processor:
            self.task_processor.cancel()
            try:
                await self.task_processor
            except asyncio.CancelledError:
                pass

    async def create_task(self, user_id: str, description: str) -> dict:
        """Create a new task and add it to the queue.

        Args:
            user_id: The Discord user ID.
            description: The task description.

        Returns:
            A dictionary containing the task ID and status.
        """
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = {
            "id": task_id,
            "user_id": user_id,
            "description": description,
            "status": "pending",
            "result": None,
            "created_at": asyncio.get_event_loop().time(),
        }
        self.active_sessions[task_id] = task

        # Add task to queue
        await self.task_queue.put(task)

        return {"task_id": task_id, "status": "pending"}

    async def get_task_status(self, task_id: str) -> dict:
        """Get the status of a task.

        Args:
            task_id: The task ID.

        Returns:
            A dictionary containing the task status.
        """
        if task_id in self.active_sessions:
            return self.active_sessions[task_id]
        return {"error": "Task not found"}

    async def get_user_tasks(self, user_id: str) -> List[dict]:
        """Get all tasks for a user.

        Args:
            user_id: The Discord user ID.

        Returns:
            A list of task dictionaries.
        """
        return [
            task for task in self.active_sessions.values() if task["user_id"] == user_id
        ]

    async def chat(self, user_id: str, message: str) -> str:
        """Chat with OpenHands.

        Args:
            user_id: The Discord user ID.
            message: The message to send to OpenHands.

        Returns:
            The response from OpenHands.
        """
        # Create or get user session
        session_id = f"chat_{user_id}"
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "id": session_id,
                "user_id": user_id,
                "context": [],
                "status": "active",
                "created_at": asyncio.get_event_loop().time(),
            }

        # Add message to context
        self.active_sessions[session_id]["context"].append(
            {"role": "user", "content": message}
        )

        # Send to OpenHands and get response
        response = await self._send_to_openhands(session_id, message)

        # Add response to context
        self.active_sessions[session_id]["context"].append(
            {"role": "assistant", "content": response}
        )

        return response

    async def process_tasks(self) -> None:
        """Process tasks from the queue."""
        while self.running:
            try:
                # Get task from queue
                task = await self.task_queue.get()

                # Update task status
                task["status"] = "running"

                # Execute OpenHands CLI
                result = await self._execute_openhands_cli(task)

                # Update task with result
                task["status"] = "completed" if result.get("success") else "failed"
                task["result"] = result
                task["completed_at"] = asyncio.get_event_loop().time()

            except asyncio.CancelledError:
                # Handle cancellation
                raise
            except Exception as e:
                # Handle other exceptions
                if task:
                    task["status"] = "failed"
                    task["error"] = str(e)
                    task["completed_at"] = asyncio.get_event_loop().time()
            finally:
                # Mark task as done
                if task:
                    self.task_queue.task_done()

    async def _execute_openhands_cli(self, task: dict) -> dict:
        """Execute the OpenHands CLI.

        Args:
            task: The task dictionary.

        Returns:
            A dictionary containing the result of the execution.
        """
        # Create user workspace directory
        user_workspace = Path(OPENHANDS_WORKDIR) / str(task["user_id"])
        user_workspace.mkdir(parents=True, exist_ok=True)

        # Set environment variables
        env = os.environ.copy()
        env["LLM_API_KEY"] = LLM_API_KEY if LLM_API_KEY is not None else ""
        env["LLM_MODEL"] = LLM_MODEL if LLM_MODEL is not None else ""
        env["SANDBOX_RUNTIME_CONTAINER_IMAGE"] = (
            SANDBOX_RUNTIME_CONTAINER_IMAGE
            if SANDBOX_RUNTIME_CONTAINER_IMAGE is not None
            else ""
        )

        # Prepare command
        cmd = [
            "python",
            "-m",
            OPENHANDS_CLI_PATH,
            "--workspace",
            str(user_workspace),
            "--task",
            task["description"],
        ]

        try:
            # Run OpenHands CLI with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )

            # Wait for process to complete with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=TASK_TIMEOUT_SECONDS
                )

                if process.returncode != 0:
                    return {
                        "success": False,
                        "error": stderr.decode("utf-8"),
                        "output": stdout.decode("utf-8"),
                    }

                return {
                    "success": True,
                    "output": stdout.decode("utf-8"),
                }
            except asyncio.TimeoutError:
                # Kill process if it times out
                process.kill()
                return {
                    "success": False,
                    "error": f"Task timed out after {TASK_TIMEOUT_SECONDS} seconds",
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def _send_to_openhands(self, session_id: str, message: str) -> str:
        """Send a message to OpenHands and get a response.

        Args:
            session_id: The session ID.
            message: The message to send.

        Returns:
            The response from OpenHands.
        """
        # Get user ID from session
        user_id = self.active_sessions[session_id]["user_id"]

        # Create user workspace directory
        user_workspace = Path(OPENHANDS_WORKDIR) / str(user_id)
        user_workspace.mkdir(parents=True, exist_ok=True)

        # Set environment variables
        env = os.environ.copy()
        env["LLM_API_KEY"] = LLM_API_KEY if LLM_API_KEY is not None else ""
        env["LLM_MODEL"] = LLM_MODEL if LLM_MODEL is not None else ""
        env["SANDBOX_RUNTIME_CONTAINER_IMAGE"] = (
            SANDBOX_RUNTIME_CONTAINER_IMAGE
            if SANDBOX_RUNTIME_CONTAINER_IMAGE is not None
            else ""
        )

        # Prepare command
        cmd = [
            "python",
            "-m",
            OPENHANDS_CLI_PATH,
            "--workspace",
            str(user_workspace),
            "--task",
            message,
        ]

        try:
            # Run OpenHands CLI with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )

            # Wait for process to complete with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=TASK_TIMEOUT_SECONDS
                )

                if process.returncode != 0:
                    error_msg = stderr.decode("utf-8")
                    return f"Error: {error_msg}"

                output = stdout.decode("utf-8")
                # Extract the assistant's response from the output
                # This is a simplified approach and might need adjustment based on actual output format
                lines = output.strip().split("\n")
                response_lines = []
                for line in lines:
                    if line.startswith("🤖 "):
                        response_lines.append(line[2:].strip())

                if response_lines:
                    return "\n".join(response_lines)
                return output
            except asyncio.TimeoutError:
                # Kill process if it times out
                process.kill()
                return f"Error: Task timed out after {TASK_TIMEOUT_SECONDS} seconds"
        except Exception as e:
            return f"Error: {str(e)}"


# Create a singleton instance
openhands_adapter = OpenHandsAdapter()
