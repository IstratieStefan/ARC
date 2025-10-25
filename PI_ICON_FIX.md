# Fixing Icon Issues on Raspberry Pi Zero 2W

If icons aren't loading on your Raspberry Pi, follow these steps:

## Quick Fix (Recommended)

### Step 1: Run the diagnostic script

```bash
cd ~/ARC  # or wherever you installed ARC
python3 debug_icons.py
```

This will show you:
- Where the system is looking for icons
- Which paths are being resolved
- What icons exist
- Any loading errors

### Step 2: Run the fix script

```bash
bash fix_icons_pi.sh
```

This will:
- Check if icons are in the correct location
- Fix permissions
- Move icons if needed
- Run diagnostics

### Step 3: Test the launcher

```bash
source venv/bin/activate
python3 launcher.py
```

Watch the console output - you should see messages like:
```
AppIcon: Loading 'Terminal'
  Path: /home/pi/ARC/arc/assets/icons/terminal.png
  Absolute: /home/pi/ARC/arc/assets/icons/terminal.png
  Exists: True
  ✓ Successfully loaded icon
```

---

## Manual Fix

If the scripts don't work, try these manual steps:

### 1. Verify icon files exist

```bash
cd ~/ARC
ls -la arc/assets/icons/
```

You should see 70+ PNG files including:
- terminal.png
- AI.png
- calendar.png
- wifi_tools.png
- etc.

**If the directory doesn't exist:**
```bash
# Icons might still be in old location
ls -la ARC_DE/icons/

# If found, move them:
mkdir -p arc/assets/icons
cp -r ARC_DE/icons/* arc/assets/icons/
```

### 2. Check file permissions

```bash
chmod -R 644 arc/assets/icons/*.png
chmod 755 arc/assets/icons
```

### 3. Verify config file location

```bash
ls -la config/arc.yaml
```

**If not found:**
```bash
# Check if it's in the root
ls -la arc.yaml

# If found in root, move it:
mkdir -p config
mv arc.yaml config/
```

### 4. Check Python can find the files

```bash
cd ~/ARC
source venv/bin/activate
python3 -c "
import os
print('Project root:', os.getcwd())
print('Icons dir exists:', os.path.exists('arc/assets/icons'))
print('Terminal icon exists:', os.path.exists('arc/assets/icons/terminal.png'))
"
```

### 5. Test config loading

```bash
python3 -c "
from arc.core import config
print('Config loaded from:', config._config_path)
print('Base dir:', config._base_dir)
print('Terminal icon:', config.builtin_apps[0]['icon'])
import os
print('Icon exists:', os.path.exists(config.builtin_apps[0]['icon']))
"
```

---

## Common Issues & Solutions

### Issue 1: "Icons directory not found"

**Cause:** Icons weren't moved to new location during reorganization.

**Solution:**
```bash
cd ~/ARC
mkdir -p arc/assets/icons
cp -r ARC_DE/icons/* arc/assets/icons/
```

### Issue 2: "Permission denied" errors

**Cause:** Icon files don't have read permissions.

**Solution:**
```bash
chmod -R 644 arc/assets/icons/*.png
```

### Issue 3: Paths show old locations (./ARC_DE/icons/)

**Cause:** Using old config file.

**Solution:**
```bash
# Pull latest config
cd ~/ARC
git pull

# Or manually update config/arc.yaml
# Change all paths from ./ARC_DE/icons/ to arc/assets/icons/
```

### Issue 4: Icons show as gray boxes with letters

**Cause:** Icon files not found, placeholders shown instead.

**Solution:** This means the path resolution is working, but files don't exist. Check:
```bash
cd ~/ARC
# See what the launcher is looking for
python3 launcher.py 2>&1 | grep "AppIcon:"
```

Look for lines showing where it's trying to load icons from.

### Issue 5: "pygame.error: Couldn't open..."

**Cause:** Corrupted icon file or wrong file format.

**Solution:**
```bash
# Check file types
file arc/assets/icons/*.png | head

# Should all say "PNG image data"
# If not, re-download or regenerate that icon
```

---

## Debug Output Explained

When you run the launcher, you'll see output like this:

### ✅ GOOD - Icon loads successfully:
```
AppIcon: Loading 'Terminal'
  Path: arc/assets/icons/terminal.png
  Absolute: /home/pi/ARC/arc/assets/icons/terminal.png
  Exists: True
  ✓ Successfully loaded icon
```

### ❌ BAD - Icon not found:
```
AppIcon: Loading 'Terminal'
  Path: arc/assets/icons/terminal.png
  Absolute: /home/pi/ARC/arc/assets/icons/terminal.png
  Exists: False
  WARNING: Icon file not found!
```
**Solution:** The file doesn't exist. Copy it from the ARC_DE/icons/ directory.

### ❌ BAD - Wrong path resolution:
```
AppIcon: Loading 'Terminal'
  Path: ./ARC_DE/icons/terminal.png
  Absolute: /home/pi/ARC/ARC_DE/icons/terminal.png
  Exists: False
  WARNING: Icon file not found!
```
**Solution:** Your config file has old paths. Update config/arc.yaml.

---

## After Fixing

Once fixed, you should see:
1. All icons load with "✓ Successfully loaded icon"
2. No "WARNING: Icon file not found!" messages
3. Icons display in the launcher (not gray boxes)

---

## Still Having Issues?

If icons still don't load after trying everything:

### 1. Capture full diagnostic output:
```bash
cd ~/ARC
python3 debug_icons.py > icon_debug.txt 2>&1
python3 launcher.py > launcher_debug.txt 2>&1
```

### 2. Check what files you have:
```bash
cd ~/ARC
find . -name "*.png" | grep -E "(icon|Icon)" > icon_files.txt
```

### 3. Send me these files:
- `icon_debug.txt`
- `launcher_debug.txt`
- `icon_files.txt`

And I'll help you fix it!

---

## Prevention

To avoid this issue after updates:

```bash
# Always pull with submodules
cd ~/ARC
git pull

# If icons get moved, the fix script will handle it
bash fix_icons_pi.sh
```

---

## Quick Reference

```bash
# Navigate to ARC directory
cd ~/ARC

# Run diagnostic
python3 debug_icons.py

# Run fix
bash fix_icons_pi.sh

# Activate environment
source venv/bin/activate

# Run launcher (with debug output)
python3 launcher.py

# Check icon files
ls -la arc/assets/icons/ | wc -l  # Should show 70+

# Check config
cat config/arc.yaml | grep "icon:"
```

---

**Pro Tip:** The new code creates placeholder icons (gray boxes with letters) when files are missing, so the launcher won't crash - you'll just see letter placeholders instead of actual icons.

