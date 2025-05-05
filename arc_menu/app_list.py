import pygame

def load_icon(path):
    return pygame.transform.scale(pygame.image.load(path).convert_alpha(), (48, 48))

apps = [
    {
        "label": "Terminal",
        "icon": load_icon("assets/app_icons/terminal.png"),
        "command": "alacritty"
    },
    {
        "label": "Web Browser",
        "icon": load_icon("assets/app_icons/web.png"),
        "command": "firefox"
    },
    {
        "label": "File Manager",
        "icon": load_icon("assets/app_icons/files.png"),
        "command": "dolphin"
    },
    {
        "label": "NFC tools",
        "icon": load_icon("../nfc_tools/nfc.png"),
        "command": "python3 ../nfc_tools/ui_test.py"
    },
    {
        "label": "RF tools",
        "icon": load_icon("../rf_tools/rf.png"),
        "command": "python3 ../rf_tools/ui_test.py"
    },
    {
        "label": "IR tools",
        "icon": load_icon("../IR_tools/ir.png"),
        "command": "python3 ../IR_tools/ui_test.py"
    },
    {
        "label": "WiFi tools",
        "icon": load_icon("../wifi_tools/wifi.png"),
        "command": "python3 ../wifi_tools/ui_test.py"
    },
    {
        "label": "SMS",
        "icon": load_icon("assets/app_icons/sms.png"),
        "command": "sms-app"
    },
    {
        "label": "Music",
        "icon": load_icon("../music_player/music.png"),
        "command": "python3 ../music_player/ui_test.py"
    },
    {
        "label": "Games",
        "icon": load_icon("../games_menu/games.png"),
        "command": "games"
    }


]
