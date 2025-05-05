# Configuration for UI elements

import os

# Screen settings
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 320
FPS = 60

# Tab settings
TAB_WIDTH = 100
TAB_HEIGHT = 40
TAB_MARGIN = 5

# Colors
COLORS = {
    'background':      (17, 17, 17),
    'tab_bg':          (50, 50, 50),
    'tab_active':      (100, 100, 100),
    'button':          (220, 220, 220),
    'button_hover':    (100, 160, 210),
    'text_light':      (5, 5, 5),
    'text':            (220, 220, 220),
    'warning_bg':      (200, 50, 50),
    'warning_text':    (255, 255, 255),
    'indicator':       (180, 180, 180),
    'indicator_active':(255, 255, 255),
    'input_bg':        (255, 255, 255),
    'input_border':    (100, 100, 100),
    'input_text':      (0, 0, 0),
    'input_placeholder': (150, 150, 150),
    'cell_bg':         (50, 50, 50),
    'cell_active':     (80, 80, 80),
    'accent':          ()
}

# Home Launcher
# Paths
BASE_DIR     = os.path.dirname(os.path.realpath(__file__))
BUILTIN_APPS = [
    { 'name':'Music',   'icon':os.path.join(BASE_DIR,'icons','music.png'),   'exec':'launch_music'   },
    { 'name':'Music',   'icon':os.path.join(BASE_DIR,'icons','music.png'),   'exec':'launch_music'   },
    { 'name':'Music',   'icon':os.path.join(BASE_DIR,'icons','music.png'),   'exec':'launch_music'   },
    { 'name':'Music',   'icon':os.path.join(BASE_DIR,'icons','music.png'),   'exec':'launch_music'   },
    { 'name':'Music',   'icon':os.path.join(BASE_DIR,'icons','music.png'),   'exec':'launch_music'   },
    { 'name':'Music',   'icon':os.path.join(BASE_DIR,'icons','music.png'),   'exec':'launch_music'   },
    { 'name':'Music',   'icon':os.path.join(BASE_DIR,'icons','music.png'),   'exec':'launch_music'   },
    { 'name':'Music',   'icon':os.path.join(BASE_DIR,'icons','music.png'),   'exec':'launch_music'   },
    { 'name':'Music',   'icon':os.path.join(BASE_DIR,'icons','music.png'),   'exec':'launch_music'   },
    { 'name':'Music',   'icon':os.path.join(BASE_DIR,'icons','music.png'),   'exec':'launch_music'   },
    { 'name':'Music',   'icon':os.path.join(BASE_DIR,'icons','music.png'),   'exec':'launch_music'   },
    { 'name':'Browser', 'icon':os.path.join(BASE_DIR,'icons','music.png'), 'exec':'launch_browser' }
]
APPS_DIR     = os.path.join(BASE_DIR, 'apps')       # each subfolder = one app, contains manifest.json + icon.png
PACKAGES_DIR = os.path.join(BASE_DIR, 'packages')   # optional installed packages

# Grid
GRID_COLS       = 4
GRID_ROWS       = 2
GRID_MARGIN     = 10
GRID_OUTER_MARGIN = 20
CELL_WIDTH      = (SCREEN_WIDTH - GRID_MARGIN*(GRID_COLS+1)) // GRID_COLS
CELL_HEIGHT     = (SCREEN_WIDTH - GRID_MARGIN*(GRID_COLS+1)) // GRID_COLS

# Top bar
TOPBAR_HEIGHT   = 30
TOPBAR_BG       = (20, 20, 20)
TOPBAR_FG       = (200, 200, 200)
TOPBAR_ICONS    = [
    # list of file paths or loaded surfaces for status icons
    'icons/topbar/apps.png',
    'icons/topbar/bluetooth.png',
    'icons/topbar/wifi.png'
]

# Radii for rounded corners
RADIUS = {
    'button': 8,
    'tab':    6,
    'warning':6,
    'modal':  6,
    'input':  6,
}

# Scroll indicator settings
INDICATOR_RADIUS = 4
INDICATOR_SPACING = 10

# Font settings
FONT_NAME = 'Arial'
FONT_SIZE = 20

# Warning message duration (milliseconds)
WARNING_DURATION = 2000