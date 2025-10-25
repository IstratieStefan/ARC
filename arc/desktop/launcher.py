"""
ARC Desktop Launcher
Main application launcher for the ARC Desktop Environment
"""

import pygame
import os
import json
import subprocess
import time
import platform
import threading

# Change to project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
os.chdir(project_root)

# Import ARC modules
from arc.core import config, AppIcon, TabManager, Slider
from arc.desktop import (
    show_loading_screen, AudioLevelSlider, TopBar, WifiMenu,
    BluetoothMenu, StatusPoller, get_wifi_strength, get_bt_status
)

# Detect platform
IS_MACOS = platform.system() == 'Darwin'
IS_LINUX = platform.system() == 'Linux'

# Volume widget - Platform aware
def get_alsa_volume():
    if IS_MACOS:
        try:
            # Use osascript for macOS volume control
            output = subprocess.check_output(
                ["osascript", "-e", "output volume of (get volume settings)"],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            return int(float(output))
        except Exception:
            pass
        return 50
    elif IS_LINUX:
        try:
            output = subprocess.check_output(
                ["amixer", "get", "Master"], stderr=subprocess.DEVNULL
            ).decode()
            import re
            m = re.search(r'\[(\d+)%\]', output)
            if m:
                return int(m.group(1))
        except Exception:
            pass
        return 50
    return 50

def set_alsa_volume(val):
    val = max(0, min(100, int(val)))
    if IS_MACOS:
        try:
            subprocess.call(
                ["osascript", "-e", f"set volume output volume {val}"],
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass
    elif IS_LINUX:
        try:
            subprocess.call(["amixer", "set", "Master", f"{val}%"], stderr=subprocess.DEVNULL)
        except Exception:
            pass

volume_overlay = {
    "visible": False,
    "level": get_alsa_volume(),
    "last_shown": 0,
}
VOLUME_OVERLAY_DURATION = 0.5  # seconds

def draw_volume_overlay(screen, level):
    width, height = 350, 40
    x = (config.screen.width - width) // 2
    y = 40

    # Background rectangle with shadow
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)

    # Main rounded rectangle (background)
    pygame.draw.rect(overlay, (32, 32, 32, 230), overlay.get_rect(), border_radius=20)

    # Volume bar background
    bar_margin = 14
    bar_height = 12
    bar_rect = pygame.Rect(bar_margin, (height - bar_height) // 2, width - 2 * bar_margin, bar_height)
    pygame.draw.rect(overlay, (60, 60, 60), bar_rect, border_radius=6)

    # Volume bar foreground
    filled_width = int(bar_rect.width * level / 100)
    fg_rect = pygame.Rect(bar_rect.left, bar_rect.top, filled_width, bar_rect.height)
    pygame.draw.rect(overlay, config.colors.accent, fg_rect, border_radius=6)

    icon_rect = pygame.Rect(bar_rect.left - 28, bar_rect.top - 4, 20, 20)
    pygame.draw.polygon(overlay, (200, 200, 200), [
        (icon_rect.left, icon_rect.top + icon_rect.height // 2),
        (icon_rect.left + 8, icon_rect.top),
        (icon_rect.left + 8, icon_rect.bottom),
    ])

    screen.blit(overlay, (x, y))

pygame.init()
# Use windowed mode on macOS for easier development
if IS_MACOS:
    screen = pygame.display.set_mode(
        (config.screen.width, config.screen.height)
    )
else:
    screen = pygame.display.set_mode(
        (config.screen.width, config.screen.height),
        pygame.FULLSCREEN
    )
clock = pygame.time.Clock()
pygame.display.set_caption('ARC Launcher')

def on_volume_change(val):
    set_alsa_volume(val)
    volume_overlay["level"] = val
    volume_overlay["visible"] = True
    volume_overlay["last_shown"] = time.time()

volume_slider = Slider(
    rect=(50, config.screen.height - 60, 300, 8),
    min_val=0, max_val=100, init_val=get_alsa_volume(), callback=on_volume_change
)

CACHE_PATH = os.path.expanduser(os.path.join('~', '.cache', 'launcher_apps.json'))

def load_apps():
    if os.path.isfile(CACHE_PATH):
        try:
            with open(CACHE_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    apps = list(config.builtin_apps)
    apps_dir = config.apps_dir
    if os.path.isdir(apps_dir):
        for entry in os.scandir(apps_dir):
            if not entry.is_dir():
                continue
            manifest = os.path.join(entry.path, 'manifest.json')
            if not os.path.isfile(manifest):
                continue
            try:
                with open(manifest, 'r') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                continue
            icon = os.path.join(entry.path, data.get('icon', 'icon.png'))
            data['icon'] = icon
            apps.append(data)
    try:
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        with open(CACHE_PATH, 'w') as f:
            json.dump(apps, f)
    except Exception:
        pass
    return apps

def launch_app(cmd):
    try:
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        print('Launch failed', cmd, e)

def paginate_apps(apps):
    per_page = config.grid.cols * config.grid.rows
    return [apps[i:i + per_page] for i in range(0, len(apps), per_page)]

def build_page_icons(app_list):
    icons = []
    pad = config.grid.padding + 10
    for idx, app in enumerate(app_list):
        row, col = divmod(idx, config.grid.cols)
        x = config.grid.x_offset + pad + col * (config.cell.width + config.grid.margin)
        y = config.grid.y_offset + config.topbar.height + pad + row * (config.cell.height + config.grid.margin)
        rect = (x, y, config.cell.width, config.cell.height)
        icons.append(AppIcon(
            app.get('name', ''), app.get('icon', ''), rect,
            lambda c=app.get('exec', ''): launch_app(c)
        ))
    return icons

all_apps = load_apps()
pages = paginate_apps(all_apps)
pages_icons = [build_page_icons(p) for p in pages]
tab_names = [f"Page {i + 1}" for i in range(len(pages))]
tab_manager = TabManager(tab_names)
wifi_menu = WifiMenu(screen)
bt_menu = BluetoothMenu()
bt_menu.active = False
current_page = 0
sel_index = 0

class ChangeDetectingPoller:
    def __init__(self, func, interval=2):
        self.func = func
        self.interval = interval
        self.last_val = None
        self.on_change = None
        self.value = None
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self._stop_event.set()

    def get(self):
        return self.value

    def _run(self):
        while not self._stop_event.is_set():
            val = self.func()
            self.value = val
            if val != self.last_val:
                if self.on_change:
                    self.on_change(val)
                self.last_val = val
            time.sleep(self.interval)

need_redraw = True

def trigger_redraw(_=None):
    global need_redraw
    need_redraw = True

wifi_poller = ChangeDetectingPoller(get_wifi_strength, interval=5)
wifi_poller.on_change = trigger_redraw
bt_poller = ChangeDetectingPoller(get_bt_status, interval=5)
bt_poller.on_change = trigger_redraw
wifi_poller.start()
bt_poller.start()

topbar = TopBar(wifi_menu=wifi_menu, bt_menu=bt_menu, wifi_poller=wifi_poller, bt_poller=bt_poller)

running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
            break
        keys = pygame.key.get_pressed()
        # --- Volume key handling ---
        if ev.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            if ev.key == pygame.K_UP and mods & pygame.KMOD_ALT:
                vol = get_alsa_volume()
                vol = min(100, vol + 5)
                set_alsa_volume(vol)
                volume_overlay["level"] = vol
                volume_overlay["visible"] = True
                volume_overlay["last_shown"] = time.time()
                need_redraw = True
                continue
            if ev.key == pygame.K_DOWN and ev.key == pygame.KMOD_ALT:
                vol = get_alsa_volume()
                vol = max(0, vol - 5)
                set_alsa_volume(vol)
                volume_overlay["level"] = vol
                volume_overlay["visible"] = True
                volume_overlay["last_shown"] = time.time()
                need_redraw = True
                continue

        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if topbar.wifi_rect and topbar.wifi_rect.collidepoint(ev.pos):
                if wifi_menu.active:
                    wifi_menu.close()
                else:
                    wifi_menu.open()
                need_redraw = True
            elif topbar.bt_rect and topbar.bt_rect.collidepoint(ev.pos):
                if bt_menu.active is True:
                    bt_menu.active = False
                    bt_menu.close()
                elif bt_menu.active is False:
                    bt_menu.active = True
                    bt_menu.open()
                need_redraw = True

        if (wifi_menu.active and
                (not wifi_menu.password_box or not wifi_menu.password_box.active)
                and ev.type == pygame.KEYDOWN
                and ev.key == pygame.K_ESCAPE):
            wifi_menu.close()
            need_redraw = True

        if bt_menu.active and ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            bt_menu.close()
            need_redraw = True

        if wifi_menu.active:
            wifi_menu.handle_event(ev)
            need_redraw = True
            continue

        if bt_menu.active:
            bt_menu.handle_event(ev)
            need_redraw = True
            continue

        current_page = tab_manager.get_active_index()
        current_icons = pages_icons[current_page] if pages_icons else []
        sel_index = max(0, min(sel_index, len(current_icons) - 1))

        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_LEFT and sel_index % config.grid.cols > 0:
                sel_index -= 1
                need_redraw = True
            elif ev.key == pygame.K_q and (ev.mod & pygame.KMOD_CTRL):
                running = False
                pygame.quit()
                break
            elif ev.key == pygame.K_RIGHT and sel_index % config.grid.cols < config.grid.cols - 1 \
                    and sel_index + 1 < len(current_icons):
                sel_index += 1
                need_redraw = True
            elif ev.key == pygame.K_UP:
                if sel_index // config.grid.cols > 0:
                    sel_index -= config.grid.cols
                else:
                    tab_manager.active = max(0, current_page - 1)
                    sel_index = 0
                need_redraw = True
            elif ev.key == pygame.K_DOWN:
                if sel_index // config.grid.cols < config.grid.rows - 1 \
                        and sel_index + config.grid.cols < len(current_icons):
                    sel_index += config.grid.cols
                else:
                    tab_manager.active = min(len(pages) - 1, current_page + 1)
                    sel_index = 0
                need_redraw = True
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and current_icons:
                idx = current_page * config.grid.cols * config.grid.rows + sel_index
                show_loading_screen(screen, message="Starting app...", duration=1.0)
                launch_app(all_apps[idx].get('exec', ''))
                need_redraw = True

        tab_manager.handle_event(ev)
        for icon in current_icons:
            icon.handle_event(ev)
        need_redraw = True

    if need_redraw:
        screen.fill(config.colors.background)
        if wifi_menu.active:
            wifi_menu.update()
            wifi_menu.draw()
        elif bt_menu.active:
            bt_menu.update()
            bt_menu.draw()
        else:
            topbar.draw(screen)
            tab_manager.draw(screen)
            for idx, icon in enumerate(current_icons):
                icon.hovered = (idx == sel_index)
                icon.draw(screen)
        if (volume_overlay["visible"] and
                (time.time() - volume_overlay["last_shown"]) < VOLUME_OVERLAY_DURATION):
            draw_volume_overlay(screen, volume_overlay["level"])
        else:
            volume_overlay["visible"] = False
        pygame.display.flip()
        need_redraw = False

    clock.tick(30)

pygame.quit()

