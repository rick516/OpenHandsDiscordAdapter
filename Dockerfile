# ビルドステージ
FROM python:3.11-slim AS builder

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 本番ステージ
FROM python:3.11-slim

WORKDIR /app

# 必要なパッケージのみをインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tini && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ビルドステージから依存関係をコピー
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# アプリケーションのコピー
COPY . .

# 非rootユーザーの作成と権限設定
RUN useradd -m appuser && \
    chown -R appuser:appuser /app
USER appuser

# Tiniをエントリーポイントとして使用
ENTRYPOINT ["/usr/bin/tini", "--"]

# アプリケーションの実行
CMD ["python", "-m", "src.__main__"] 