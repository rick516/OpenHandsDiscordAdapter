#!/bin/bash
set -e

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    curl -sSf https://astral.sh/uv/install.sh | sh
    echo "uv installed successfully!"
else
    echo "uv is already installed."
fi

# Create a virtual environment using uv
echo "Creating virtual environment with uv..."
uv venv

# Activate the virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies using uv
echo "Installing dependencies with uv..."
uv pip install -r requirements.txt

# Install development dependencies if needed
if [ "$1" == "--dev" ]; then
    echo "Installing development dependencies..."
    uv pip install -r requirements-dev.txt
fi

# Generate lock file
echo "Generating lock file..."
uv pip freeze > requirements.lock

echo "Setup completed successfully!"
echo "To activate the virtual environment, run: source .venv/bin/activate" 