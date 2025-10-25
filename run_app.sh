#!/bin/bash
# App launcher wrapper that ensures correct working directory
# Usage: bash run_app.sh <app_directory> <script_name>

# Get the directory where this script is located (ARC root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to ARC root
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Run the app
APP_DIR="$1"
SCRIPT_NAME="$2"

if [ -z "$APP_DIR" ] || [ -z "$SCRIPT_NAME" ]; then
    echo "Usage: $0 <app_directory> <script_name>"
    exit 1
fi

if [ -f "$APP_DIR/$SCRIPT_NAME" ]; then
    cd "$APP_DIR"
    python3 "$SCRIPT_NAME"
else
    echo "Error: $APP_DIR/$SCRIPT_NAME not found"
    exit 1
fi

