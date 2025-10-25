# Icons Folder Setup

The config now reads icons from `ARC/Icons/` folder.

## Directory Structure

```
ARC/
├── Icons/                    # Main icon folder
│   ├── terminal.png         # Terminal app
│   ├── AI.png               # AI Chatbot
│   ├── calendar.png         # Calendar
│   ├── rf.png               # RF tools
│   ├── ir.png               # IR tools
│   ├── nfc.png              # NFC tools
│   ├── wifi_tools.png       # WiFi tools
│   ├── bluetooth_tools.png  # Bluetooth tools
│   ├── files.png            # File manager
│   ├── editor.png           # Text editor
│   ├── music.png            # Music player
│   ├── games.png            # Games
│   ├── arc_connect.png      # ARC Connect
│   ├── wifi_locked.png      # WiFi locked icon
│   ├── wifi_unlocked.png    # WiFi unlocked icon
│   └── topbar/              # Topbar icons subfolder
│       ├── battery.png
│       ├── cellular.png
│       ├── wifi_0.png
│       ├── wifi_1.png
│       ├── wifi_2.png
│       ├── wifi_3.png
│       ├── wifi_4.png
│       ├── bluetooth_on.png
│       ├── bluetooth_off.png
│       └── bluetooth_connected.png
├── config/
│   └── arc.yaml            # Config points to Icons/
└── launcher.py
```

## Setup on Raspberry Pi

### Option 1: Automatic Setup (Recommended)

```bash
cd ~/ARC
git pull
bash setup_icons.sh
```

This script will:
- Create `Icons/` and `Icons/topbar/` directories
- Copy icons from old locations if they exist
- Verify all required icons are present
- Set correct permissions

### Option 2: Manual Setup

```bash
cd ~/ARC

# Create directories
mkdir -p Icons/topbar

# Copy from old location (if you had them there)
cp ARC_DE/icons/*.png Icons/
cp ARC_DE/icons/topbar/*.png Icons/topbar/

# Or copy from wherever you have them
# cp /path/to/your/icons/*.png Icons/
```

## Required Icons

### App Icons (13 files in `Icons/`):
1. `terminal.png` - Terminal emulator
2. `AI.png` - AI Chatbot
3. `calendar.png` - Calendar app
4. `rf.png` - RF tools
5. `ir.png` - IR tools
6. `nfc.png` - NFC tools
7. `wifi_tools.png` - WiFi tools
8. `bluetooth_tools.png` - Bluetooth tools
9. `files.png` - File manager
10. `editor.png` - Text editor
11. `music.png` - Music player
12. `games.png` - Game launcher
13. `arc_connect.png` - ARC Connect

### WiFi Menu Icons (2 files in `Icons/`):
- `wifi_locked.png` - Locked WiFi network
- `wifi_unlocked.png` - Open WiFi network

### Topbar Icons (10 files in `Icons/topbar/`):
1. `battery.png` - Battery indicator
2. `cellular.png` - Cellular signal
3. `wifi_0.png` - WiFi no signal
4. `wifi_1.png` - WiFi weak signal
5. `wifi_2.png` - WiFi medium signal
6. `wifi_3.png` - WiFi good signal
7. `wifi_4.png` - WiFi excellent signal
8. `bluetooth_on.png` - Bluetooth on
9. `bluetooth_off.png` - Bluetooth off
10. `bluetooth_connected.png` - Bluetooth connected

**Total: 25 icon files**

## Verify Setup

After setting up, verify everything is in place:

```bash
# Check app icons
ls -la Icons/*.png

# Check topbar icons
ls -la Icons/topbar/*.png

# Count total icons
find Icons -name "*.png" | wc -l
# Should show: 25
```

## Test Icons Load

```bash
cd ~/ARC

# Run diagnostic
python3 debug_icons.py

# All should show "Exists: True"
```

## Run Launcher

```bash
python3 launcher.py
```

You should now see your PNG icons instead of gray boxes with letters!

## Troubleshooting

### Icons still show as gray boxes with letters

**Cause:** Icon files don't exist in `Icons/` folder

**Solution:**
```bash
# Check what you have
ls -la Icons/

# If empty, copy from old location
bash setup_icons.sh

# Or manually:
cp ARC_DE/icons/*.png Icons/
cp ARC_DE/icons/topbar/*.png Icons/topbar/
```

### "File is not a Windows BMP file" error

**Cause:** Files in `Icons/` aren't actually PNG files

**Solution:**
```bash
# Check file types
file Icons/*.png

# Should all say "PNG image data"
# If not, get proper PNG files
```

### Some icons load, others don't

**Cause:** Missing some icon files

**Solution:**
```bash
# Run setup script to see which are missing
bash setup_icons.sh

# It will list:
# ✓ terminal.png
# ✗ calendar.png (missing)
# etc.
```

## Icon Specifications

For best results, icons should be:
- **Format:** PNG with transparency
- **Size:** 64x64 to 128x128 pixels recommended
- **File size:** < 100KB per icon
- **Color depth:** 32-bit RGBA

## Quick Commands

```bash
# Setup Icons folder
bash setup_icons.sh

# Verify icons
ls Icons/*.png | wc -l  # Should show 15
ls Icons/topbar/*.png | wc -l  # Should show 10

# Test loading
python3 debug_icons.py

# Run launcher
python3 launcher.py
```

## Summary

✅ **Config updated** - Points to `Icons/` folder  
✅ **Setup script** - `bash setup_icons.sh`  
✅ **25 icons needed** - 15 app + 2 wifi + 10 topbar  
✅ **Automatic verification** - Script checks everything  

**Run `bash setup_icons.sh` and your icons will work!** 🎯

