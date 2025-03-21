# System Patterns

## System Architecture

The OpenHandsDiscordAdapter System follows a modular architecture with clear separation of concerns. The system is organized into the following components:

```mermaid
flowchart TD
    DiscordBot[Discord Bot] --> Adapter[OpenHands Adapter]
    DiscordBot --> Formatter[Response Formatter]
    Adapter --> OpenHandsCLI[OpenHands CLI]
    Config[Configuration] --> DiscordBot
    Config --> Adapter
    ErrorHandler[Error Handler] --> DiscordBot
    ErrorHandler --> Adapter
    Monitoring[Monitoring & Diagnostics] -.-> DiscordBot
    Monitoring -.-> Adapter
    Monitoring -.-> OpenHandsCLI
```

### Key Components

1. **Discord Bot (`src/bot/bot.py`)**
   - Handles Discord events and commands
   - Manages user interactions
   - Routes requests to the OpenHands adapter
   - Presents formatted responses back to users
   - Supports both prefix commands and slash commands

2. **OpenHands Adapter (`src/adapter/openhands_adapter.py`)**
   - Interfaces with the OpenHands CLI
   - Manages task queues and execution
   - Maintains user sessions and conversation context
   - Handles asynchronous task processing

3. **Response Formatter (`src/utils/formatter.py`)**
   - Formats task results and status updates for Discord
   - Creates Discord embeds with appropriate styling
   - Handles message chunking for large responses
   - Provides help information for both prefix and slash commands

4. **Configuration (`src/config.py`)**
   - Manages environment variables
   - Provides configuration validation
   - Centralizes system settings

5. **Error Handler (Planned)**
   - Provides centralized error handling
   - Implements retry mechanisms for transient errors
   - Generates user-friendly error messages

6. **Monitoring & Diagnostics (Planned)**
   - Collects system health metrics
   - Provides diagnostic commands
   - Generates alerts for system issues

## Design Patterns

### 1. Adapter Pattern
The OpenHandsAdapter acts as an adapter between the Discord bot and the OpenHands CLI, translating Discord commands into OpenHands operations.

### 2. Command Pattern
The Discord bot uses the command pattern to handle different user commands (`!oh task`, `!oh status`, etc.), encapsulating each command as a separate function. This pattern is also applied to slash commands (`/task`, `/status`, etc.).

### 3. Asynchronous Task Queue
The system uses an asynchronous task queue to manage and process OpenHands tasks, allowing for non-blocking operation and concurrent task execution.

### 4. Singleton Pattern
The OpenHandsAdapter is implemented as a singleton to ensure a single instance manages all OpenHands interactions.

### 5. Factory Pattern
The formatter module acts as a factory for creating different types of Discord embeds based on the content being displayed.

### 6. Circuit Breaker Pattern (Planned)
To improve error handling, a circuit breaker pattern will be implemented to prevent repeated failures when external services are unavailable.

### 7. Repository Pattern (Planned)
For persistent storage of task and user data, a repository pattern will be used to abstract the storage implementation.

### 8. Strategy Pattern (Planned)
The response formatting will be enhanced with a strategy pattern to support different output formats based on content type and user preferences.

### 9. Facade Pattern
The Discord bot acts as a facade, providing a simplified interface to the complex subsystems (OpenHands CLI, task management, etc.).

## Testing Patterns

### 1. Unit Testing
Individual components are tested in isolation using mock objects to replace dependencies.

```mermaid
flowchart TD
    FormatterTest[Formatter Tests] --> Formatter[Response Formatter]
    AdapterTest[Adapter Tests] --> Adapter[OpenHands Adapter]
    AdapterTest --> MockCLI[Mock OpenHands CLI]
    BotTest[Bot Tests] --> Bot[Discord Bot]
    BotTest --> MockAdapter[Mock Adapter]
    BotTest --> MockFormatter[Mock Formatter]
```

### 2. Integration Testing
Tests the interaction between components, ensuring they work together correctly.

```mermaid
flowchart TD
    BotAdapterTest[Bot-Adapter Tests] --> Bot[Discord Bot]
    BotAdapterTest --> Adapter[OpenHands Adapter]
    BotAdapterTest --> MockCLI[Mock OpenHands CLI]
    AdapterCLITest[Adapter-CLI Tests] --> Adapter[OpenHands Adapter]
    AdapterCLITest --> MockCLI[Mock OpenHands CLI]
```

### 3. End-to-End Testing
Tests the entire system flow from Discord command to OpenHands execution and response.

## Component Relationships

### Discord Bot → OpenHands Adapter
- The bot forwards user commands and messages to the adapter
- The adapter returns results that the bot presents to users

### OpenHands Adapter → OpenHands CLI
- The adapter executes the OpenHands CLI as a subprocess
- It passes user inputs and retrieves outputs

### Discord Bot → Response Formatter
- The bot uses the formatter to create user-friendly Discord embeds
- The formatter handles different types of content (task results, status updates, help information)

## Data Flow

```mermaid
sequenceDiagram
    User->>Discord Bot: Send command/message
    Discord Bot->>OpenHands Adapter: Forward request
    OpenHands Adapter->>Task Queue: Add task (if applicable)
    OpenHands Adapter->>OpenHands CLI: Execute command
    OpenHands CLI->>OpenHands Adapter: Return result
    OpenHands Adapter->>Discord Bot: Return formatted response
    Discord Bot->>Response Formatter: Format response
    Discord Bot->>User: Display formatted response
```

## Command Handling Flow

```mermaid
sequenceDiagram
    User->>Discord Bot: Send prefix command (!oh)
    Discord Bot->>Command Handler: Process prefix command
    Command Handler->>OpenHands Adapter: Execute operation
    
    User->>Discord Bot: Send slash command (/)
    Discord Bot->>Slash Command Handler: Process slash command
    Slash Command Handler->>OpenHands Adapter: Execute operation
    
    OpenHands Adapter->>Discord Bot: Return result
    Discord Bot->>Response Formatter: Format response
    Discord Bot->>User: Display formatted response
```

## Error Handling Strategy
The system implements a comprehensive error handling strategy:
1. Command validation in the Discord bot
2. Error catching in the adapter's task execution
3. Graceful degradation with informative error messages
4. Timeout handling for long-running tasks
5. Retry mechanisms for transient errors (planned)
6. Circuit breaker for external service failures (planned)

## Security Strategy
The system implements security measures to protect against common vulnerabilities:
1. Input validation to prevent injection attacks
2. Permission checks for command execution
3. Rate limiting to prevent abuse
4. Secure handling of API keys and sensitive information

## Performance Optimization
To ensure responsive user experience, the system includes:
1. Asynchronous processing for non-blocking operations
2. Task queue management to prevent overloading
3. Caching for frequently used data (planned)
4. Message pagination for large responses (planned)

## Internationalization Support
For multi-language support, the system implements:
1. Documentation in multiple languages (English and Japanese)
2. Planned localization of bot messages and responses
3. Future support for user language preferences
4. Locale-aware formatting for dates, times, and numbers

## システムアーキテクチャ

OpenHandsDiscordAdapterは、Discord APIとOpenHandsを統合するアダプターとして機能します。システムは以下のコンポーネントで構成されています：

1. **Discord Bot Interface**: Discord APIと通信し、ユーザーコマンドを処理します
2. **Command Handler**: ユーザーコマンドを解析し、適切なアクションにルーティングします
3. **Task Manager**: OpenHandsタスクの作成、管理、ステータス追跡を行います
4. **Chat Handler**: OpenHandsとのチャット機能を提供します
5. **Configuration Manager**: 環境変数と設定を管理します

## 主要な技術的決定

1. **モジュール分割**: 機能ごとに明確に分離されたモジュール構造を採用し、保守性と拡張性を向上
2. **非同期処理**: Discord.pyとasyncioを使用した非同期処理により、複数のリクエストを効率的に処理
3. **環境変数による設定**: 設定は環境変数を通じて行い、デプロイ環境に応じた柔軟な構成が可能
4. **Docker化**: コンテナ化によりデプロイと環境の一貫性を確保
5. **CI/CD自動化**: GitHub Actionsを使用した継続的インテグレーションと継続的デリバリーの実装

## 使用中の設計パターン

1. **アダプターパターン**: Discord APIとOpenHands APIの間の互換性を提供
2. **コマンドパターン**: ユーザーリクエストをカプセル化し、適切なハンドラーに転送
3. **ファクトリーパターン**: タスクとレスポンスの生成を抽象化
4. **オブザーバーパターン**: タスクステータスの変更を監視し、ユーザーに通知
5. **シングルトンパターン**: 設定マネージャーなど、単一インスタンスが必要なコンポーネントに使用

## コンポーネントの関係

```mermaid
graph TD
    User[Discord User] -->|Commands/Messages| DiscordBot[Discord Bot]
    DiscordBot -->|Parse Commands| CommandHandler[Command Handler]
    CommandHandler -->|Task Commands| TaskManager[Task Manager]
    CommandHandler -->|Chat Messages| ChatHandler[Chat Handler]
    TaskManager -->|Create/Manage Tasks| OpenHands[OpenHands API]
    ChatHandler -->|Send/Receive Messages| OpenHands
    ConfigManager[Configuration Manager] -->|Provide Settings| DiscordBot
    ConfigManager -->|Provide Settings| TaskManager
    ConfigManager -->|Provide Settings| ChatHandler
```

## 開発ワークフロー

1. **フィーチャーブランチ開発**: 新機能やバグ修正は個別のブランチで開発
2. **プルリクエスト**: コードレビューとCI/CDチェックを通過後にマージ
3. **自動テスト**: ユニットテストと統合テストによる品質保証
4. **コードスタイル**: Black、isort、flake8、mypyによるコード品質の維持
5. **セキュリティチェック**: Banditとsafetyによるセキュリティ脆弱性のチェック

## ブランチプロテクション設定

リポジトリでは以下のブランチプロテクションルールが設定されています：

1. **プルリクエストの必須化**: `main`ブランチへの直接プッシュは禁止され、すべての変更はPRを通して行う必要があります
2. **レビュー承認の必須化**: 少なくとも1人のレビュー承認が必要です
3. **ステータスチェックの必須化**: 以下のCI/CDワークフローのチェックが成功する必要があります
   - lint: コードスタイルと品質チェック
   - test: ユニットテストと統合テスト
   - security: セキュリティ脆弱性チェック
   - docker: Dockerイメージのビルドテスト
4. **ブランチの最新状態の必須化**: マージ前にブランチを最新の状態に保つ必要があります
5. **管理者にも適用**: 管理者もこれらのルールに従う必要があります

これにより、コードの品質を維持し、安定したメインブランチを確保します 