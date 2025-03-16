# Technical Context

## Technology Stack

### Core Technologies
- **Python 3.9+**: The primary programming language
- **Discord.py**: Library for Discord bot development
- **Asyncio**: For asynchronous programming
- **OpenHands CLI**: Command-line interface for the OpenHands AI coding assistant

### Dependencies
- **discord.py**: Discord API wrapper for Python
- **python-dotenv**: For loading environment variables
- **aiohttp**: Asynchronous HTTP client/server
- **pydantic**: Data validation and settings management

### Testing Libraries
- **pytest**: Primary testing framework
- **pytest-asyncio**: For testing asynchronous code
- **pytest-mock**: For mocking dependencies
- **coverage**: For measuring test coverage

### Monitoring Tools (Planned)
- **Prometheus**: For metrics collection
- **Grafana**: For metrics visualization
- **healthchecks.io**: For external monitoring

## Development Setup

### Environment Variables
The system requires the following environment variables:
- `DISCORD_TOKEN`: Discord bot token
- `COMMAND_PREFIX`: Prefix for bot commands (default: `!oh `)
- `OPENHANDS_CLI_PATH`: Path to the OpenHands CLI
- `OPENHANDS_WORKDIR`: Directory for OpenHands workspaces
- `LLM_API_KEY`: API key for the language model
- `LLM_MODEL`: Model identifier (default: `claude-3-sonnet-20240229`)
- `SANDBOX_RUNTIME_CONTAINER_IMAGE`: Docker image for the sandbox runtime
- `OPENHANDS_CHAT_CHANNEL`: Name of the Discord channel for OpenHands chat
- `MAX_CONCURRENT_TASKS`: Maximum number of concurrent tasks (default: 5)
- `TASK_TIMEOUT_SECONDS`: Timeout for tasks in seconds (default: 300)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `RETRY_COUNT`: Number of retries for failed operations (default: 3)
- `RETRY_DELAY`: Delay between retries in seconds (default: 2)

### Local Development
1. Clone the repository
2. Create a `.env` file with the required environment variables
3. Install dependencies: `pip install -r requirements.txt`
4. Install development dependencies: `pip install -r requirements-dev.txt`
5. Run the bot: `python -m src`

### Testing
1. Install test dependencies: `pip install -r requirements-dev.txt`
2. Run tests: `pytest`
3. Run tests with coverage: `pytest --cov=src`
4. Generate coverage report: `pytest --cov=src --cov-report=html`

### Docker Deployment
The system can be deployed using Docker:
1. Build the Docker image: `docker build -t OpenHandsDiscordAdapter .`
2. Run the container: `docker run -d --env-file .env OpenHandsDiscordAdapter`

Alternatively, use Docker Compose:
```bash
docker-compose up -d
```

## Technical Constraints

### Discord API Limitations
- Message size limit: 2000 characters
- Embed size limit: 6000 characters total, with specific field limits
- Rate limits on API calls
- 25 reactions per message

### OpenHands CLI Constraints
- Requires specific environment setup
- Task execution is resource-intensive
- Long-running tasks need timeout handling
- Limited input/output capabilities

### Security Considerations
- API keys must be kept secure
- User input validation is essential
- Sandbox isolation for code execution
- Rate limiting for command execution
- Proper permission handling

## Integration Points

### Discord API
- Bot authentication and connection
- Command handling
- Message sending and receiving
- Embed formatting
- Reactions and interactive components

### OpenHands CLI
- Task creation and execution
- Chat functionality
- Status checking
- Result retrieval

## Performance Considerations

### Scalability
- The system uses asynchronous programming to handle multiple concurrent users
- Task queue management prevents overloading the system
- Configurable limits for concurrent tasks
- Horizontal scaling through multiple bot instances (planned)

### Resource Usage
- Long-running tasks can consume significant resources
- Timeout mechanisms prevent runaway processes
- Docker containerization provides resource isolation
- Resource quotas and limits for containerized deployments

### Latency
- Discord API interactions have inherent latency
- OpenHands task execution can take time
- Progress updates help manage user expectations
- Caching can reduce latency for repeated operations

## Testing Strategy

### Unit Testing
- Test individual components in isolation
- Mock external dependencies (Discord API, OpenHands CLI)
- Verify correct behavior of component methods
- Validate error handling and edge cases

### Integration Testing
- Test interactions between components
- Validate correct data flow between modules
- Use mock objects for external dependencies

### End-to-End Testing
- Test complete user workflows
- Validate system behavior from user perspective
- May use a test Discord server and bot account

### Test Data
- Mock inputs for various command scenarios
- Sample task outputs for testing formatting
- Error scenarios for testing error handling

## Monitoring and Observability (Planned)

### Health Checks
- Endpoint for checking system status
- Discord command for system diagnostics
- Connection status monitoring

### Metrics
- Task execution time
- Command frequency
- Error rates
- Resource usage

### Logging
- Structured logging with context
- Log levels for different severity
- Correlation IDs for tracking requests
- Sensitive data filtering

### Alerting
- Critical error notifications
- Service degradation alerts
- Resource usage warnings 