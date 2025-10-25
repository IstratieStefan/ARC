#!/bin/bash
# Setup script to enable ARC Launcher auto-start on boot

set -e

echo "=========================================="
echo "ARC Launcher Auto-Start Setup"
echo "=========================================="
echo ""

# Get the actual project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"

echo "Project directory: $PROJECT_DIR"
echo ""

# Ask user which method they prefer
echo "Choose auto-start method:"
echo "1) Desktop Autostart (recommended for desktop environments)"
echo "2) Systemd Service (recommended for headless/kiosk mode)"
echo "3) Both"
echo ""
read -p "Enter your choice (1/2/3): " choice

case $choice in
    1|3)
        echo ""
        echo "Setting up Desktop Autostart..."
        
        # Create autostart directory if it doesn't exist
        mkdir -p ~/.config/autostart
        
        # Copy and modify the desktop entry with actual paths
        sed "s|/home/admin/Github/ARC|$PROJECT_DIR|g" "$PROJECT_DIR/arc-launcher.desktop" > ~/.config/autostart/arc-launcher.desktop
        chmod +x ~/.config/autostart/arc-launcher.desktop
        
        echo "✓ Desktop autostart entry created at ~/.config/autostart/arc-launcher.desktop"
        ;;
esac

case $choice in
    2|3)
        echo ""
        echo "Setting up Systemd Service..."
        
        # Copy and modify the service file with actual paths and user
        CURRENT_USER=$(whoami)
        SERVICE_FILE="/tmp/arc-launcher.service"
        
        sed -e "s|/home/admin/Github/ARC|$PROJECT_DIR|g" \
            -e "s|User=admin|User=$CURRENT_USER|g" \
            -e "s|XAUTHORITY=/home/admin/.Xauthority|XAUTHORITY=$HOME/.Xauthority|g" \
            "$PROJECT_DIR/arc-launcher.service" > "$SERVICE_FILE"
        
        echo "Installing systemd service (requires sudo)..."
        sudo cp "$SERVICE_FILE" /etc/systemd/system/arc-launcher.service
        sudo systemctl daemon-reload
        sudo systemctl enable arc-launcher.service
        
        echo "✓ Systemd service installed and enabled"
        echo ""
        echo "Service commands:"
        echo "  Start:   sudo systemctl start arc-launcher"
        echo "  Stop:    sudo systemctl stop arc-launcher"
        echo "  Status:  sudo systemctl status arc-launcher"
        echo "  Logs:    sudo journalctl -u arc-launcher -f"
        ;;
esac

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""

if [ "$choice" == "1" ] || [ "$choice" == "3" ]; then
    echo "Desktop autostart is now enabled."
    echo "The launcher will start automatically when you log in."
    echo ""
    echo "To disable: rm ~/.config/autostart/arc-launcher.desktop"
fi

if [ "$choice" == "2" ] || [ "$choice" == "3" ]; then
    echo "Systemd service is now enabled."
    echo "The launcher will start automatically on boot."
    echo ""
    echo "To disable: sudo systemctl disable arc-launcher"
fi

echo ""
echo "Reboot your Raspberry Pi to test the auto-start."

