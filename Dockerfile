# Accept build arguments
ARG PYTHON_VERSION=3.12
ARG USE_UV=true

# ビルドステージ
FROM python:${PYTHON_VERSION}-slim AS builder

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
COPY requirements-dev.txt .

# Install uv package manager if USE_UV is true
RUN if [ "$USE_UV" = "true" ]; then \
        apt-get update && \
        apt-get install -y --no-install-recommends curl && \
        curl -sSf https://astral.sh/uv/install.sh | sh && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/* && \
        uv pip install --no-cache-dir --upgrade pip && \
        uv pip install --no-cache-dir -r requirements.txt; \
    else \
        pip install --no-cache-dir --upgrade pip && \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# 本番ステージ
FROM python:${PYTHON_VERSION}-slim

# Pass the build arguments to this stage
ARG USE_UV=true

WORKDIR /app

# 必要なパッケージのみをインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends tini && \
    if [ "$USE_UV" = "true" ]; then \
        apt-get install -y --no-install-recommends curl && \
        curl -sSf https://astral.sh/uv/install.sh | sh; \
    fi && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ビルドステージから依存関係をコピー
COPY --from=builder /usr/local/lib/python${PYTHON_VERSION}/site-packages /usr/local/lib/python${PYTHON_VERSION}/site-packages
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