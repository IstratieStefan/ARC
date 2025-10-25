#!/bin/bash
# Quick Fix Script for ARC Icon and Config Issues
# Run this if you're experiencing icon loading problems after the reorganization
# Usage: bash quick_fix.sh

set -e  # Exit on error

echo "=========================================="
echo "ARC Quick Fix Script"
echo "=========================================="
echo ""

# Get script directory and cd to it
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Working directory: $SCRIPT_DIR"
echo ""

# 1. Fix icon location
echo "1. Checking icon files..."
if [ -d "ARC_DE/icons" ] && [ ! -d "arc/assets/icons" ]; then
  echo "   → Icons found in old location (ARC_DE/icons/)"
  echo "   → Creating new location (arc/assets/icons/)"
  mkdir -p arc/assets/icons
  cp -r ARC_DE/icons/* arc/assets/icons/
  echo "   ✓ Icons copied to arc/assets/icons/"
elif [ -d "arc/assets/icons" ]; then
  ICON_COUNT=$(find arc/assets/icons -name "*.png" 2>/dev/null | wc -l)
  echo "   ✓ Icons already in correct location (arc/assets/icons/)"
  echo "   ✓ Found $ICON_COUNT icon files"
else
  echo "   ✗ WARNING: No icons found in either location!"
  echo "   Please ensure icon files are present"
fi

echo ""

# 2. Fix config location
echo "2. Checking config file..."
if [ -f "arc.yaml" ] && [ ! -f "config/arc.yaml" ]; then
  echo "   → Config found in root (arc.yaml)"
  echo "   → Moving to config directory"
  mkdir -p config
  cp arc.yaml config/arc.yaml
  echo "   ✓ Config copied to config/arc.yaml"
elif [ -f "config/arc.yaml" ]; then
  echo "   ✓ Config already in correct location (config/arc.yaml)"
else
  echo "   ✗ WARNING: No config file found!"
fi

echo ""

# 3. Update config paths
echo "3. Updating config paths..."
if [ -f "config/arc.yaml" ]; then
  # Backup original
  cp config/arc.yaml config/arc.yaml.backup
  echo "   → Created backup: config/arc.yaml.backup"
  
  # Update icon paths
  sed -i.tmp 's|./ARC_DE/icons/|arc/assets/icons/|g' config/arc.yaml
  sed -i.tmp 's|ARC_DE/icons/|arc/assets/icons/|g' config/arc.yaml
  
  # Update font paths
  sed -i.tmp 's|./assets/fonts/|arc/assets/fonts/|g' config/arc.yaml
  sed -i.tmp 's|assets/fonts/|arc/assets/fonts/|g' config/arc.yaml
  
  # Update apps directory
  sed -i.tmp 's|apps_dir: ./apps|apps_dir: arc/apps|g' config/arc.yaml
  
  # Clean up temp files
  rm -f config/arc.yaml.tmp
  
  echo "   ✓ Config paths updated to new structure"
else
  echo "   ✗ Skipping: No config file found"
fi

echo ""

# 4. Fix fonts location
echo "4. Checking font files..."
if [ -d "assets/fonts" ] && [ ! -d "arc/assets/fonts" ]; then
  echo "   → Fonts found in old location (assets/fonts/)"
  echo "   → Creating new location (arc/assets/fonts/)"
  mkdir -p arc/assets/fonts
  cp -r assets/fonts/* arc/assets/fonts/
  echo "   ✓ Fonts copied to arc/assets/fonts/"
elif [ -d "arc/assets/fonts" ]; then
  FONT_COUNT=$(find arc/assets/fonts -name "*.ttf" 2>/dev/null | wc -l)
  echo "   ✓ Fonts already in correct location (arc/assets/fonts/)"
  echo "   ✓ Found $FONT_COUNT font files"
else
  echo "   ⚠ Fonts directory not found (this might be OK)"
fi

echo ""

# 5. Check directory structure
echo "5. Verifying new directory structure..."
DIRS_OK=0
DIRS_TOTAL=4

[ -d "arc/core" ] && echo "   ✓ arc/core/" && ((DIRS_OK++)) || echo "   ✗ arc/core/"
[ -d "arc/desktop" ] && echo "   ✓ arc/desktop/" && ((DIRS_OK++)) || echo "   ✗ arc/desktop/"
[ -d "arc/apps" ] && echo "   ✓ arc/apps/" && ((DIRS_OK++)) || echo "   ✗ arc/apps/"
[ -d "arc/assets" ] && echo "   ✓ arc/assets/" && ((DIRS_OK++)) || echo "   ✗ arc/assets/"

echo ""

# 6. Set permissions
echo "6. Setting permissions..."
if [ -d "arc/assets/icons" ]; then
  chmod -R 644 arc/assets/icons/*.png 2>/dev/null || true
  chmod 755 arc/assets/icons 2>/dev/null || true
  echo "   ✓ Icon permissions set"
fi

if [ -d "arc/assets/fonts" ]; then
  chmod -R 644 arc/assets/fonts/*.ttf 2>/dev/null || true
  chmod 755 arc/assets/fonts 2>/dev/null || true
  echo "   ✓ Font permissions set"
fi

echo ""

# 7. Summary
echo "=========================================="
echo "Fix Summary"
echo "=========================================="
echo ""
echo "Directory Structure: $DIRS_OK/$DIRS_TOTAL directories OK"

if [ -d "arc/assets/icons" ]; then
  ICON_COUNT=$(find arc/assets/icons -name "*.png" 2>/dev/null | wc -l)
  echo "Icons: $ICON_COUNT files in arc/assets/icons/"
else
  echo "Icons: ✗ NOT FOUND"
fi

if [ -f "config/arc.yaml" ]; then
  echo "Config: ✓ config/arc.yaml"
else
  echo "Config: ✗ NOT FOUND"
fi

echo ""
echo "=========================================="
echo "Fix Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the launcher: python3 launcher.py"
echo "3. Check console output for 'Successfully loaded icon' messages"
echo ""
echo "If you still have issues, run: python3 debug_icons.py"
echo ""

