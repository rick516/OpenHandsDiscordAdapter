# Accept build arguments
ARG PYTHON_VERSION=3.12
ARG USE_UV=true

# ベースステージ
FROM python:${PYTHON_VERSION}-slim AS base

# ビルドステージ
FROM base AS builder

WORKDIR /app

# 依存関係ファイルのコピー
COPY requirements.txt requirements-dev.txt ./

# uvを使用する場合
RUN if [ "$USE_UV" = "true" ]; then \
        # uvのインストール
        apt-get update && \
        apt-get install -y --no-install-recommends curl && \
        curl -LsSf https://astral.sh/uv/install.sh | sh && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/* && \
        # uvの設定
        export UV_COMPILE_BYTECODE=1 && \
        export UV_LINK_MODE=copy && \
        # 依存関係のインストール
        uv pip install --no-cache-dir --upgrade pip && \
        uv pip install --no-cache-dir -r requirements.txt; \
    else \
        # 標準的なpipを使用
        pip install --no-cache-dir --upgrade pip && \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# アプリケーションのコピー
COPY . .

# 本番ステージ
FROM base

# 引数を本番ステージに渡す
ARG USE_UV=true

WORKDIR /app

# 必要なパッケージのみをインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends tini && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# uvを使用する場合は本番環境にもインストール
RUN if [ "$USE_UV" = "true" ]; then \
        apt-get update && \
        apt-get install -y --no-install-recommends curl && \
        curl -LsSf https://astral.sh/uv/install.sh | sh && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/*; \
    fi

# ビルドステージから依存関係をコピー
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# アプリケーションのコピー
COPY --from=builder /app /app

# 非rootユーザーの作成と権限設定
RUN useradd -m appuser && \
    chown -R appuser:appuser /app
USER appuser

# Tiniをエントリーポイントとして使用
ENTRYPOINT ["/usr/bin/tini", "--"]

# アプリケーションの実行
CMD ["python", "-m", "src.__main__"] 