"""
Formatter Module

This module provides utilities for formatting responses for Discord.
"""

from typing import List

import discord


def format_result(result: dict) -> discord.Embed:
    """Format a task result as a Discord embed.

    Args:
        result: The task result dictionary.

    Returns:
        A Discord embed.
    """
    if result.get("success"):
        embed = discord.Embed(
            title="Task Completed",
            description="OpenHands task completed successfully",
            color=discord.Color.green(),
        )

        # Format output
        output = result.get("output", "")
        if len(output) > 4000:  # Discord has a 4096 character limit for embed fields
            chunks = [output[i : i + 1000] for i in range(0, len(output), 1000)]
            embed.add_field(name="Output", value=chunks[0] + "...", inline=False)
            for i, chunk in enumerate(chunks[1:], 1):
                if i < 4:  # Limit to 4 chunks to avoid hitting Discord's limits
                    embed.add_field(
                        name=f"Output (continued {i})", value=chunk, inline=False
                    )
                else:
                    embed.add_field(
                        name="Note",
                        value="Output truncated due to Discord's character limits",
                        inline=False,
                    )
                    break
        else:
            embed.add_field(name="Output", value=output or "No output", inline=False)
    else:
        embed = discord.Embed(
            title="Task Failed",
            description="OpenHands task failed",
            color=discord.Color.red(),
        )
        embed.add_field(
            name="Error", value=result.get("error", "Unknown error"), inline=False
        )

        # Include output if available
        output = result.get("output")
        if output:
            if len(output) > 1000:
                embed.add_field(
                    name="Output", value=output[:1000] + "...", inline=False
                )
            else:
                embed.add_field(name="Output", value=output, inline=False)

    return embed


def format_status(status: dict) -> discord.Embed:
    """Format a task status as a Discord embed.

    Args:
        status: The task status dictionary.

    Returns:
        A Discord embed.
    """
    status_colors = {
        "pending": discord.Color.blue(),
        "running": discord.Color.gold(),
        "completed": discord.Color.green(),
        "failed": discord.Color.red(),
    }

    if "error" in status:
        embed = discord.Embed(
            title="Error", description=status["error"], color=discord.Color.red()
        )
        return embed

    embed = discord.Embed(
        title=f"Task: {status.get('id', 'Unknown')}",
        description=status.get("description", "No description"),
        color=status_colors.get(status.get("status"), discord.Color.light_grey()),
    )

    embed.add_field(name="Status", value=status.get("status", "Unknown"), inline=True)

    # Add result if available
    if status.get("result"):
        result = status["result"]
        if result.get("success"):
            output = result.get("output", "")
            if len(output) > 1000:
                embed.add_field(
                    name="Output", value=output[:1000] + "...", inline=False
                )
            else:
                embed.add_field(
                    name="Output", value=output or "No output", inline=False
                )
        else:
            embed.add_field(
                name="Error", value=result.get("error", "Unknown error"), inline=False
            )

    return embed


def format_tasks_list(tasks: List[dict]) -> discord.Embed:
    """Format a list of tasks as a Discord embed.

    Args:
        tasks: A list of task dictionaries.

    Returns:
        A Discord embed.
    """
    embed = discord.Embed(
        title="Your Tasks",
        description=f"Total: {len(tasks)} tasks",
        color=discord.Color.blue(),
    )

    if not tasks:
        embed.add_field(
            name="No Tasks", value="You don't have any tasks yet", inline=False
        )
        return embed

    # Sort tasks by creation time (newest first)
    sorted_tasks = sorted(tasks, key=lambda t: t.get("created_at", 0), reverse=True)

    # Limit to 10 tasks to avoid hitting Discord's limits
    for task in sorted_tasks[:10]:
        status = task.get("status", "Unknown")
        status_emoji = {
            "pending": "⏳",
            "running": "🔄",
            "completed": "✅",
            "failed": "❌",
        }.get(status, "❓")

        value = f"{status_emoji} Status: {status}"

        # Add result summary if available
        if task.get("result"):
            result = task["result"]
            if result.get("success"):
                value += "\n✅ Result: Success"
            else:
                value += f"\n❌ Error: {result.get('error', 'Unknown error')[:100]}"

        embed.add_field(
            name=f"Task: {task.get('id')}",
            value=(
                f"**Description**: {task.get('description', 'No description')[:100]}\n"
                f"{value}"
            ),
            inline=False,
        )

    if len(sorted_tasks) > 10:
        embed.add_field(
            name="Note",
            value=(
                f"Showing 10 of {len(sorted_tasks)} tasks. "
                "Use `!oh status <task_id>` to view a specific task."
            ),
            inline=False,
        )

    return embed


def format_help(command_prefix):
    """Format help message.

    Args:
        command_prefix: The command prefix used by the bot.

    Returns:
        str: Formatted help message.
    """
    help_text = "**OpenHands Discord Bot Help**\n\n"

    # Add prefix commands section
    help_text += "**Prefix Commands:**\n"
    help_text += f"`{command_prefix}task <description>` - Create a new task\n"
    help_text += (
        f"`{command_prefix}status [task_id]` - Check task status or list all tasks\n"
    )
    help_text += f"`{command_prefix}help` - Show this help message\n\n"

    # Add slash commands section
    help_text += "**Slash Commands:**\n"
    help_text += "`/task <description>` - Create a new task\n"
    help_text += "`/status [task_id]` - Check task status or list all tasks\n"
    help_text += "`/tasks` - List all your tasks\n"
    help_text += "`/help` - Show this help message\n\n"

    # Add examples section
    help_text += "**Examples:**\n"
    help_text += f"`{command_prefix}task Create a Python script that calculates fibonacci numbers`\n"
    help_text += f"`{command_prefix}status 1234`\n"
    help_text += "or\n"
    help_text += "`/task Create a Python script that calculates fibonacci numbers`\n"
    help_text += "`/status 1234`\n\n"

    # Add chat mode section
    help_text += "**Chat Mode:**\n"
    help_text += "You can also chat directly with OpenHands in DMs or in the designated channel.\n"

    return help_text
