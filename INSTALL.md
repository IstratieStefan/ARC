# ARC Installation Guide

Complete installation instructions for different platforms.

---

## Quick Install

### macOS (Development)

```bash
# 1. Clone repository
git clone https://github.com/IstratieStefan/ARC.git
cd ARC

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run launcher
python3 launcher.py
```

### Linux / Raspberry Pi

```bash
# 1. Clone repository
git clone https://github.com/IstratieStefan/ARC.git
cd ARC

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-linux.txt  # Optional: for hardware features

# 4. Run launcher
python3 launcher.py
```

---

## Detailed Installation

### Step 1: System Prerequisites

#### macOS
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3
brew install python3

# Install Git
brew install git
```

#### Linux (Debian/Ubuntu)
```bash
# Update package list
sudo apt update

# Install Python and development tools
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install Git
sudo apt install -y git

# Install SDL2 libraries (required for pygame)
sudo apt install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

# Install audio libraries (required for pyaudio)
sudo apt install -y portaudio19-dev

# Optional: Network tools (for WiFi/Bluetooth features)
sudo apt install -y wireless-tools aircrack-ng bluez
```

#### Raspberry Pi OS
```bash
# Same as Linux, plus:
sudo apt install -y python3-rpi.gpio  # For GPIO access
```

---

### Step 2: Clone Repository

```bash
# Clone from GitHub
git clone https://github.com/IstratieStefan/ARC.git

# Navigate to directory
cd ARC

# Verify files
ls -la
```

---

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Verify activation (prompt should show (venv))
which python3
# Should output: /path/to/ARC/venv/bin/python3
```

---

### Step 4: Install Dependencies

#### Core Dependencies (All Platforms)

```bash
# Ensure venv is activated
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install core dependencies
pip install -r requirements.txt
```

**What gets installed:**
- `numpy` - Numerical computing
- `pygame` - Graphics and UI framework
- `mutagen` - Audio metadata reading
- `requests` - HTTP library
- `pillow` - Image processing
- `pyyaml` - Configuration file parser
- `pyaudio` - Audio I/O
- `qrcode` - QR code generation
- `flask` & `flask-cors` - Web server for ARC Connect
- `websockets` - WebSocket support
- `paramiko` - SSH functionality
- `qtpy` - Qt compatibility layer
- `smbus2` - I2C communication (hardware)

#### Linux-Specific (Optional)

```bash
# Only on Linux/Raspberry Pi
pip install -r requirements-linux.txt
```

**What gets installed:**
- `python-uinput` - Keyboard emulation for hardware

**Note:** This will fail on macOS - that's expected and OK!

#### Development Tools (Optional)

```bash
# For development only
pip install -r requirements-dev.txt
```

**What gets installed:**
- `black` - Code formatter
- `flake8` - Code linter
- `mypy` - Type checker
- `pytest` - Testing framework
- `ipython` - Better REPL

---

### Step 5: Verify Installation

```bash
# Test imports
python3 -c "import pygame; import numpy; import yaml; print('✓ All imports successful')"

# Check pygame version
python3 -c "import pygame; print(f'Pygame {pygame.version.ver}')"

# List installed packages
pip list
```

---

### Step 6: Run Test Scripts

```bash
# Test icon loading
python3 debug_icons.py

# Test app launcher
bash test_run_app.sh

# Make sure scripts are executable
chmod +x run_app.sh test_run_app.sh
```

---

### Step 7: Run ARC

```bash
# Activate venv (if not already active)
source venv/bin/activate

# Run launcher
python3 launcher.py
```

**Expected:** 
- Window opens (480x320 on macOS, fullscreen on Linux)
- Icons display correctly
- Top bar shows WiFi/Bluetooth status
- Clicking icons launches apps

---

## Platform-Specific Notes

### macOS

**Display:**
- Runs in windowed mode (480x320)
- Good for development and testing

**Features:**
- Volume control via AppleScript
- WiFi status via airport utility
- Bluetooth via system_profiler

**Limitations:**
- Some network tools (aircrack-ng) not available
- Hardware-specific features won't work

### Linux Desktop

**Display:**
- Runs in fullscreen mode
- Use Ctrl+Q to quit

**Features:**
- Full network tool support
- Volume control via ALSA
- WiFi via nmcli
- Bluetooth via bluetoothctl

**Permissions:**
```bash
# For network features (WiFi scanning, etc.)
sudo usermod -aG netdev $USER

# For Bluetooth
sudo usermod -aG bluetooth $USER

# Log out and back in for changes to take effect
```

### Raspberry Pi

**Display:**
- Fullscreen on connected display
- Can use framebuffer

**Hardware Support:**
- GPIO access (with python-uinput)
- I2C devices (with smbus2)
- SPI displays
- Hardware keyboard

**Auto-start on Boot:**
```bash
# Create autostart directory
mkdir -p ~/.config/autostart

# Create desktop entry
cat > ~/.config/autostart/arc.desktop << EOF
[Desktop Entry]
Type=Application
Name=ARC Launcher
Exec=/home/pi/ARC/venv/bin/python /home/pi/ARC/launcher.py
Terminal=false
EOF
```

---

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'pygame'`

**Solution:**
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### pygame Installation Fails

**Problem:** pygame won't install on Linux

**Solution:**
```bash
# Install SDL2 development libraries
sudo apt install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

# Try again
pip install pygame
```

### pyaudio Installation Fails

**Problem:** pyaudio won't compile

**Solution (Linux):**
```bash
# Install PortAudio development files
sudo apt install portaudio19-dev

# Try again
pip install pyaudio
```

**Solution (macOS):**
```bash
# Install PortAudio via Homebrew
brew install portaudio

# Try again
pip install pyaudio
```

### python-uinput Fails on macOS

**Problem:** `python-uinput` fails to install

**Solution:** This is expected! Skip it on macOS:
```bash
# Only install base requirements on macOS
pip install -r requirements.txt
# Don't install requirements-linux.txt on macOS
```

---

## Updating

```bash
cd ~/ARC

# Pull latest changes
git pull

# Activate venv
source venv/bin/activate

# Update dependencies
pip install --upgrade -r requirements.txt

# Run quick fix (if needed)
bash quick_fix.sh

# Test
python3 launcher.py
```

---

## Uninstalling

```bash
# Remove virtual environment
rm -rf ~/ARC/venv

# Remove entire project (careful!)
rm -rf ~/ARC
```

---

## Requirements Files Summary

| File | Purpose | Platform |
|------|---------|----------|
| `requirements.txt` | Core dependencies | All platforms |
| `requirements-linux.txt` | Linux-specific packages | Linux/Pi only |
| `requirements-dev.txt` | Development tools | Optional |

---

## Next Steps

After installation:
1. Read [SETUP.md](SETUP.md) for usage instructions
2. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if issues arise
3. See [STRUCTURE.md](STRUCTURE.md) to understand the codebase
4. Visit [arc.istratiestefan.com](https://arc.istratiestefan.com) for more info

---

**Installation complete! Run `python3 launcher.py` to start ARC.** 🚀

