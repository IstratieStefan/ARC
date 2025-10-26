#!/bin/bash
# ARC Connect - Minimal Server Startup

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Error: venv not found"
    exit 1
fi

# Check dependencies
if ! venv/bin/python -c "import paramiko" 2>/dev/null; then
    echo "Installing paramiko..."
    venv/bin/pip install paramiko -q
fi

IP=$(hostname -I | awk '{print $1}')

echo "ARC Connect (Minimal Mode)"
echo ""
echo "  http://$IP:5001/"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run with minimal settings
venv/bin/python arc/apps/connect/server_minimal.py

