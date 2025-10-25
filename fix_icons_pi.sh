#!/bin/bash
# Quick fix script for icon issues on Raspberry Pi
# Run this on your Pi: bash fix_icons_pi.sh

echo "========================================"
echo "ARC Icon Fix for Raspberry Pi"
echo "========================================"
echo ""

# Get the script directory (should be ARC root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "1. Checking directory structure..."
if [ -d "arc/assets/icons" ]; then
    ICON_COUNT=$(find arc/assets/icons -name "*.png" | wc -l)
    echo "   ✓ Icons directory found: arc/assets/icons"
    echo "   ✓ Icon files: $ICON_COUNT"
else
    echo "   ✗ Icons directory NOT found!"
    echo "   Expected: $SCRIPT_DIR/arc/assets/icons"
    
    # Check if old structure exists
    if [ -d "ARC_DE/icons" ]; then
        echo ""
        echo "   Found old icon location: ARC_DE/icons"
        echo "   Copying icons to new location..."
        mkdir -p arc/assets/icons
        cp -r ARC_DE/icons/* arc/assets/icons/
        echo "   ✓ Icons copied"
    fi
fi

echo ""
echo "2. Checking icon permissions..."
find arc/assets/icons -name "*.png" -exec chmod 644 {} \; 2>/dev/null
echo "   ✓ Permissions set to 644"

echo ""
echo "3. Listing some icon files..."
ls -lh arc/assets/icons/*.png 2>/dev/null | head -5

echo ""
echo "4. Checking config file..."
if [ -f "config/arc.yaml" ]; then
    echo "   ✓ Config found: config/arc.yaml"
else
    echo "   ✗ Config NOT found!"
    if [ -f "arc.yaml" ]; then
        echo "   Found config in root, moving to config/"
        mkdir -p config
        mv arc.yaml config/
    fi
fi

echo ""
echo "5. Running diagnostic..."
if [ -f "debug_icons.py" ]; then
    source venv/bin/activate 2>/dev/null || true
    python3 debug_icons.py
else
    echo "   debug_icons.py not found"
fi

echo ""
echo "========================================"
echo "Fix attempt complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Try running: python3 launcher.py"
echo "2. Check the console output for icon loading messages"
echo "3. If icons still don't load, send me the output"
echo ""

