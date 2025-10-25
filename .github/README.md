# ARC - All-in-one Remote Console

> **Status:** ✅ Fully Reorganized & Cross-Platform Compatible

## Quick Start

```bash
# Clone the repository
git clone https://github.com/IstratieStefan/ARC.git
cd ARC

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the launcher
python launcher.py
```

## What's New? 🎉

The ARC codebase has been **completely reorganized** into a professional, maintainable structure:

### Before → After

```
❌ Old Structure                    ✅ New Structure
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
25+ root directories               Clean package structure
Scattered config files             arc/
Duplicate assets                    ├── core/      (config, UI)
Inconsistent naming                 ├── desktop/   (launcher, menus)
No package structure               ├── apps/      (17 apps)
                                    └── assets/    (icons, fonts)
```

### Key Improvements

✅ **Professional Structure** - Proper Python package  
✅ **Cross-Platform** - Works on macOS & Linux  
✅ **Centralized Assets** - All icons & fonts in one place  
✅ **Clean Imports** - `from arc.core import config`  
✅ **Well Documented** - Complete setup & structure docs  
✅ **100% Functional** - All features working  

## Platform Support

| Feature | macOS | Linux |
|---------|-------|-------|
| Display | Windowed (dev) | Fullscreen |
| Volume | osascript ✅ | amixer ✅ |
| WiFi | airport ✅ | nmcli ✅ |
| Bluetooth | system_profiler ✅ | bluetoothctl ✅ |

## Project Structure

```
ARC/
├── arc/                    # Main Python package
│   ├── core/              # Core utilities (config, UI elements)
│   ├── desktop/           # Desktop environment & launcher
│   ├── apps/              # All applications (17 apps)
│   └── assets/            # Icons, fonts, images
├── config/                # Configuration files
│   └── arc.yaml          # Main config (cross-platform paths)
├── docs/                  # Documentation
├── launcher.py            # Entry point
└── requirements.txt       # Dependencies
```

## Applications

17 built-in applications:
- 🔧 **Tools**: WiFi, Bluetooth, IR, NFC, RF, BadUSB
- 📱 **Apps**: Calendar, Notes, Music Player, Games
- 🔌 **Connect**: ARC Connect (web interface)
- ⚙️ **System**: Settings, Terminal, Files

## Documentation

- 📘 [SETUP.md](SETUP.md) - Installation & setup guide
- 📗 [STRUCTURE.md](STRUCTURE.md) - Architecture details
- 📙 [REORGANIZATION_SUMMARY.md](REORGANIZATION_SUMMARY.md) - What changed

## Configuration

Edit `config/arc.yaml` to customize:
- Colors & theme
- Screen size
- Built-in apps
- Icon paths
- Keyboard layout

## Development

### Adding a New App

```bash
# 1. Create app directory
mkdir -p arc/apps/myapp
touch arc/apps/myapp/__init__.py
touch arc/apps/myapp/main.py

# 2. Add icon
cp myicon.png arc/assets/icons/myapp.png

# 3. Register in config/arc.yaml
# builtin_apps:
#   - name: My App
#     icon: arc/assets/icons/myapp.png
#     exec: "python -m arc.apps.myapp.main"
```

### Clean Imports

```python
from arc.core import config, Button, AppIcon
from arc.desktop import TopBar, WifiMenu, show_loading_screen
from arc.apps.myapp import main
```

## Hardware

Designed for:
- Orange Pi Zero 2W
- Raspberry Pi 3/4
- Any Linux SBC with Python 3.7+

Supports:
- 3.5" SPI displays
- I²C keyboards
- WiFi/Bluetooth
- GPIO, UART, I²C, SPI modules

## Contributing

Contributions welcome! The new structure makes it easy to:
1. Find and fix bugs
2. Add new applications
3. Improve documentation
4. Add platform support

## License

See [LICENSE](LICENSE) file.

## Links

- 🌐 [Official Website](https://arc.istratiestefan.com)
- 📦 [Hardware Repo](https://github.com/IstratieStefan/ARC-Hardware)
- 📖 [Documentation](docs/)
- 🐛 [Report Issues](https://github.com/IstratieStefan/ARC/issues)

---

**Designed in California 🇺🇸 • Built in Romania 🇷🇴**

