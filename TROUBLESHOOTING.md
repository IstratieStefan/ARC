# ARC Troubleshooting Guide

Common issues and their solutions.

## Quick Fixes

### Icons Not Loading

**Symptoms:**
- Error: "File is not a Windows BMP file"
- Icons show as gray boxes with letters
- Errors mention `./ARC_DE/icons/` paths

**Solution:**
```bash
cd ~/ARC
bash quick_fix.sh
```

This automatically:
- Moves icons to correct location
- Updates config paths
- Fixes permissions
- Verifies structure

### After Git Pull Issues

If things break after `git pull`:

```bash
cd ~/ARC
bash quick_fix.sh
source venv/bin/activate
python3 launcher.py
```

---

## Platform-Specific Issues

### Raspberry Pi / Linux

#### Icons Not Displaying
```bash
# Check if files exist
ls -la arc/assets/icons/

# If empty, run fix
bash quick_fix.sh

# Check permissions
chmod -R 644 arc/assets/icons/*.png
```

#### Permission Denied Errors
```bash
# For network features
sudo python3 launcher.py

# Or add user to groups
sudo usermod -aG netdev,bluetooth $USER
```

#### Display Issues
```bash
# If screen is black
export DISPLAY=:0
python3 launcher.py

# For framebuffer
sudo python3 launcher.py
```

### macOS

#### Module Not Found
```bash
# Ensure virtual environment is activated
source venv/bin/activate
python3 launcher.py
```

#### Icons Not Loading
```bash
# Same fix works on macOS
bash quick_fix.sh
```

---

## Common Errors

### Error: "No module named 'arc'"

**Cause:** Running from wrong directory or venv not activated.

**Solution:**
```bash
cd ~/ARC  # Or your ARC installation directory
source venv/bin/activate
python3 launcher.py
```

### Error: "Config file not found"

**Cause:** Config in wrong location.

**Solution:**
```bash
bash quick_fix.sh
# Or manually:
mkdir -p config
cp arc.yaml config/ 2>/dev/null || true
```

### Error: pygame.error on icon loading

**Cause:** Icon files missing or wrong paths in config.

**Solution:**
```bash
# Run diagnostic
python3 debug_icons.py

# Run fix
bash quick_fix.sh
```

### Error: "python-uinput" not found (macOS)

**Cause:** This is a Linux-only library.

**Solution:** This is normal on macOS. The library is only needed for hardware keyboard integration on Linux devices. Development works fine without it.

---

## Diagnostic Tools

### Check Icon Status
```bash
python3 debug_icons.py
```

Shows:
- Where system looks for icons
- Which paths resolve correctly
- What files exist
- Loading errors

### Check Structure
```bash
ls -la arc/
```

Should show:
```
arc/
├── core/
├── desktop/
├── apps/
└── assets/
```

### Check Config
```bash
cat config/arc.yaml | grep "icon:"
```

Paths should look like:
```yaml
icon: arc/assets/icons/terminal.png  # ✓ Correct
icon: ./ARC_DE/icons/terminal.png    # ✗ Old path
```

---

## Manual Fixes

### Manually Update Config Paths

If `quick_fix.sh` doesn't work:

```bash
cd ~/ARC
nano config/arc.yaml
```

Replace all instances of:
- `./ARC_DE/icons/` → `arc/assets/icons/`
- `./assets/fonts/` → `arc/assets/fonts/`
- `./apps` → `arc/apps`

### Manually Move Icons

```bash
cd ~/ARC
mkdir -p arc/assets/icons
cp -r ARC_DE/icons/* arc/assets/icons/
chmod -R 644 arc/assets/icons/*.png
```

### Manually Move Fonts

```bash
cd ~/ARC
mkdir -p arc/assets/fonts
cp -r assets/fonts/* arc/assets/fonts/
chmod -R 644 arc/assets/fonts/*.ttf
```

---

## Performance Issues

### Slow Startup

**Cause:** Loading many apps or large icons.

**Solution:**
- Reduce number of builtin apps in config
- Optimize icon sizes (recommended: 64x64 or 128x128 pixels)

### Laggy UI

**Cause:** Underpowered hardware or high FPS setting.

**Solution:**
Edit `config/arc.yaml`:
```yaml
screen:
  fps: 30  # Lower if needed (try 20 or 15)
```

---

## Network Feature Issues

### WiFi Scanning Not Working

**Linux:**
```bash
# Check if tools installed
which nmcli
which iwlist

# Install if missing
sudo apt install wireless-tools network-manager
```

**macOS:**
```bash
# Check airport utility exists
ls /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport
```

### Bluetooth Not Working

**Linux:**
```bash
# Check bluetooth service
sudo systemctl status bluetooth

# Start if stopped
sudo systemctl start bluetooth

# Install tools
sudo apt install bluez
```

---

## Getting Help

If you're still having issues:

1. **Run diagnostics:**
   ```bash
   python3 debug_icons.py > diagnostic.txt 2>&1
   python3 launcher.py > launcher.txt 2>&1
   ```

2. **Collect info:**
   ```bash
   uname -a > system_info.txt
   python3 --version >> system_info.txt
   ls -la arc/ >> system_info.txt
   ```

3. **Open an issue** on GitHub with:
   - The diagnostic output files
   - Your system info
   - Steps you've already tried

---

## Prevention

### Keep Things Working

```bash
# Before pulling updates
cd ~/ARC
git status  # Check for local changes

# After pulling
bash quick_fix.sh  # Fix any path issues
```

### Backup Your Config

```bash
cp config/arc.yaml config/arc.yaml.backup
```

### Use Virtual Environment

Always activate before running:
```bash
source venv/bin/activate
```

---

## Quick Reference

```bash
# Fix everything
bash quick_fix.sh

# Diagnose issues
python3 debug_icons.py

# Check structure
ls -la arc/

# Run launcher
source venv/bin/activate && python3 launcher.py

# View logs
python3 launcher.py 2>&1 | tee launcher.log
```

---

**Still stuck? Check [PI_ICON_FIX.md](PI_ICON_FIX.md) for detailed icon troubleshooting.**



