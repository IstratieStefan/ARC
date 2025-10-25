#!/bin/bash
# Generate arc.yaml with absolute paths for the current installation
# This ensures apps work from anywhere

set -e

# Get the directory where this script is located (ARC root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "ARC project root: $SCRIPT_DIR"

# Determine config location
CONFIG_FILE="$SCRIPT_DIR/config/arc.yaml"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found at $CONFIG_FILE"
    exit 1
fi

echo "Updating config file: $CONFIG_FILE"

# Create a backup
BACKUP_FILE="$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
cp "$CONFIG_FILE" "$BACKUP_FILE"
echo "Backup created: $BACKUP_FILE"

# Get the current user's home directory
USER_HOME="$HOME"

# Update the exec paths to use absolute paths
# This replaces /home/admin/ARC or /home/admin/Github/ARC with the actual current path
sed -i.tmp "s|/home/admin/ARC|$SCRIPT_DIR|g" "$CONFIG_FILE"
sed -i.tmp "s|/home/admin/Github/ARC|$SCRIPT_DIR|g" "$CONFIG_FILE"

# Clean up temp file
rm -f "$CONFIG_FILE.tmp"

echo ""
echo "✓ Config file updated successfully!"
echo ""
echo "Summary of changes:"
echo "  - All paths updated to use: $SCRIPT_DIR"
echo "  - Apps launch with venv Python: $SCRIPT_DIR/venv/bin/python"
echo "  - Backup saved to: $BACKUP_FILE"
echo ""
echo "Note: Icon paths may still need to be updated manually if not at /home/admin/Icons/"
echo "      Current icon path in config: /home/admin/Icons/"
echo ""

# Check if icons directory exists
if [ ! -d "/home/admin/Icons" ]; then
    echo "⚠ Warning: /home/admin/Icons/ directory not found!"
    echo ""
    echo "To set up icons, either:"
    echo "  1. Create the directory: sudo mkdir -p /home/admin/Icons"
    echo "  2. Copy icons: cp -r $SCRIPT_DIR/ARC_DE/icons/* /home/admin/Icons/"
    echo "  3. Or update the icon paths in $CONFIG_FILE to point to your icons"
fi

echo ""
echo "All apps will now launch correctly from anywhere using:"
echo "  - Format: cd $SCRIPT_DIR && venv/bin/python arc/apps/<app>/main.py"
echo "  - Virtual environment: $SCRIPT_DIR/venv/bin/python"
echo "  - Project root: $SCRIPT_DIR"

