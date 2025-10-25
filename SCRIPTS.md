# ARC Helper Scripts

This document lists all helper scripts available in the ARC repository.

---

## 🚀 Quick Fix Scripts

### `quick_fix.sh` - Main Fix Script

**Purpose:** Automatically fixes common issues after updates or reorganization.

**Usage:**
```bash
bash quick_fix.sh
```

**What it does:**
- ✅ Moves icons from old to new location
- ✅ Moves config to correct directory
- ✅ Updates all paths in config file
- ✅ Copies fonts to new location
- ✅ Sets correct permissions
- ✅ Verifies directory structure

**When to use:**
- After pulling updates
- When icons don't load
- When seeing "File is not a Windows BMP file" errors
- After reorganization

---

### `fix_icons_pi.sh` - Raspberry Pi Icon Fix

**Purpose:** Specifically for fixing icon issues on Raspberry Pi.

**Usage:**
```bash
bash fix_icons_pi.sh
```

**What it does:**
- ✅ Checks directory structure
- ✅ Fixes icon permissions
- ✅ Moves icons if needed
- ✅ Runs diagnostics
- ✅ Provides next steps

**When to use:**
- Running on Raspberry Pi / Linux
- Icons showing as gray boxes
- Path-related errors

---

## 🔍 Diagnostic Scripts

### `debug_icons.py` - Icon Diagnostic Tool

**Purpose:** Diagnoses icon loading issues with detailed output.

**Usage:**
```bash
python3 debug_icons.py
```

**What it shows:**
- Project root directory
- Icon directory location and contents
- Config loading status
- Icon path resolution
- File existence checks
- Pygame loading tests

**Output example:**
```
==========================================
ARC Icon Path Debugger
==========================================

1. Project Root: /home/pi/ARC

2. Icons Directory: /home/pi/ARC/arc/assets/icons
   Exists: True
   Is Directory: True
   Icon count: 72

3. Testing Config Loading:
   ✓ Config loaded successfully

4. Testing Icon Paths in Config:
   wifi_locked: arc/assets/icons/wifi_locked.png
      Exists: True
```

**When to use:**
- Before running fixes (to see what's wrong)
- After fixes (to verify they worked)
- When reporting bugs

---

## 📦 Installation Scripts

### `requirements.txt` - Python Dependencies

**Purpose:** Lists all Python packages needed.

**Usage:**
```bash
pip install -r requirements.txt
```

**Packages:**
- pygame - Graphics and UI
- numpy - Numerical operations
- mutagen - Audio metadata
- requests - HTTP requests
- flask - Web server
- And more...

---

## 🛠️ Using the Scripts Together

### First Time Setup
```bash
# 1. Clone repository
git clone https://github.com/IstratieStefan/ARC.git
cd ARC

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run quick fix (in case of old checkout)
bash quick_fix.sh

# 5. Run launcher
python3 launcher.py
```

### After Git Pull
```bash
# 1. Pull updates
git pull

# 2. Fix any path issues
bash quick_fix.sh

# 3. Activate venv and run
source venv/bin/activate
python3 launcher.py
```

### Troubleshooting Workflow
```bash
# 1. Run diagnostic
python3 debug_icons.py

# 2. Run fix based on diagnosis
bash quick_fix.sh

# 3. Run diagnostic again to verify
python3 debug_icons.py

# 4. Try launcher
python3 launcher.py
```

---

## 📋 Script Locations

```
ARC/
├── quick_fix.sh           # Main fix script
├── fix_icons_pi.sh        # Raspberry Pi specific
├── debug_icons.py         # Diagnostic tool
├── launcher.py            # Main application entry
└── requirements.txt       # Python dependencies
```

---

## 🔧 Creating Your Own Scripts

You can add custom scripts to help with your workflow:

### Example: Auto-start script

```bash
#!/bin/bash
# auto_start.sh - Automatically start ARC

cd ~/ARC
source venv/bin/activate
python3 launcher.py
```

### Example: Update script

```bash
#!/bin/bash
# update.sh - Update and fix ARC

cd ~/ARC
git pull
bash quick_fix.sh
echo "Update complete! Run: python3 launcher.py"
```

### Example: Backup script

```bash
#!/bin/bash
# backup_config.sh - Backup configuration

cp config/arc.yaml config/arc.yaml.backup.$(date +%Y%m%d)
echo "Config backed up!"
```

---

## 📚 Related Documentation

- [SETUP.md](SETUP.md) - Installation guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [PI_ICON_FIX.md](PI_ICON_FIX.md) - Detailed icon fix guide
- [STRUCTURE.md](STRUCTURE.md) - Project structure

---

## 💡 Tips

1. **Always run scripts from ARC root directory**
   ```bash
   cd ~/ARC
   bash quick_fix.sh  # ✓ Correct
   ```

2. **Make scripts executable**
   ```bash
   chmod +x quick_fix.sh
   ./quick_fix.sh  # Now works
   ```

3. **Check output carefully**
   - ✓ = Success
   - ✗ = Error (needs attention)
   - ⚠ = Warning (might be OK)

4. **Save diagnostic output**
   ```bash
   python3 debug_icons.py > diagnostic.txt
   # Share this file when asking for help
   ```

---

## 🆘 Getting Help

If scripts don't fix your issue:

1. Run `python3 debug_icons.py > diagnostic.txt`
2. Run `python3 launcher.py > launcher.txt 2>&1`
3. Share these files in a GitHub issue

---

**Quick Reference:**
- Fix icons: `bash quick_fix.sh`
- Diagnose: `python3 debug_icons.py`
- Run ARC: `python3 launcher.py`



