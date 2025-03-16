# OpenHandsDiscordAdapter

OpenHands AIとDiscordを連携させるボットで、Discord上でAIによるタスク実行やチャット機能を提供します。

## 機能

- Discord上からOpenHandsのタスクを作成・管理
- タスクのステータスや結果を確認
- 専用チャンネルでOpenHandsとチャット
- 複数のLLMプロバイダー（Anthropic、OpenAI、OpenRouterなど）をサポート

## 前提条件

- Python 3.9以上
- Discordデベロッパーアカウント
- OpenHands CLIのインストール
- LLM API キー（Anthropic、OpenAI、OpenRouterなど）

## セットアップ手順

### 1. Discord Botの設定

1. [Discord Developer Portal](https://discord.com/developers/applications)にアクセス
2. 「New Application」をクリックして名前を付ける
3. 「Bot」タブに移動し、「Add Bot」をクリック
4. 「Privileged Gateway Intents」セクションで以下を有効化：
   - Message Content Intent
5. ボットトークンをコピー（`.env`ファイルに必要）
6. 「OAuth2」>「URL Generator」に移動
7. 以下のスコープを選択：
   - `bot`
   - `applications.commands`
8. 以下のボット権限を選択：
   - Send Messages（メッセージの送信）
   - Read Message History（メッセージ履歴の読み取り）
   - View Channels（チャンネルの表示）
   - Embed Links（埋め込みリンク）
   - Add Reactions（リアクションの追加）
9. 生成されたURLをコピーし、ボットをサーバーに招待

### 2. 環境のセットアップ

1. リポジトリをクローン：
   ```
   git clone https://github.com/yourusername/OpenHandsDiscordAdapter.git
   cd OpenHandsDiscordAdapter
   ```

2. 依存関係をインストール：
   ```
   pip install -r requirements.txt
   ```

3. `.env.example`を元に`.env`ファイルを作成：
   ```
   cp .env.example .env
   ```

4. `.env`ファイルを編集して設定：
   ```
   # Discord Bot設定
   DISCORD_TOKEN=あなたのDiscordボットトークン
   COMMAND_PREFIX=!oh 
   OPENHANDS_CHAT_CHANNEL=openhands-chat

   # OpenHands設定
   OPENHANDS_CLI_PATH=openhands.core.cli
   OPENHANDS_WORKDIR=./openhands_workspace

   # LLM設定
   LLM_API_KEY=あなたのLLM APIキー
   # 形式: プロバイダー/モデル名
   LLM_MODEL=anthropic/claude-3-5-sonnet-20241022

   # ランタイム設定
   SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.28-nikolaik

   # タスク設定
   MAX_CONCURRENT_TASKS=5
   TASK_TIMEOUT_SECONDS=300
   ```

### 3. サーバーのセットアップ

1. Discordサーバーに`openhands-chat`という名前のチャンネルを作成（または`.env`ファイルでカスタマイズ）
2. ボットがこのチャンネルでメッセージを読み書きする権限を持っていることを確認

### 4. ボットの実行

```
python -m src.__main__
```

ボットが正常にログインすると、ログメッセージが表示されます。

### 5. Windowsでサービスとして実行

Windowsでバックグラウンドサービスとして実行するには：

1. `start_bot.bat`バッチファイルを作成：
   ```batch
   @echo off
   echo OpenHandsDiscordAdapter Botを起動中...
   cd /d %~dp0
   python -m src.__main__
   if %ERRORLEVEL% NEQ 0 (
       echo ボットがエラーコード %ERRORLEVEL% でクラッシュしました
       echo 詳細はログを確認してください
       timeout /t 10
   )
   pause
   ```

2. タスクスケジューラで設定：
   - タスクスケジューラを開く
   - 新しいタスクを作成
   - スタートアップ時に実行するよう設定
   - アクション：プログラムの開始
   - プログラム/スクリプト：バッチファイルのパス
   - 開始（オプション）：プロジェクトディレクトリのパス

## 使用方法

### スラッシュコマンド

- `/help` - ヘルプ情報を表示
- `/task <説明>` - 新しいタスクを作成
- `/status [タスクID]` - タスクのステータスを確認
- `/tasks` - すべてのタスクを一覧表示

### プレフィックスコマンド

ボットは従来のプレフィックスコマンドもサポートしています：

- `!oh help` - ヘルプ情報を表示
- `!oh task <説明>` - 新しいタスクを作成
- `!oh status [タスクID]` - タスクのステータスを確認
- `!oh tasks` - すべてのタスクを一覧表示

### チャットモード

`openhands-chat`チャンネルでメッセージを送信するか、ボットにDMを送ることでOpenHandsとチャットできます。

## LLMプロバイダーの設定

アダプターは`LLM_MODEL`環境変数を通じて複数のLLMプロバイダーをサポートしています：

- Anthropic: `anthropic/claude-3-5-sonnet-20241022`
- OpenAI: `openai/gpt-4-turbo`
- OpenRouter: `openrouter/anthropic/claude-3-5-sonnet-20241022`

## トラブルシューティング

### ボットがメッセージに応答しない

- Discord Developer Portalで「Message Content Intent」が有効になっているか確認
- サーバーでボットが必要な権限を持っているか確認
- `.env`ファイルのDiscordトークンが正しいか確認

### OpenHands CLIのエラー

- OpenHands CLIがインストールされているか確認: `pip install openhands`
- ワークスペースディレクトリが存在し、書き込み可能か確認
- LLM APIキーが正しいか確認

### LLMプロバイダーの問題

- APIキーが有効で、十分なクレジットがあるか確認
- モデル名が`プロバイダー/モデル名`の形式で正しく設定されているか確認
- OpenRouterの場合は`openrouter/プロバイダー/モデル名`の形式を使用

## ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下で提供されています。

このプロジェクトは以下のオープンソースソフトウェアを使用しています：
- [OpenHands](https://github.com/All-Hands-AI/OpenHands) - MITライセンス
- [discord.py](https://github.com/Rapptz/discord.py) - MITライセンス

依存関係とライセンスの詳細については[CREDITS.md](CREDITS.md)を参照してください。 