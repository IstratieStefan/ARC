# ARC Launcher Auto-Start Setup

This guide explains how to make the ARC Launcher start automatically when your Raspberry Pi boots up.

## Quick Setup (Recommended)

Run the automated setup script:

```bash
cd ~/Github/ARC
chmod +x setup_autostart.sh
./setup_autostart.sh
```

The script will guide you through choosing the best auto-start method for your setup.

## Method 1: Desktop Autostart (Recommended for Desktop Use)

This method works well if you're running a desktop environment (LXDE, XFCE, etc.).

### Setup:

```bash
# Create autostart directory
mkdir -p ~/.config/autostart

# Copy the desktop entry
cp ~/Github/ARC/arc-launcher.desktop ~/.config/autostart/

# Make it executable
chmod +x ~/.config/autostart/arc-launcher.desktop
```

### To disable:

```bash
rm ~/.config/autostart/arc-launcher.desktop
```

## Method 2: Systemd Service (Recommended for Kiosk/Headless Mode)

This method is more robust and works well for kiosk setups or when you want better control.

### Setup:

```bash
# Copy service file
sudo cp ~/Github/ARC/arc-launcher.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable the service
sudo systemctl enable arc-launcher.service

# Start it now (optional, to test)
sudo systemctl start arc-launcher.service
```

### Useful Commands:

```bash
# Check status
sudo systemctl status arc-launcher

# View logs
sudo journalctl -u arc-launcher -f

# Stop the service
sudo systemctl stop arc-launcher

# Disable auto-start
sudo systemctl disable arc-launcher

# Restart the service
sudo systemctl restart arc-launcher
```

### To disable:

```bash
sudo systemctl stop arc-launcher
sudo systemctl disable arc-launcher
```

## Troubleshooting

### Launcher doesn't appear after reboot

1. **Check if X11 is running:**
   ```bash
   echo $DISPLAY
   ```
   Should output `:0` or similar.

2. **Check the logs (systemd method):**
   ```bash
   sudo journalctl -u arc-launcher -n 50
   ```

3. **Check autostart file (desktop method):**
   ```bash
   cat ~/.config/autostart/arc-launcher.desktop
   ```

4. **Test manually:**
   ```bash
   cd ~/Github/ARC
   source venv/bin/activate
   python launcher.py
   ```

### Permission issues

Make sure the files are executable:
```bash
chmod +x ~/Github/ARC/launcher.py
chmod +x ~/Github/ARC/setup_autostart.sh
```

### Display issues with systemd

If using systemd and the display doesn't work, try adding this to the service file:
```ini
Environment=XDG_RUNTIME_DIR=/run/user/1000
```

Or run it as a user service instead:
```bash
# Copy to user service directory
mkdir -p ~/.config/systemd/user
cp arc-launcher.service ~/.config/systemd/user/

# Enable user service
systemctl --user enable arc-launcher.service
systemctl --user start arc-launcher.service

# Enable lingering (allows user services to run at boot)
sudo loginctl enable-linger $USER
```

## Boot Directly to Launcher (Kiosk Mode)

If you want to boot directly to the launcher without seeing the desktop:

1. **Disable desktop auto-login to desktop:**
   ```bash
   sudo raspi-config
   # Go to: System Options -> Boot / Auto Login -> Console Autologin
   ```

2. **Use the systemd service method above**

3. **Or, edit ~/.bashrc to start on console login:**
   ```bash
   echo '
   # Start ARC Launcher on login to tty1
   if [ "$(tty)" = "/dev/tty1" ]; then
       startx ~/Github/ARC/launcher.py
   fi' >> ~/.bashrc
   ```

## Configuration Notes

- **Path**: The setup assumes your ARC project is in `~/Github/ARC`. If it's elsewhere, edit the paths in the service/desktop files.
- **User**: The systemd service runs as user `admin`. Change the `User=` line if your username is different.
- **Virtual Environment**: Both methods use the virtual environment at `~/Github/ARC/venv`.

## Testing Auto-Start

After setup, reboot to test:
```bash
sudo reboot
```

The launcher should appear automatically after boot.

