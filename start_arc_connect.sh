#!/bin/bash
# ARC Connect Server Startup Script

echo "=== Starting ARC Connect Server ==="
echo ""

# Get the script's directory (works even if called from elsewhere)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create it first: python3 -m venv venv"
    exit 1
fi

# Check if dependencies are installed
if ! venv/bin/python -c "import fastapi, uvicorn, psutil" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    venv/bin/pip install fastapi uvicorn[standard] python-multipart websockets psutil
fi

# Get IP address
IP_ADDR=$(hostname -I | awk '{print $1}')

echo "🚀 Starting ARC Connect server..."
echo ""
echo "   Local:   http://localhost:5001/"
echo "   Network: http://$IP_ADDR:5001/"
echo ""
echo "   API Docs: http://$IP_ADDR:5001/docs"
echo ""
echo "📝 Logs: $SCRIPT_DIR/arc_connect.log"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
venv/bin/uvicorn arc.apps.connect.server:app \
    --host 0.0.0.0 \
    --port 5001 \
    --log-level info \
    2>&1 | tee arc_connect.log

