#!/bin/bash
# Test script for run_app.sh
# Run this to verify the app launcher works

echo "=========================================="
echo "Testing run_app.sh"
echo "=========================================="
echo ""

# Get ARC root
cd "$(dirname "${BASH_SOURCE[0]}")"
ARC_ROOT="$(pwd)"

echo "ARC root: $ARC_ROOT"
echo ""

# Test 1: Check if run_app.sh exists
echo "Test 1: Check if run_app.sh exists"
if [ -f "run_app.sh" ]; then
    echo "  ✓ run_app.sh found"
else
    echo "  ✗ run_app.sh NOT found"
    exit 1
fi
echo ""

# Test 2: Check if run_app.sh is executable
echo "Test 2: Check if executable"
if [ -x "run_app.sh" ]; then
    echo "  ✓ run_app.sh is executable"
else
    echo "  ✗ run_app.sh is NOT executable"
    echo "  Fixing with: chmod +x run_app.sh"
    chmod +x run_app.sh
fi
echo ""

# Test 3: List available apps
echo "Test 3: Available app directories"
for dir in Chatbot Calendar_app BT_tools WIFI_tools Games Music_player NFC_tools IR_tools RF_tools Notes_app ARC_connect; do
    if [ -d "$dir" ]; then
        if [ -f "$dir/main.py" ]; then
            echo "  ✓ $dir (has main.py)"
        elif [ -f "$dir/ip.py" ]; then
            echo "  ✓ $dir (has ip.py)"
        else
            echo "  ⚠ $dir (no main.py or ip.py)"
        fi
    else
        echo "  ✗ $dir (not found)"
    fi
done
echo ""

# Test 4: Test run_app.sh with dry run
echo "Test 4: Dry run test"
echo "  Running: bash run_app.sh Chatbot main.py (will stop after finding file)"
echo ""

# Create a test that just checks if the script finds the file
if bash -c 'set -e; SCRIPT_DIR="$(pwd)"; APP_DIR="$1"; SCRIPT_NAME="$2"; APP_PATH="$SCRIPT_DIR/$APP_DIR/$SCRIPT_NAME"; if [ -f "$APP_PATH" ]; then echo "  ✓ Found: $APP_PATH"; exit 0; else echo "  ✗ Not found: $APP_PATH"; exit 1; fi' -- Chatbot main.py; then
    echo "  ✓ App file is accessible"
else
    echo "  ✗ App file not found"
fi
echo ""

# Test 5: Check virtual environment
echo "Test 5: Virtual environment"
if [ -d "venv" ]; then
    echo "  ✓ venv directory exists"
    if [ -f "venv/bin/activate" ]; then
        echo "  ✓ venv/bin/activate exists"
        source venv/bin/activate
        echo "  ✓ Virtual environment activated"
        echo "  Python: $(which python3)"
        echo "  Version: $(python3 --version)"
    else
        echo "  ✗ venv/bin/activate not found"
    fi
else
    echo "  ✗ venv directory not found"
    echo "  Create with: python3 -m venv venv"
fi
echo ""

echo "=========================================="
echo "Test Complete"
echo "=========================================="
echo ""
echo "To manually test an app, run:"
echo "  bash run_app.sh Chatbot main.py"
echo ""
echo "Or test from launcher:"
echo "  python3 launcher.py"
echo ""

