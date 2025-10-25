# ARC Setup Guide

Quick setup guide for getting ARC running on macOS and Linux.

## Prerequisites

### macOS
- Python 3.7+ (install via Homebrew: `brew install python3`)
- Git
- Optional: Terminal emulator (iTerm2, kitty)

### Linux (Debian/Ubuntu-based)
- Python 3.7+: `sudo apt install python3 python3-pip python3-venv`
- Git: `sudo apt install git`
- System libraries for pygame: `sudo apt install python3-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev`
- Optional: Network tools for WiFi/BT features: `sudo apt install wireless-tools aircrack-ng bluez`

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/IstratieStefan/ARC.git
cd ARC
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/macOS
```

### 3. Install Dependencies

**macOS (Development):**
```bash
pip install -r requirements.txt
# All dependencies will install successfully
```

**Linux / Raspberry Pi:**
```bash
# Install base dependencies
pip install -r requirements.txt

# Install Linux-specific packages (optional, for hardware features)
pip install -r requirements-linux.txt
```

**Development Tools (Optional):**
```bash
pip install -r requirements-dev.txt
# Includes code formatters, linters, testing tools
```

> **Note:** The `requirements-linux.txt` file contains `python-uinput` which only works on Linux. It's used for hardware keyboard integration on Raspberry Pi. Skip it on macOS.

## Running ARC

### Basic Launch

```bash
source venv/bin/activate
python launcher.py
```

### Platform-Specific Behavior

**macOS:**
- Runs in windowed mode (480x320) for easier development
- Volume control via macOS `osascript`
- WiFi/Bluetooth status uses macOS system commands
- Press Ctrl+Q to quit

**Linux:**
- Runs in fullscreen mode (ideal for embedded devices)
- Volume control via ALSA `amixer`
- WiFi/Bluetooth uses `nmcli` and `bluetoothctl`
- Press Ctrl+Q or ESC to quit

## Configuration

### Global Configuration
Edit `config/arc.yaml` to customize:
- Screen size and FPS
- Colors and theme
- Built-in apps
- Icon paths
- Grid layout
- Font settings

### User-Specific Configuration
Create `~/.config/arc.yaml` to override settings without modifying the repo.

### Example Customization

```yaml
# ~/.config/arc.yaml
screen:
  width: 800
  height: 600

colors:
  accent: [100, 200, 50]  # Custom accent color

builtin_apps:
  - name: My Custom App
    icon: /path/to/icon.png
    exec: "python /path/to/app.py"
```

## Project Structure

```
ARC/
├── arc/                    # Main package
│   ├── core/              # Config, UI elements
│   ├── desktop/           # Desktop environment
│   ├── apps/              # All applications
│   └── assets/            # Icons, fonts
├── config/                # Configuration files
├── launcher.py            # Entry point
└── requirements.txt       # Dependencies
```

See [STRUCTURE.md](STRUCTURE.md) for detailed documentation.

## Development

### Adding a New App

1. Create app directory:
```bash
mkdir -p arc/apps/my_app
touch arc/apps/my_app/__init__.py
touch arc/apps/my_app/main.py
```

2. Add app code to `main.py`:
```python
import pygame
from arc.core import config

def main():
    screen = pygame.display.set_mode((config.screen.width, config.screen.height))
    # Your app code here
    pygame.quit()

if __name__ == "__main__":
    main()
```

3. Add icon to `arc/assets/icons/my_app.png`

4. Register in `config/arc.yaml`:
```yaml
builtin_apps:
  - name: My App
    icon: arc/assets/icons/my_app.png
    exec: "python -m arc.apps.my_app.main"
```

### Keyboard Controls

- **Arrow Keys**: Navigate between apps
- **Enter**: Launch selected app
- **Ctrl+Q**: Quit ARC
- **Alt+Up/Down**: Volume control (when implemented)
- **ESC**: Close menus

### Testing on Both Platforms

The codebase automatically detects the platform and adjusts:
- Paths use `os.path.join()` for cross-platform compatibility
- Platform-specific commands are handled in code
- Config uses forward slashes (converted automatically)

## Troubleshooting

### Issue: Module not found errors
**Solution:** Make sure you're running from the project root and the virtual environment is activated:
```bash
cd /path/to/ARC
source venv/bin/activate
python launcher.py
```

### Issue: Icon not found warnings
**Solution:** Check that icon paths in `config/arc.yaml` are relative to the project root and use forward slashes:
```yaml
icon: arc/assets/icons/myicon.png  # ✓ Correct
icon: ./ARC_DE/icons/myicon.png    # ✗ Old path
```

### Issue: pygame fails to initialize (Linux)
**Solution:** Install SDL2 development libraries:
```bash
sudo apt install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
```

### Issue: Permission denied for network tools (Linux)
**Solution:** Some features require sudo privileges:
```bash
sudo python launcher.py  # For WiFi scanning, packet injection, etc.
```
Or add your user to necessary groups:
```bash
sudo usermod -aG netdev,bluetooth $USER
```

## Hardware Deployment (Raspberry Pi / Orange Pi)

For deploying to actual ARC hardware:

1. Flash Armbian or Raspberry Pi OS
2. Install dependencies
3. Clone repository
4. Run launcher on boot:
```bash
# Add to ~/.config/autostart/arc.desktop
[Desktop Entry]
Type=Application
Name=ARC Launcher
Exec=/home/pi/ARC/venv/bin/python /home/pi/ARC/launcher.py
```

## Platform Differences

| Feature | macOS | Linux |
|---------|-------|-------|
| Window Mode | Windowed | Fullscreen |
| Volume Control | osascript | amixer |
| WiFi Status | airport | nmcli |
| Bluetooth | system_profiler | bluetoothctl |
| File Manager | open | pcmanfm |
| Terminal | Terminal.app | kitty/xterm |

## Next Steps

- See [STRUCTURE.md](STRUCTURE.md) for architecture details
- Read the docs in `docs/` for hardware specifications
- Check out `arc/apps/` for example applications
- Join the community at [https://arc.istratiestefan.com](https://arc.istratiestefan.com)

## Support

- **Issues**: [GitHub Issues](https://github.com/IstratieStefan/ARC/issues)
- **Documentation**: See `docs/` folder
- **Website**: [arc.istratiestefan.com](https://arc.istratiestefan.com)

---

**Happy Hacking! 🚀**

