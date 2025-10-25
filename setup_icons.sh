#!/bin/bash
# Setup Icons folder with proper structure
# Run this on your Raspberry Pi to organize icons

cd "$(dirname "$0")"
ARC_ROOT="$(pwd)"

echo "=========================================="
echo "Setting up Icons folder"
echo "=========================================="
echo ""
echo "ARC Root: $ARC_ROOT"
echo ""

# Create Icons directory structure
echo "1. Creating directory structure..."
mkdir -p Icons/topbar
echo "   ✓ Icons/"
echo "   ✓ Icons/topbar/"
echo ""

# Copy icons from old location if they exist
echo "2. Looking for existing icons..."

if [ -d "ARC_DE/icons" ]; then
    echo "   Found: ARC_DE/icons/"
    echo "   Copying app icons..."
    cp ARC_DE/icons/*.png Icons/ 2>/dev/null || true
    echo "   Copying topbar icons..."
    cp ARC_DE/icons/topbar/*.png Icons/topbar/ 2>/dev/null || true
    COPIED=$(ls Icons/*.png 2>/dev/null | wc -l)
    echo "   ✓ Copied $COPIED app icons"
elif [ -d "arc/assets/icons" ]; then
    echo "   Found: arc/assets/icons/"
    echo "   Copying app icons..."
    cp arc/assets/icons/*.png Icons/ 2>/dev/null || true
    echo "   Copying topbar icons..."
    cp arc/assets/icons/topbar/*.png Icons/topbar/ 2>/dev/null || true
    COPIED=$(ls Icons/*.png 2>/dev/null | wc -l)
    echo "   ✓ Copied $COPIED app icons"
else
    echo "   ⚠ No existing icon directories found"
    echo "   Please copy your icon files to Icons/"
fi
echo ""

# List what we have
echo "3. Checking Icons folder contents..."
ICON_COUNT=$(ls Icons/*.png 2>/dev/null | wc -l)
TOPBAR_COUNT=$(ls Icons/topbar/*.png 2>/dev/null | wc -l)

echo "   App icons: $ICON_COUNT files"
if [ $ICON_COUNT -gt 0 ]; then
    ls Icons/*.png 2>/dev/null | head -5 | sed 's/^/      /'
    if [ $ICON_COUNT -gt 5 ]; then
        echo "      ... and $((ICON_COUNT - 5)) more"
    fi
fi

echo ""
echo "   Topbar icons: $TOPBAR_COUNT files"
if [ $TOPBAR_COUNT -gt 0 ]; then
    ls Icons/topbar/*.png 2>/dev/null | sed 's/^/      /'
fi
echo ""

# Check for required icons
echo "4. Verifying required icons..."
REQUIRED_ICONS=(
    "terminal.png"
    "AI.png"
    "calendar.png"
    "rf.png"
    "ir.png"
    "nfc.png"
    "wifi_tools.png"
    "bluetooth_tools.png"
    "files.png"
    "editor.png"
    "music.png"
    "games.png"
    "arc_connect.png"
)

MISSING=0
for icon in "${REQUIRED_ICONS[@]}"; do
    if [ -f "Icons/$icon" ]; then
        echo "   ✓ $icon"
    else
        echo "   ✗ $icon (missing)"
        ((MISSING++))
    fi
done
echo ""

# Check topbar icons
TOPBAR_ICONS=(
    "battery.png"
    "cellular.png"
    "wifi_0.png"
    "wifi_1.png"
    "wifi_2.png"
    "wifi_3.png"
    "wifi_4.png"
    "bluetooth_on.png"
    "bluetooth_off.png"
    "bluetooth_connected.png"
)

echo "5. Verifying topbar icons..."
TOPBAR_MISSING=0
for icon in "${TOPBAR_ICONS[@]}"; do
    if [ -f "Icons/topbar/$icon" ]; then
        echo "   ✓ topbar/$icon"
    else
        echo "   ✗ topbar/$icon (missing)"
        ((TOPBAR_MISSING++))
    fi
done
echo ""

# Summary
echo "=========================================="
echo "Setup Summary"
echo "=========================================="
echo ""
echo "Directory: $ARC_ROOT/Icons/"
echo "App icons: $ICON_COUNT files ($MISSING missing)"
echo "Topbar icons: $TOPBAR_COUNT files ($TOPBAR_MISSING missing)"
echo ""

if [ $MISSING -eq 0 ] && [ $TOPBAR_MISSING -eq 0 ]; then
    echo "✓ All icons present!"
    echo ""
    echo "Now run:"
    echo "  python3 launcher.py"
else
    echo "⚠ Some icons are missing"
    echo ""
    echo "To fix:"
    if [ -d "ARC_DE/icons" ]; then
        echo "  1. Copy missing icons from ARC_DE/icons/ to Icons/"
        echo "     cp ARC_DE/icons/*.png Icons/"
        echo "     cp ARC_DE/icons/topbar/*.png Icons/topbar/"
    elif [ -d "arc/assets/icons" ]; then
        echo "  1. Copy missing icons from arc/assets/icons/ to Icons/"
        echo "     cp arc/assets/icons/*.png Icons/"
        echo "     cp arc/assets/icons/topbar/*.png Icons/topbar/"
    else
        echo "  1. Find your icon files and copy them to Icons/"
    fi
    echo ""
    echo "  2. Re-run this script to verify:"
    echo "     bash setup_icons.sh"
fi
echo ""

# Set permissions
echo "6. Setting permissions..."
chmod 644 Icons/*.png 2>/dev/null || true
chmod 644 Icons/topbar/*.png 2>/dev/null || true
echo "   ✓ Permissions set"
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="

