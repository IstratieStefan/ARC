import pygame, os, json, subprocess
from ARC_DE.loading_screen import show_loading_screen
import ui_elements
os.chdir(os.path.dirname(os.path.realpath(__file__)))
from config import config
from ui_elements import AppIcon, TabManager, Slider
from ARC_DE.volume_widget import AudioLevelSlider
from ARC_DE.topbar import TopBar
from ARC_DE.wifi_menu import WifiMenu
from ARC_DE.bluetooth_menu import BluetoothMenu
from ARC_DE.status_poller import StatusPoller
from ARC_DE.arc_status import get_wifi_strength, get_bt_status

# Main launcher code
pygame.init()
screen = pygame.display.set_mode(
    (config.screen.width, config.screen.height),
    pygame.FULLSCREEN
)
clock = pygame.time.Clock()
pygame.display.set_caption('ARC Launcher')

def on_volume_change(val):
    # Set volume somewhere if needed; this is not in your config anymore
    pass

volume_slider = Slider(
    rect=(50, config.screen.height - 60, 300, 8),
    min_val=0, max_val=100, init_val=50, callback=on_volume_change
)

CACHE_PATH = os.path.expanduser(os.path.join('~', '.cache', 'launcher_apps.json'))

def load_apps():
    if os.path.isfile(CACHE_PATH):
        try:
            with open(CACHE_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    # Use the list from YAML
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
    return [apps[i:i+per_page] for i in range(0, len(apps), per_page)]

def build_page_icons(app_list):
    icons = []
    pad = config.grid.padding + 10
    for idx, app in enumerate(app_list):
        row, col = divmod(idx, config.grid.cols)
        x = config.grid.x_offset + pad + col * (config.cell.width + config.grid.margin)
        y = config.grid.y_offset+ config.topbar.height + pad + row * (config.cell.height + config.grid.margin)
        rect = (x, y, config.cell.width, config.cell.height)
        icons.append(AppIcon(
            app.get('name',''), app.get('icon',''), rect,
            lambda c=app.get('exec',''): launch_app(c)
        ))
    return icons

# Initialize data
all_apps = load_apps()
pages = paginate_apps(all_apps)
pages_icons = [build_page_icons(p) for p in pages]
tab_names = [f"Page {i+1}" for i in range(len(pages))]
tab_manager = TabManager(tab_names)
wifi_menu = WifiMenu(screen)
bt_menu = BluetoothMenu()
bt_menu.active = False
current_page = 0
sel_index = 0

# Top bar icon pollers with change detection
import time
class ChangeDetectingPoller(StatusPoller):
    def __init__(self, func, interval=2):
        super().__init__(func, interval)
        self.last_val = None
        self.on_change = None

    def run(self):
        while not self._stop_event.is_set():
            val = self.func()
            if val != self.last_val:
                if self.on_change:
                    self.on_change(val)
                self.last_val = val
            time.sleep(self.interval)

need_redraw = True  # Initial redraw

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

        # Otherwise, grid navigation
        current_page = tab_manager.get_active_index()
        current_icons = pages_icons[current_page] if pages_icons else []
        sel_index = max(0, min(sel_index, len(current_icons)-1))

        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_LEFT and sel_index % config.grid.cols > 0:
                sel_index -= 1
                need_redraw = True
            elif ev.key == pygame.K_q and (ev.mod & pygame.KMOD_CTRL):
                running = False
                pygame.quit()
                break
            elif ev.key == pygame.K_RIGHT and sel_index % config.grid.cols < config.grid.cols-1 \
                 and sel_index+1 < len(current_icons):
                sel_index += 1
                need_redraw = True
            elif ev.key == pygame.K_UP:
                if sel_index // config.grid.cols > 0:
                    sel_index -= config.grid.cols
                else:
                    tab_manager.active = max(0, current_page-1)
                    sel_index = 0
                need_redraw = True
            elif ev.key == pygame.K_DOWN:
                if sel_index // config.grid.cols < config.grid.rows-1 \
                   and sel_index+config.grid.cols < len(current_icons):
                    sel_index += config.grid.cols
                else:
                    tab_manager.active = min(len(pages)-1, current_page+1)
                    sel_index = 0
                need_redraw = True
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and current_icons:
                idx = current_page * config.grid.cols * config.grid.rows + sel_index
                show_loading_screen(screen, message="Starting app...", duration=1.0)
                launch_app(all_apps[idx].get('exec',''))
                need_redraw = True

        tab_manager.handle_event(ev)
        for icon in current_icons:
            icon.handle_event(ev)
        need_redraw = True

    # --- Only redraw if necessary ---
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
        pygame.display.flip()
        need_redraw = False

    clock.tick(30)

pygame.quit()
