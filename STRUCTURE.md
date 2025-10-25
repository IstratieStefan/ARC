# ARC Project Structure

This document describes the reorganized structure of the ARC project.

## Directory Layout

```
ARC/
├── arc/                        # Main Python package
│   ├── __init__.py            # Package initialization
│   ├── core/                  # Core utilities and components
│   │   ├── __init__.py        # Exports: config, UI elements
│   │   ├── config.py          # Configuration management (YAML)
│   │   ├── ui_elements.py     # Reusable UI components
│   │   └── keyboard.py        # Keyboard input handling
│   ├── desktop/               # Desktop environment (formerly ARC_DE)
│   │   ├── __init__.py        # Desktop module exports
│   │   ├── launcher.py        # Main desktop launcher
│   │   ├── arc_status.py      # System status (WiFi, BT)
│   │   ├── bluetooth_menu.py  # Bluetooth interface
│   │   ├── call_menu.py       # Call interface
│   │   ├── loading_screen.py  # Loading screen utility
│   │   ├── status_poller.py   # Background status polling
│   │   ├── topbar.py          # Top bar UI
│   │   ├── volume_widget.py   # Volume control widget
│   │   ├── wifi_menu.py       # WiFi interface
│   │   └── contacts.json      # Contact data
│   ├── apps/                  # All applications
│   │   ├── __init__.py
│   │   ├── badusb/            # Bad USB tools
│   │   ├── bluetooth_tools/   # Bluetooth utilities
│   │   ├── calculator/        # Calculator app
│   │   ├── calendar/          # Calendar app
│   │   ├── chatbot/           # AI chatbot
│   │   ├── connect/           # ARC Connect (web interface)
│   │   ├── games/             # Game launcher
│   │   ├── ir_tools/          # Infrared tools
│   │   ├── mail/              # Email client
│   │   ├── maps/              # Maps application
│   │   ├── music_player/      # Music player
│   │   ├── nfc_tools/         # NFC tools
│   │   ├── notes/             # Text editor/notes
│   │   ├── rf_tools/          # RF tools
│   │   ├── settings/          # Settings app
│   │   ├── time/              # Time/clock app
│   │   └── wifi_tools/        # WiFi analysis tools
│   └── assets/                # All static assets
│       ├── icons/             # All icons
│       │   ├── topbar/        # Top bar icons
│       │   ├── AI.png
│       │   ├── terminal.png
│       │   └── ... (all app icons)
│       └── fonts/             # All fonts
│           └── Inter/         # Inter font family
├── config/                    # Configuration files
│   └── arc.yaml              # Main configuration
├── docs/                      # Documentation
│   ├── ARC Documentation.pdf
│   └── ARC Documentation English.pdf
├── firmware/                  # Hardware firmware
│   └── keyboard/             # Keyboard firmware
├── gallery/                   # Screenshots and demo images
├── website/                   # ARC website (Astro project)
├── venv/                      # Python virtual environment
├── launcher.py                # Main entry point
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Python project configuration
├── README.md                  # Project documentation
├── LICENSE                    # License file
└── STRUCTURE.md              # This file

```

## Key Improvements

### 1. **Modular Package Structure**
   - All code organized under the `arc/` package
   - Clear separation between core, desktop, and apps
   - Proper `__init__.py` files for clean imports

### 2. **Centralized Assets**
   - All icons consolidated in `arc/assets/icons/`
   - All fonts in `arc/assets/fonts/`
   - No more scattered asset duplicates

### 3. **Consistent Naming**
   - Apps use lowercase with underscores (e.g., `bluetooth_tools`, `music_player`)
   - Clear, descriptive directory names
   - Follows Python naming conventions

### 4. **Clean Imports**
   - Import from package: `from arc.core import config`
   - Import desktop components: `from arc.desktop import TopBar`
   - Import apps: `from arc.apps.games import main`

### 5. **Configuration Management**
   - Config file moved to `config/arc.yaml`
   - All paths updated to new structure
   - Supports both system config (`~/.config/arc.yaml`) and local config

## How to Use

### Running the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run the launcher
python launcher.py
```

### Importing Modules

```python
# Import core components
from arc.core import config, Button, AppIcon

# Import desktop components
from arc.desktop import TopBar, WifiMenu

# Import an app
from arc.apps.music_player import main
```

### Adding a New App

1. Create a directory in `arc/apps/your_app/`
2. Add `__init__.py` and `main.py`
3. Add an icon to `arc/assets/icons/your_app.png`
4. Update `config/arc.yaml` to include your app in `builtin_apps`

### Customization

Edit `config/arc.yaml` to:
- Change UI colors and styling
- Modify app grid layout
- Add/remove builtin apps
- Configure icon paths
- Adjust system behavior

## Platform Support

The codebase now includes platform-aware code:
- **macOS**: Volume control via `osascript`, windowed mode for development
- **Linux**: Volume control via `amixer`, fullscreen mode, system integration

## Migration Notes

If you're migrating from the old structure:
1. Old `ARC_DE/` → Now `arc/desktop/`
2. Old `BT_tools/` → Now `arc/apps/bluetooth_tools/`
3. Old `config.py` → Now `arc/core/config.py`
4. Old `ui_elements.py` → Now `arc/core/ui_elements.py`
5. All icon paths updated in `config/arc.yaml`

## Development

### Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Testing

Run the launcher in development mode (windowed) on macOS, or fullscreen on Linux.

## Architecture

- **arc/core/**: Shared utilities, configuration, UI components
- **arc/desktop/**: Desktop environment, launcher, system UI
- **arc/apps/**: Individual applications (modular)
- **arc/assets/**: Static resources (icons, fonts)
- **config/**: Configuration files (YAML)

This structure makes the codebase:
- ✅ More maintainable
- ✅ Easier to navigate
- ✅ Better organized
- ✅ Following Python best practices
- ✅ Ready for packaging and distribution

