import pygame, os, json, subprocess

import ui_elements

os.chdir(os.path.dirname(os.path.realpath(__file__)))
import config
from ui_elements import AppIcon, TabManager, Slider
from ARC_DE.volume_widget import AudioLevelSlider
from ARC_DE.topbar import TopBar
from ARC_DE.wifi_menu import WifiMenu

# Main launcher code
pygame.init()
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()
pygame.display.set_caption('ARC Launcher')

# Volume slider (if you need it)
def on_volume_change(val):
    config.VOLUME = int(val)

volume_slider = Slider(
    rect=(50, config.SCREEN_HEIGHT - 60, 300, 8),
    min_val=0, max_val=100, init_val=50, callback=on_volume_change
)

CACHE_PATH = os.path.expanduser(os.path.join('~', '.cache', 'launcher_apps.json'))

def load_apps():
    #Try loading from cache
    if os.path.isfile(CACHE_PATH):
        try:
            with open(CACHE_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            pass

    #Otherwise do a fresh scan
    apps = list(config.BUILTIN_APPS)
    apps_dir = config.APPS_DIR
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

    #Write the result back to cache
    try:
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        with open(CACHE_PATH, 'w') as f:
            json.dump(apps, f)
    except Exception:
        # if we can't write cache (permissions?), just ignore
        pass

    return apps

def launch_app(cmd):
    try:
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        print('Launch failed', cmd, e)

# Pagination (grid) helpers
def paginate_apps(apps):
    per_page = config.GRID_COLS * config.GRID_ROWS
    return [apps[i:i+per_page] for i in range(0, len(apps), per_page)]

def build_page_icons(app_list):
    icons = []
    pad = config.GRID_PADDING + 10
    for idx, app in enumerate(app_list):
        row, col = divmod(idx, config.GRID_COLS)
        x = pad + col * (config.CELL_WIDTH + config.GRID_MARGIN)
        y = config.TOPBAR_HEIGHT + pad + row * (config.CELL_HEIGHT + config.GRID_MARGIN)
        rect = (x, y, config.CELL_WIDTH, config.CELL_HEIGHT)
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
current_page = 0
sel_index = 0

topbar = TopBar()

running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
            break


        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if topbar.wifi_rect and topbar.wifi_rect.collidepoint(ev.pos):
                # directly call on the injected menu
                if wifi_menu.active:
                    wifi_menu.close()
                else:
                    wifi_menu.open()

        if wifi_menu.active and (not wifi_menu.password_box or not wifi_menu.password_box.active) and ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            wifi_menu.close()



        if wifi_menu.active:
            wifi_menu.handle_event(ev)
            continue


        # Otherwise, grid navigation
        current_page = tab_manager.get_active_index()
        current_icons = pages_icons[current_page] if pages_icons else []
        sel_index = max(0, min(sel_index, len(current_icons)-1))

        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_LEFT and sel_index % config.GRID_COLS > 0:
                sel_index -= 1
            elif ev.key == pygame.K_q and (ev.mod & pygame.KMOD_CTRL):
                    running = False
                    pygame.quit()
            elif ev.key == pygame.K_RIGHT and sel_index % config.GRID_COLS < config.GRID_COLS-1 \
                 and sel_index+1 < len(current_icons):
                sel_index += 1
            elif ev.key == pygame.K_UP:
                if sel_index // config.GRID_COLS > 0:
                    sel_index -= config.GRID_COLS
                else:
                    tab_manager.active = max(0, current_page-1)
                    sel_index = 0
            elif ev.key == pygame.K_DOWN:
                if sel_index // config.GRID_COLS < config.GRID_ROWS-1 \
                   and sel_index+config.GRID_COLS < len(current_icons):
                    sel_index += config.GRID_COLS
                else:
                    tab_manager.active = min(len(pages)-1, current_page+1)
                    sel_index = 0
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and current_icons:
                idx = current_page * config.GRID_COLS * config.GRID_ROWS + sel_index
                launch_app(all_apps[idx].get('exec',''))
                pygame.display.iconify()

        # Pass through to UI elements
        tab_manager.handle_event(ev)
        for icon in current_icons:
            icon.handle_event(ev)

    # Draw
    screen.fill(config.COLORS['background'])

    if wifi_menu.active:
        wifi_menu.update()
        wifi_menu.draw()
    else:
        topbar.draw(screen)
        tab_manager.draw(screen)
        for idx, icon in enumerate(current_icons):
            icon.hovered = (idx == sel_index)
            icon.draw(screen)

    pygame.display.flip()
    clock.tick(config.FPS)

pygame.quit()