# Configuration for UI elements

import os

# Screen settings
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 320
FPS = 30

# Tab settings
TAB_WIDTH = 100
TAB_HEIGHT = 40
TAB_MARGIN = 5

ACCENT_COLOR = (204, 99, 36)

# Colors
COLORS = {
    'background':      (20, 20, 20),
    'background_light':(250, 250, 250),
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
    'cell_bg':         (220, 220, 220),
    'cell_active':     (240, 240, 240),
    'accent':          ACCENT_COLOR,
    'slider_bg':       ( 50,  50,  50),
    'slider_fill':     ( 50, 200,  50),
    'slider_knob':     (200, 200, 200),
    'slider_active_knob': (255, 255, 255),
}

ICONS = {
    'wifi_locked':"./ARC_DE/icons/wifi_locked.png",
    'wifi_unlocked':"./ARC_DE/icons/wifi_unlocked.png",
}
# Home Launcher
# Paths
BASE_DIR     = os.path.dirname(os.path.realpath(__file__))
BUILTIN_APPS = [
    { 'name':'Terminal',   'icon':os.path.join(BASE_DIR,'ARC_DE','icons','terminal.png'),   'exec':'lxterminal &'   },
    { 'name':'Web browser', 'icon':os.path.join(BASE_DIR,'ARC_DE','icons','browser.png'),   'exec':'python3 ./web_apps/browser.py'   },
    { 'name':'Phone',   'icon':os.path.join(BASE_DIR,'ARC_DE','icons','phone.png'),   'exec':'python3 coming_soon.coming_soon'   },
    { 'name':'Contacts',   'icon':os.path.join(BASE_DIR,'ARC_DE','icons','contacts.png'),   'exec':'python3 coming_soon.coming_soon'   },
    { 'name':'Mail',   'icon':os.path.join(BASE_DIR,'ARC_DE','icons','mail.png'),   'exec':'python3 coming_soon.coming_soon'   },
    { 'name':'Whatsapp',   'icon':os.path.join(BASE_DIR,'ARC_DE','icons','sms.png'),   'exec':'python3 ./web_apps/whatsapp.py'   },
    { 'name':'Calendar',   'icon':os.path.join(BASE_DIR,'ARC_DE','icons','calendar.png'),   'exec':'python3 -m calendar_app.main'   },
    { 'name':'RF tools',   'icon':os.path.join(BASE_DIR,'ARC_DE','icons','rf.png'),   'exec':'python3 -m RF_tools.main'   },
    { 'name':'IR tools',   'icon':os.path.join(BASE_DIR,'ARC_DE','icons','ir.png'),   'exec':'python3 -m IR_tools.main'   },
    { 'name':'NFC tools',   'icon':os.path.join(BASE_DIR,'ARC_DE','icons','nfc.png'),   'exec':'python3 -m NFC_tools.main'   },
    { 'name':'WiFi tools',   'icon':os.path.join(BASE_DIR,'ARC_DE','icons','wifi_tools.png'),   'exec':'python3 -m WIFI_tools.main'   },
    { 'name':'Files',   'icon':os.path.join(BASE_DIR,'ARC_DE','icons','files.png'),   'exec':'pcmanfm'   },
    { 'name':'Text editor',   'icon':os.path.join(BASE_DIR,'ARC_DE','icons','editor.png'),   'exec':'vim -r'   },
    { 'name':'Music',   'icon':os.path.join(BASE_DIR,'ARC_DE','icons','music.png'),   'exec':'python3 -m music_player.main'   },
    { 'name':'Games',   'icon':os.path.join(BASE_DIR,'ARC_DE','icons','games.png'),   'exec':'python3 .Games.main'   },
    { 'name':'Settings', 'icon':os.path.join(BASE_DIR,'ARC_DE','icons','settings.png'), 'exec':'python .Settings.main' },
    { 'name':'ARC connect', 'icon':os.path.join(BASE_DIR,'ARC_DE','icons','arc_connect.png'), 'exec':'python3 -m ARC_connect.ip' }
]
APPS_DIR     = os.path.join(BASE_DIR, 'apps')       # each subfolder = one app, contains manifest.json + icon.png
PACKAGES_DIR = os.path.join(BASE_DIR, 'packages')   # optional installed packages

# Grid
GRID_COLS       = 4
GRID_ROWS       = 2
GRID_MARGIN     = 10
GRID_PADDING    = 20
CELL_WIDTH      = (SCREEN_WIDTH - 2 * GRID_PADDING - GRID_MARGIN*(GRID_COLS+1)) // GRID_COLS
CELL_HEIGHT     = (SCREEN_WIDTH - 2 * GRID_PADDING - GRID_MARGIN*(GRID_COLS+1)) // GRID_COLS

# Top bar
TOPBAR_HEIGHT        = 30
TOPBAR_BG            = (20, 20, 20)
TOPBAR_FG            = (200, 200, 200)
NOTIFICATION_DOT     = (245, 88, 88)

# left-side static icons
TOPBAR_ICONS         = [
    # …add/remove as desired
]

# indicator icon paths (must exist)
TOPBAR_ICON_BATTERY  = os.path.join(BASE_DIR, 'ARC_DE', 'icons', 'topbar', 'battery.png')
TOPBAR_ICON_MOBILE   = os.path.join(BASE_DIR, 'ARC_DE', 'icons', 'topbar', 'cellular.png')

TOPBAR_WIFI_ICONS = [
    os.path.join(BASE_DIR, 'ARC_DE', 'icons', 'topbar', 'wifi_0.png'),
    os.path.join(BASE_DIR, 'ARC_DE', 'icons', 'topbar', 'wifi_1.png'),
    os.path.join(BASE_DIR, 'ARC_DE', 'icons', 'topbar', 'wifi_2.png'),
    os.path.join(BASE_DIR, 'ARC_DE', 'icons', 'topbar', 'wifi_3.png'),
    os.path.join(BASE_DIR, 'ARC_DE', 'icons', 'topbar', 'wifi_4.png'),
]

TOPBAR_ICON_BT_ON = os.path.join(BASE_DIR, 'ARC_DE', 'icons', 'topbar', 'bluetooth_on.png')
TOPBAR_ICON_BT_OFF = os.path.join(BASE_DIR, 'ARC_DE', 'icons', 'topbar', 'bluetooth_off.png')
TOPBAR_ICON_BT_CONNECTED = os.path.join(BASE_DIR, 'ARC_DE', 'icons', 'topbar', 'bluetooth_connected.png')

# which elements to show
TOPBAR_SHOW_CLOCK       = True
TOPBAR_CLOCK_FORMAT     = "%H:%M" # HH:MM only
TOPBAR_SHOW_NOTIFICATIONS = True

TOPBAR_SHOW_BATTERY     = True
TOPBAR_SHOW_WIFI        = True
TOPBAR_SHOW_BT          = True
TOPBAR_SHOW_MOBILE      = True

# spacing (pixels)
TOPBAR_PADDING_LEFT     = 5
TOPBAR_PADDING_RIGHT    = 5
TOPBAR_ICON_SPACING     = 5
TOPBAR_NOTIFICATION_SPACING = 5

# Radius for rounded corners
RADIUS = {
    'button': 8,
    'app_button': 20,
    'tab':    6,
    'warning':6,
    'modal':  6,
    'input':  6,
    'app_icon': 15,
    'slider': 4,
    'slider_knob':6,
}

COLORS['slider_bg']          = (80, 80, 80)
COLORS['slider_fill']        = (50, 150, 250)
COLORS['slider_knob']        = (200, 200, 200)
COLORS['slider_active_knob'] = (255, 255, 255)
RADIUS['slider']             = 4
RADIUS['slider_knob']        = 6

# Scroll indicator settings
INDICATOR_RADIUS = 4
INDICATOR_SPACING = 10

# Font settings
FONT_NAME = './assets/fonts/Inter/Inter_18pt-SemiBold.ttf'
FONT_SIZE = 20

MUSIC_DIR = '/home/stefan/Music'
GAME_JSON = os.path.join(BASE_DIR, 'Games', 'games.json')

# Warning message duration (milliseconds)
WARNING_DURATION = 2000