"""
Discord Bot Module

This module provides the Discord bot for interacting with OpenHands.
"""

import asyncio
import logging
from typing import Optional

import discord
from discord.ext import commands

from OpenHandsDiscord.adapter.openhands_adapter import openhands_adapter
from OpenHandsDiscord.config import DISCORD_TOKEN, COMMAND_PREFIX, OPENHANDS_CHAT_CHANNEL
from OpenHandsDiscord.utils.formatter import (
    format_result,
    format_status,
    format_tasks_list,
    format_help,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("openhands-discord")

# Set up Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, help_command=None)


@bot.event
async def on_ready():
    """Event handler for when the bot is ready."""
    logger.info(f"Logged in as {bot.user.name} ({bot.user.id})")
    logger.info(f"Command prefix: {COMMAND_PREFIX}")
    
    # Start the OpenHands adapter
    await openhands_adapter.start()
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=f"{COMMAND_PREFIX}help"
        )
    )


@bot.event
async def on_message(message):
    """Event handler for when a message is received."""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Process DMs or messages in the OpenHands chat channel
    if isinstance(message.channel, discord.DMChannel) or (
        isinstance(message.channel, discord.TextChannel) and 
        message.channel.name == OPENHANDS_CHAT_CHANNEL
    ):
        # Only process messages that don't start with the command prefix
        if not message.content.startswith(bot.command_prefix):
            async with message.channel.typing():
                # Send a thinking message
                thinking_msg = await message.channel.send("🤔 Thinking...")
                
                try:
                    # Get response from OpenHands
                    response = await openhands_adapter.chat(
                        str(message.author.id),
                        message.content
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
async def create_task(ctx, *, description: str):
    """Create a new task.
    
    Args:
        description: The task description.
    """
    # Send a thinking message
    thinking_msg = await ctx.send("⏳ Creating task...")
    
    try:
        # Create task
        result = await openhands_adapter.create_task(
            str(ctx.author.id),
            description
        )
        
        # Send response
        await thinking_msg.edit(
            content=f"✅ Task created with ID: `{result['task_id']}`\n"
                   f"Use `{COMMAND_PREFIX}status {result['task_id']}` to check the status."
        )
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        await thinking_msg.edit(content=f"❌ Error creating task: {str(e)}")


@bot.command(name="status")
async def check_status(ctx, task_id: Optional[str] = None):
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
async def help_command(ctx):
    """Show help message."""
    embed = format_help()
    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    """Event handler for command errors."""
    if isinstance(error, commands.MissingRequiredArgument):
        if ctx.command.name == "task":
            await ctx.send(
                f"❌ Error: Missing task description\n"
                f"Usage: `{COMMAND_PREFIX}task <description>`"
            )
        else:
            await ctx.send(f"❌ Error: {str(error)}")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(
            f"❌ Command not found. Use `{COMMAND_PREFIX}help` to see available commands."
        )
    else:
        logger.error(f"Command error: {error}")
        await ctx.send(f"❌ Error: {str(error)}")


async def main():
    """Main function to run the bot."""
    try:
        # Start the bot
        await bot.start(DISCORD_TOKEN)
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