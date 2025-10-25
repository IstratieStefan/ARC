# Using run_app.sh on Raspberry Pi

## Step-by-Step Instructions

### 1. Get the Latest Files

```bash
cd ~/ARC  # or wherever your ARC is
git pull
```

### 2. Make Scripts Executable

```bash
chmod +x run_app.sh
chmod +x test_run_app.sh
```

### 3. Run the Test Script

```bash
bash test_run_app.sh
```

**Expected output:**
```
==========================================
Testing run_app.sh
==========================================

ARC root: /home/admin/ARC

Test 1: Check if run_app.sh exists
  ✓ run_app.sh found

Test 2: Check if executable
  ✓ run_app.sh is executable

Test 3: Available app directories
  ✓ Chatbot (has main.py)
  ✓ Calendar_app (has main.py)
  ✓ BT_tools (has main.py)
  ✓ WIFI_tools (has main.py)
  ... etc
```

### 4. Test Manually

Test launching an app directly:

```bash
bash run_app.sh Chatbot main.py
```

You should see:
```
[run_app] ARC root: /home/admin/ARC
[run_app] Looking for: /home/admin/ARC/Chatbot/main.py
[run_app] Activating virtual environment...
[run_app] Changing to: /home/admin/ARC/Chatbot
[run_app] Running: python3 main.py
```

Then the Chatbot app should start.

### 5. Run the Launcher

```bash
source venv/bin/activate
python3 launcher.py
```

Now click on any app icon - it should launch correctly!

---

## How It Works

### When You Click an App Icon:

1. **Launcher** runs: `bash run_app.sh Chatbot main.py`
2. **run_app.sh**:
   - Finds ARC root directory
   - Looks for `/home/admin/ARC/Chatbot/main.py`
   - Activates virtual environment
   - Changes to Chatbot directory
   - Runs `python3 main.py`
3. **Chatbot** starts running

### Debug Output

The improved script shows what it's doing:
```
[run_app] ARC root: /home/admin/ARC
[run_app] Looking for: /home/admin/ARC/Chatbot/main.py
[run_app] Activating virtual environment...
[run_app] Changing to: /home/admin/ARC/Chatbot
[run_app] Running: python3 main.py
```

This helps you see if:
- ✓ It finds the ARC root
- ✓ It finds the app file
- ✓ It activates venv
- ✓ It runs the app

---

## Troubleshooting

### "Error: Chatbot/main.py not found"

**Cause:** App directory doesn't exist or is named differently.

**Solution:**
```bash
# Check what apps you have
ls -d */main.py

# If named differently, update config/arc.yaml
nano config/arc.yaml
```

### "Warning: No virtual environment found"

**Cause:** Virtual environment not created.

**Solution:**
```bash
cd ~/ARC
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### "Permission denied" when running script

**Cause:** Script not executable.

**Solution:**
```bash
chmod +x run_app.sh
```

### App starts but can't import modules

**Cause:** Module not installed in venv.

**Solution:**
```bash
source venv/bin/activate
pip install <missing_module>
```

---

## Testing Individual Apps

To test each app works:

```bash
# Test Chatbot
bash run_app.sh Chatbot main.py

# Test Calendar
bash run_app.sh Calendar_app main.py

# Test Bluetooth tools
bash run_app.sh BT_tools main.py

# Test WiFi tools  
bash run_app.sh WIFI_tools main.py

# Test Music player
bash run_app.sh music_player main.py

# Test Games
bash run_app.sh Games main.py

# Test NFC tools
bash run_app.sh NFC_tools main.py

# Test IR tools
bash run_app.sh IR_tools main.py

# Test RF tools
bash run_app.sh RF_tools main.py

# Test Notes
bash run_app.sh Notes_app main.py

# Test ARC Connect
bash run_app.sh ARC_connect ip.py
```

---

## What's Different?

### Before (Old Way):
```bash
# Had to be in the app directory
cd ~/ARC/Chatbot
python3 main.py
```

Problems:
- ✗ Wrong working directory if launched from elsewhere
- ✗ No venv activation
- ✗ Couldn't find imports

### Now (New Way):
```bash
# Run from anywhere
bash run_app.sh Chatbot main.py
```

Benefits:
- ✓ Always finds ARC root
- ✓ Auto-activates venv
- ✓ Sets correct working directory
- ✓ Adds ARC to Python path
- ✓ Shows debug output

---

## Quick Command Reference

```bash
# Navigate to ARC
cd ~/ARC

# Pull latest changes
git pull

# Make executable
chmod +x run_app.sh test_run_app.sh

# Test the setup
bash test_run_app.sh

# Test an app manually
bash run_app.sh Chatbot main.py

# Run the launcher
source venv/bin/activate
python3 launcher.py
```

---

## Success Indicators

✅ **Icons load** - You see app icons, not gray boxes  
✅ **Apps launch** - Clicking icons opens apps  
✅ **No errors** - No "file not found" messages  
✅ **Debug output** - You see `[run_app]` messages showing progress  

---

## Need Help?

If something doesn't work:

1. Run the test script and share output:
   ```bash
   bash test_run_app.sh > test_output.txt 2>&1
   ```

2. Try launching manually and share output:
   ```bash
   bash run_app.sh Chatbot main.py > chatbot_test.txt 2>&1
   ```

3. Share these files so I can help debug!

---

**The script is ready - just pull it, test it, and enjoy! 🚀**

