# ARC Quick Start Guide

## First Time Setup

### 1. Install Dependencies

```bash
cd /home/admin/ARC
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

# Copy icons (use whichever folder exists)
cp -r /home/admin/ARC/ARC_DE/icons/* /home/admin/Icons/ 2>/dev/null || \
cp -r /home/admin/ARC/arc/assets/icons/* /home/admin/Icons/
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
cd /home/admin/ARC
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
cd /home/admin/ARC && venv/bin/python arc/apps/music_player/main.py
```

Or any other app:
```bash
cd /home/admin/ARC && venv/bin/python arc/apps/chatbot/main.py
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
├── config/
│   └── arc.yaml            # Main configuration
├── venv/                   # Python virtual environment
│   └── bin/
│       └── python          # Python interpreter with all deps
├── arc/
│   ├── apps/               # All applications
│   │   ├── music_player/
│   │   ├── chatbot/
│   │   └── ... other apps
│   ├── assets/             # Icons and fonts
│   └── core/               # Core system files
└── ... documentation and setup files
```

## Configuration Files

- **`config/arc.yaml`** - Main config (icons, apps, colors, launch commands)
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
   grep "exec.*venv/bin/python" config/arc.yaml
   ```

2. Update paths:
   ```bash
   ./generate_config.sh
   ```

3. Test manually (copy exec command from config and run it):
   ```bash
   cd /home/admin/ARC && venv/bin/python arc/apps/music_player/main.py
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
cd /home/admin/ARC
git pull
./generate_config.sh
sudo systemctl restart arc-launcher  # if using systemd
```

### Reset Everything

```bash
cd /home/admin/ARC
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
✅ Apps launch directly with venv Python (no wrapper script)
✅ Icons should be in `/home/admin/Icons/` or update config
✅ Test apps work before setting up auto-start
✅ Each app runs in its own directory with PYTHONPATH set

Happy hacking! 🚀

