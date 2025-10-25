#!/bin/bash
# App launcher wrapper that ensures correct working directory
# Usage: bash run_app.sh <app_directory> <script_name>
# Example: bash run_app.sh Chatbot main.py

set -e  # Exit on error

# Get the directory where this script is located (ARC root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "[run_app] ARC root: $SCRIPT_DIR"

# Get app parameters
APP_DIR="$1"
SCRIPT_NAME="$2"

if [ -z "$APP_DIR" ] || [ -z "$SCRIPT_NAME" ]; then
    echo "Error: Missing arguments"
    echo "Usage: $0 <app_directory> <script_name>"
    echo "Example: $0 Chatbot main.py"
    exit 1
fi

# Full path to app
APP_PATH="$SCRIPT_DIR/$APP_DIR/$SCRIPT_NAME"
echo "[run_app] Looking for: $APP_PATH"

# Check if app exists
if [ ! -f "$APP_PATH" ]; then
    echo "[run_app] Error: $APP_PATH not found"
    echo "[run_app] Available directories in $SCRIPT_DIR:"
    ls -d "$SCRIPT_DIR"/*/ 2>/dev/null | head -10 || echo "  (none found)"
    exit 1
fi

# Activate virtual environment if it exists
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    echo "[run_app] Activating virtual environment..."
    source "$SCRIPT_DIR/venv/bin/activate"
else
    echo "[run_app] Warning: No virtual environment found at $SCRIPT_DIR/venv"
fi

# Add ARC root to Python path
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Change to app directory and run
echo "[run_app] Changing to: $SCRIPT_DIR/$APP_DIR"
cd "$SCRIPT_DIR/$APP_DIR"

echo "[run_app] Running: python3 $SCRIPT_NAME"
exec python3 "$SCRIPT_NAME"

