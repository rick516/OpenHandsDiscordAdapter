# OpenHandsDiscordAdapter

A Discord bot that integrates with OpenHands to provide AI-powered task execution and chat capabilities directly in Discord.

## Features

- Create and manage OpenHands tasks directly from Discord
- Check task status and results
- Chat with OpenHands in dedicated channels
- Supports multiple LLM providers (Anthropic, OpenAI, OpenRouter, etc.)

## Prerequisites

- Python 3.9 or higher
- Discord Developer Account
- OpenHands CLI installed
- LLM API key (Anthropic, OpenAI, or OpenRouter)

## Setup Instructions

### 1. Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" tab and click "Add Bot"
4. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
5. Copy your bot token (you'll need this for the `.env` file)
6. Go to "OAuth2" > "URL Generator"
7. Select the following scopes:
   - `bot`
   - `applications.commands`
8. Select the following bot permissions:
   - Send Messages
   - Read Message History
   - View Channels
   - Embed Links
   - Add Reactions
9. Copy the generated URL and use it to invite the bot to your server

### 2. Environment Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/OpenHandsDiscordAdapter.git
   cd OpenHandsDiscordAdapter
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   ```

4. Edit the `.env` file with your configuration:
   ```
   # Discord Bot Configuration
   DISCORD_TOKEN=your_discord_bot_token_here
   COMMAND_PREFIX=!oh 
   OPENHANDS_CHAT_CHANNEL=openhands-chat

   # OpenHands Configuration
   OPENHANDS_CLI_PATH=openhands.core.cli
   OPENHANDS_WORKDIR=./openhands_workspace

   # LLM Configuration
   LLM_API_KEY=your_llm_api_key_here
   # Format: provider/model_name
   LLM_MODEL=anthropic/claude-3-5-sonnet-20241022

   # Runtime Configuration
   SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.28-nikolaik

   # Task Configuration
   MAX_CONCURRENT_TASKS=5
   TASK_TIMEOUT_SECONDS=300
   ```

### 3. Server Setup

1. Create a channel named `openhands-chat` in your Discord server (or customize the name in your `.env` file)
2. Ensure the bot has permissions to read and send messages in this channel

### 4. Running the Bot

```
python -m src.__main__
```

You should see a message indicating that the bot has logged in successfully.

## Usage

### Slash Commands

- `/help` - Display help information
- `/task <description>` - Create a new task
- `/status [task_id]` - Check task status
- `/tasks` - List all tasks

### Prefix Commands

The bot also supports traditional prefix commands:

- `!oh help` - Display help information
- `!oh task <description>` - Create a new task
- `!oh status [task_id]` - Check task status
- `!oh tasks` - List all tasks

### Chat Mode

Simply send a message in the `openhands-chat` channel or DM the bot to chat with OpenHands.

## LLM Provider Configuration

The adapter supports multiple LLM providers through the `LLM_MODEL` environment variable:

- Anthropic: `anthropic/claude-3-5-sonnet-20241022`
- OpenAI: `openai/gpt-4-turbo`
- OpenRouter: `openrouter/anthropic/claude-3-5-sonnet-20241022`

## Troubleshooting

### Bot Not Responding to Messages

- Ensure the "Message Content Intent" is enabled in the Discord Developer Portal
- Check that the bot has the necessary permissions in your server
- Verify your Discord token is correct in the `.env` file

### OpenHands CLI Errors

- Make sure OpenHands CLI is installed: `pip install openhands`
- Check that the workspace directory exists and is writable
- Verify your LLM API key is correct

### LLM Provider Issues

- Ensure your API key is valid and has sufficient credits
- Check that the model name is correctly formatted as `provider/model_name`
- For OpenRouter, use the format `openrouter/provider/model_name`

## License

This project is licensed under the [MIT License](LICENSE).

This project uses the following open source software:
- [OpenHands](https://github.com/All-Hands-AI/OpenHands) - MIT License
- [discord.py](https://github.com/Rapptz/discord.py) - MIT License

See [CREDITS.md](CREDITS.md) for more details on dependencies and licenses.
