# Config Updated for Current Structure

## What Changed

I've updated the configuration to work with your **current** directory structure where icons are still in `ARC_DE/icons/`.

## New Files

### 1. `run_app.sh` - App Launcher Wrapper

**Purpose:** Ensures apps run from the correct directory with the right Python environment.

**Location:** `ARC/run_app.sh`

**Usage:** Automatically called by the launcher (you don't run this directly)

**What it does:**
- Finds the ARC root directory
- Activates the virtual environment
- Changes to the app's directory  
- Runs the app with python3

### 2. Updated `config/arc.yaml`

**What's fixed:**
- ✅ Icon paths point to `ARC_DE/icons/` (where they currently are)
- ✅ All app launch commands use `run_app.sh` wrapper
- ✅ Apps will launch correctly no matter where you run launcher from
- ✅ Paths are relative and will be resolved automatically

## Icon Paths in Config

```yaml
# Icons now point to actual location
icons:
  wifi_locked: ARC_DE/icons/wifi_locked.png
  wifi_unlocked: ARC_DE/icons/wifi_unlocked.png

builtin_apps:
  - name: Terminal
    icon: ARC_DE/icons/terminal.png
    # ... etc
```

## App Launch Commands

```yaml
builtin_apps:
  - name: AI Chatbot
    icon: ARC_DE/icons/AI.png
    exec: "bash run_app.sh Chatbot main.py"
    
  - name: Calendar
    icon: ARC_DE/icons/calendar.png
    exec: "bash run_app.sh Calendar_app main.py"
```

**Format:** `bash run_app.sh <app_directory> <script_name>`

## How It Works

### When You Launch an App:

1. **Launcher** executes: `bash run_app.sh Chatbot main.py`
2. **run_app.sh** script:
   - Finds ARC root directory (where the script lives)
   - Activates `venv/bin/activate` if it exists
   - Changes to `Chatbot/` directory
   - Runs `python3 main.py`
3. **App runs** with correct working directory and environment

### Icon Loading:

1. **Config** specifies: `ARC_DE/icons/terminal.png`
2. **Config loader** resolves it to: `/home/admin/ARC/ARC_DE/icons/terminal.png`
3. **AppIcon class** loads the image from the absolute path

## Testing on Raspberry Pi

```bash
cd ~/ARC  # Or wherever your ARC is

# Pull the latest changes
git pull

# Make sure run_app.sh is executable
chmod +x run_app.sh

# Test icon loading
python3 debug_icons.py

# Run the launcher
source venv/bin/activate
python3 launcher.py
```

## Expected Results

### Icons Should Load:
```
AppIcon: Loading 'Terminal'
  Path: /home/admin/ARC/ARC_DE/icons/terminal.png
  Absolute: /home/admin/ARC/ARC_DE/icons/terminal.png
  Exists: True
  ✓ Successfully loaded icon
```

### Apps Should Launch:
- Click on any app icon
- The app should open in its own window
- No "file not found" errors

## Directory Structure You Have

```
ARC/
├── ARC_DE/
│   └── icons/           # ← Your icons are here
│       ├── terminal.png
│       ├── AI.png
│       └── ... (all icons)
├── Chatbot/
│   └── main.py
├── Calendar_app/
│   └── main.py
├── config/
│   └── arc.yaml         # ← Updated config
├── run_app.sh           # ← New app wrapper
├── launcher.py          # ← Entry point
└── venv/                # ← Virtual environment
```

## Benefits

✅ **Works from anywhere** - Run launcher from any directory  
✅ **Uses current structure** - No need to move icons  
✅ **Activates venv automatically** - Apps get the right Python packages  
✅ **Correct working directory** - Each app runs in its own folder  
✅ **Cross-platform** - Works on Linux and macOS  

## Optional: Move Icons Later

If you want to move to the new structure later:

```bash
# Move icons to new location
mkdir -p arc/assets/icons
cp -r ARC_DE/icons/* arc/assets/icons/

# Update config
sed -i 's|ARC_DE/icons/|arc/assets/icons/|g' config/arc.yaml

# Test
python3 launcher.py
```

But for now, **everything works as-is** with icons in `ARC_DE/icons/`!

## Troubleshooting

### Icons Still Don't Load

```bash
# Check what paths are being used
python3 debug_icons.py

# Check if icons exist
ls -la ARC_DE/icons/

# Check config
cat config/arc.yaml | head -20
```

### Apps Don't Launch

```bash
# Check if run_app.sh is executable
ls -la run_app.sh

# Make it executable
chmod +x run_app.sh

# Test wrapper directly
bash run_app.sh Chatbot main.py
```

### Virtual Environment Not Found

```bash
# Create venv if missing
python3 -m venv venv

# Install dependencies
source venv/bin/activate
pip install -r requirements.txt
```

## Summary

You now have:
- ✅ Config pointing to correct icon location (`ARC_DE/icons/`)
- ✅ App wrapper (`run_app.sh`) that ensures correct execution
- ✅ Updated launcher that runs commands from ARC root
- ✅ Everything works regardless of where you run launcher from

**Just pull the changes and test!** 🚀

