"""
Discord Bot Module

This module provides the Discord bot for interacting with OpenHands.
"""

import asyncio
import http.server
import json
import logging
import socketserver
import threading
from typing import Any, Callable, Coroutine, List, Optional, Type, Union

import discord
from discord import app_commands
from discord.ext import commands

from src.adapter.openhands_adapter import OpenHandsAdapter
from src.config import COMMAND_PREFIX, DISCORD_TOKEN, OPENHANDS_CHAT_CHANNEL, Config
from src.utils.formatter import (
    format_help,
    format_result,
    format_status,
    format_tasks_list,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("OpenHandsDiscordAdapter")

# Set up Discord bot
intents = discord.Intents.default()
intents.message_content = True

intents.messages = True

# Create OpenHands adapter

openhands_adapter = OpenHandsAdapter()


class OpenHandsBot(commands.Bot):
    """Discord bot for interacting with OpenHands."""

    def __init__(self, config: Config) -> None:
        """Initialize the bot."""
        super().__init__(
            command_prefix=COMMAND_PREFIX, intents=intents, help_command=None
        )
        self.config = config

        # Start health check server
        self.start_health_check_server()

    def start_health_check_server(self) -> None:
        """Start a simple HTTP server for health checks."""

        class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self) -> None:
                """Handle GET requests."""
                if self.path == "/health":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    health_data = {
                        "status": "ok",
                        "version": "1.0.0",
                        "discord_connected": True,
                    }
                    self.wfile.write(json.dumps(health_data).encode())
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Not found"}).encode())

            def log_message(self, format: str, *args: Any) -> None:
                """Suppress logging for health check requests."""
                pass

        def run_server() -> None:
            """Run the health check server."""
            with socketserver.TCPServer(("", 8000), HealthCheckHandler) as httpd:
                httpd.serve_forever()

        # Start the health check server in a separate thread
        health_thread = threading.Thread(target=run_server, daemon=True)
        health_thread.start()
        logger.info("Health check server started on port 8000")


# Initialize the bot
bot = OpenHandsBot(Config())


@bot.event
async def on_ready() -> None:
    """Event handler for when the bot is ready."""
    if bot.user is not None:
        logger.info(f"Logged in as {bot.user.name} ({bot.user.id})")
    else:
        logger.info("Logged in but user is None")
    logger.info(f"Command prefix: {COMMAND_PREFIX}")

    # Register slash commands
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        logger.error(f"Failed to sync slash commands: {e}")

    # Start the OpenHands adapter
    await openhands_adapter.start()

    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name=f"{COMMAND_PREFIX}help | /help"
        )
    )


@bot.event
async def on_message(message: discord.Message) -> None:
    """Event handler for when a message is received."""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Process DMs or messages in the OpenHands chat channel
    if isinstance(message.channel, discord.DMChannel) or (
        isinstance(message.channel, discord.TextChannel)
        and message.channel.name == OPENHANDS_CHAT_CHANNEL
    ):
        # Only process messages that don't start with the command prefix
        if not message.content.startswith(str(bot.command_prefix)):
            async with message.channel.typing():
                # Send a thinking message
                thinking_msg = await message.channel.send("🤔 Thinking...")

                try:
                    # Get response from OpenHands
                    response = await openhands_adapter.chat(
                        str(message.author.id), message.content
                    )

                    # Delete thinking message
                    await thinking_msg.delete()

                    # Send response
                    await message.channel.send(response)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    await thinking_msg.edit(content=f"❌ Error: {str(e)}")

            # Don't process commands
            return

    # Process commands
    await bot.process_commands(message)


@bot.command(name="task")
async def create_task(ctx: commands.Context, *, description: str) -> None:
    """Create a new task.

    Args:
        description: The task description.
    """
    # Send a thinking message
    thinking_msg = await ctx.send("⏳ Creating task...")

    try:
        # Create task
        result = await openhands_adapter.create_task(str(ctx.author.id), description)

        # Send response
        await thinking_msg.edit(
            content=f"✅ Task created with ID: `{result['task_id']}`\n"
            f"Use `{COMMAND_PREFIX}status {result['task_id']}` to check the status."
        )
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        await thinking_msg.edit(content=f"❌ Error creating task: {str(e)}")


@bot.command(name="status")
async def check_status(ctx: commands.Context, task_id: Optional[str] = None) -> None:
    """Check task status.

    Args:
        task_id: The task ID. If not provided, shows all tasks.
    """
    # Send a thinking message
    thinking_msg = await ctx.send("⏳ Checking status...")

    try:
        if task_id:
            # Get status of specific task
            status = await openhands_adapter.get_task_status(task_id)
            embed = format_status(status)
        else:
            # Get all tasks for user
            tasks = await openhands_adapter.get_user_tasks(str(ctx.author.id))
            embed = format_tasks_list(tasks)

        # Send response
        await thinking_msg.delete()
        await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"Error checking status: {e}")
        await thinking_msg.edit(content=f"❌ Error checking status: {str(e)}")


@bot.command(name="help")
async def show_help(ctx: commands.Context) -> None:
    """Show help information."""
    await ctx.send(format_help(COMMAND_PREFIX))


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
    """Event handler for command errors."""
    if isinstance(error, commands.MissingRequiredArgument):
        if ctx.command and ctx.command.name == "task":
            await ctx.send(
                f"❌ Error: Missing task description\n"
                f"Usage: `{COMMAND_PREFIX}task <description>`"
            )
        else:
            await ctx.send(f"❌ Error: {str(error)}")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(
            f"❌ Command not found. Use `{COMMAND_PREFIX}help` "
            "to see available commands."
        )
    else:
        logger.error(f"Command error: {error}")
        await ctx.send(f"❌ Error: {str(error)}")


# Slash command implementations
@bot.tree.command(name="help", description="Show help information")
async def slash_help(interaction: discord.Interaction) -> None:
    """Show help information."""
    await interaction.response.send_message(format_help(COMMAND_PREFIX))


@bot.tree.command(name="task", description="Create a new task")
async def slash_task(interaction: discord.Interaction, description: str) -> None:
    """Create a new task."""
    await interaction.response.defer(thinking=True)

    try:
        task_id = await openhands_adapter.create_task(
            str(interaction.user.id), description
        )

        response = f"✅ Task created with ID: `{task_id}`\n"
        response += "I'll notify you when it's complete."

        await interaction.followup.send(response)
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        await interaction.followup.send(f"❌ Error: {str(e)}")


@bot.tree.command(name="status", description="Check task status")
@app_commands.describe(task_id="The ID of the task to check (optional)")
async def slash_status(
    interaction: discord.Interaction, task_id: Optional[str] = None
) -> None:
    """Check task status."""
    await interaction.response.defer(thinking=True)

    try:
        if task_id:
            # Get status of specific task
            status = await openhands_adapter.get_task_status(task_id)

            # Format and send status
            formatted_status = format_status(status)
            await interaction.followup.send(embed=formatted_status)
        else:
            # Get all tasks for user
            tasks = await openhands_adapter.get_user_tasks(str(interaction.user.id))

            if not tasks:
                await interaction.followup.send("You don't have any tasks yet.")
                return

            # Format and send tasks list
            formatted_tasks = format_tasks_list(tasks)
            await interaction.followup.send(embed=formatted_tasks)
    except Exception as e:
        logger.error(f"Error checking status: {e}")
        await interaction.followup.send(f"❌ Error: {str(e)}")


@bot.tree.command(name="tasks", description="List all your tasks")
async def slash_tasks(interaction: discord.Interaction) -> None:
    """List all your tasks."""
    await interaction.response.defer(thinking=True)

    try:
        # Get all tasks for user
        tasks = await openhands_adapter.get_user_tasks(str(interaction.user.id))

        if not tasks:
            await interaction.followup.send("You don't have any tasks yet.")
            return

        # Format and send tasks list
        formatted_tasks = format_tasks_list(tasks)
        await interaction.followup.send(embed=formatted_tasks)
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        await interaction.followup.send(f"❌ Error: {str(e)}")


async def main() -> None:
    """Main function to run the bot."""
    try:
        # Start the bot
        await bot.start(DISCORD_TOKEN if DISCORD_TOKEN is not None else "")
    except KeyboardInterrupt:
        # Handle keyboard interrupt
        logger.info("Keyboard interrupt received")
    except Exception as e:
        # Handle other exceptions
        logger.error(f"Error starting bot: {e}")
    finally:
        # Stop the OpenHands adapter
        await openhands_adapter.stop()

        # Close the bot
        if not bot.is_closed():
            await bot.close()


if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
