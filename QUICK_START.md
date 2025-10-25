# ARC Quick Start Guide

## First Time Setup

### 1. Install Dependencies

```bash
cd ~/Github/ARC
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# On Linux/Raspberry Pi only:
pip install -r requirements-linux.txt
```

### 2. Set Up Icons

```bash
# Create icons directory
sudo mkdir -p /home/admin/Icons

# Copy icons
cp -r ARC_DE/icons/* /home/admin/Icons/
```

### 3. Configure Paths

If your ARC is **not** at `/home/admin/Github/ARC/`:

```bash
./generate_config.sh
```

This updates all app launch paths to use your actual installation location.

### 4. Set Up Auto-Start (Optional)

```bash
./setup_autostart.sh
```

Choose your preferred method when prompted.

## Running ARC

### From Terminal

```bash
cd ~/Github/ARC
source venv/bin/activate
python launcher.py
```

### After Auto-Start Setup

Just reboot - ARC will launch automatically!

```bash
sudo reboot
```

## Testing Apps

### Test Individual App

```bash
./run_app.sh music_player main.py
./run_app.sh Chatbot main.py
```

### Verify Icons Work

```bash
python test_icons.py
```

## Common Commands

### View Logs (if using systemd)

```bash
sudo journalctl -u arc-launcher -f
```

### Stop/Start Service

```bash
sudo systemctl stop arc-launcher
sudo systemctl start arc-launcher
sudo systemctl status arc-launcher
```

### Update From Git

```bash
cd ~/Github/ARC
git pull
./generate_config.sh  # Update paths after pull
sudo systemctl restart arc-launcher  # If using systemd
```

## File Structure

```
ARC/
├── launcher.py              # Main launcher
├── run_app.sh              # App wrapper script
├── config/
│   └── arc.yaml            # Main configuration
├── venv/                   # Python virtual environment
├── music_player/           # Example app
│   └── main.py
├── Chatbot/
│   └── main.py
└── ... other apps
```

## Configuration Files

- **`config/arc.yaml`** - Main config (icons, apps, colors)
- **`run_app.sh`** - Launches apps with correct environment
- **`setup_autostart.sh`** - Sets up auto-start on boot
- **`generate_config.sh`** - Updates paths for your installation

## Troubleshooting

### Icons Don't Load

1. Check icon directory exists:
   ```bash
   ls /home/admin/Icons/
   ```

2. If not, copy icons:
   ```bash
   sudo mkdir -p /home/admin/Icons
   cp -r ARC_DE/icons/* /home/admin/Icons/
   ```

3. Run diagnostic:
   ```bash
   python test_icons.py
   ```

### Apps Don't Launch

1. Check paths in config:
   ```bash
   grep "exec.*run_app.sh" config/arc.yaml
   ```

2. Update paths:
   ```bash
   ./generate_config.sh
   ```

3. Test manually:
   ```bash
   ./run_app.sh music_player main.py
   ```

### Auto-Start Doesn't Work

1. Check service status:
   ```bash
   sudo systemctl status arc-launcher
   ```

2. View logs:
   ```bash
   sudo journalctl -u arc-launcher -n 50
   ```

3. Test display variable:
   ```bash
   echo $DISPLAY
   ```

## Documentation

- **[APP_LAUNCHING.md](APP_LAUNCHING.md)** - How app launching works
- **[AUTOSTART.md](AUTOSTART.md)** - Auto-start setup details
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and fixes
- **[SETUP.md](SETUP.md)** - Detailed installation guide

## Quick Fixes

### After Git Pull

```bash
cd ~/Github/ARC
git pull
./generate_config.sh
sudo systemctl restart arc-launcher  # if using systemd
```

### Reset Everything

```bash
cd ~/Github/ARC
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-linux.txt  # Linux only
./generate_config.sh
```

## Support

For issues, check:
1. `TROUBLESHOOTING.md` - Common problems
2. GitHub Issues - Report bugs
3. Official docs - Detailed documentation

## Key Points

✅ Always use absolute paths in config
✅ Run `generate_config.sh` after moving the project
✅ Apps launch via `run_app.sh` which activates venv automatically
✅ Icons should be in `/home/admin/Icons/` or update config
✅ Test apps work before setting up auto-start

Happy hacking! 🚀

