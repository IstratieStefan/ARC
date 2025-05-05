import pygame, os, json, subprocess
import config
from ui_elements import AppIcon, TabManager
from topbar import TopBar

pygame.init()
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Helper: discover apps from builtins, apps/, packages/
def load_apps():
    apps = []
    apps.extend(config.BUILTIN_APPS)
    def scan_dir(directory):
        if os.path.isdir(directory):
            for name in os.listdir(directory):
                d = os.path.join(directory, name)
                m = os.path.join(d, 'manifest.json')
                if os.path.isfile(m):
                    try:
                        data = json.load(open(m))
                        icon = os.path.join(d, data.get('icon', 'icon.png'))
                        data['icon'] = icon
                        apps.append(data)
                    except:
                        pass
    scan_dir(config.APPS_DIR)
    scan_dir(config.PACKAGES_DIR)
    return apps

# Launch helper
def launch_app(cmd):
    try:
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        print('Launch failed', cmd, e)

# Load and paginate apps
def paginate_apps(apps):
    per_page = config.GRID_COLS * config.GRID_ROWS
    return [apps[i:i+per_page] for i in range(0, len(apps), per_page)]

# Build AppIcon objects for a page
def build_page_icons(app_list):
    icons = []
    pad = config.GRID_PADDING + 10
    for idx, app in enumerate(app_list):
        row, col = divmod(idx, config.GRID_COLS)
        x = pad + col * (config.CELL_WIDTH  + config.GRID_MARGIN)
        y = (config.TOPBAR_HEIGHT +
             pad +
             row * (config.CELL_HEIGHT + config.GRID_MARGIN))
        rect = (x, y, config.CELL_WIDTH, config.CELL_HEIGHT)
        icons.append(AppIcon(
            app.get('name',''),
            app.get('icon',''),
            rect,
            lambda c=app.get('exec',''): launch_app(c),
        ))
    return icons


# Initialize data
all_apps = load_apps()
pages = paginate_apps(all_apps)
tab_names = [f"Page {i+1}" for i in range(len(pages))]
tab_manager = TabManager(tab_names)
pages_icons = [build_page_icons(p) for p in pages]

# Selection state per page
current_page = 0
sel_index = 0

# Top bar
topbar = TopBar()

running = True
while running:
    # Determine current icons
    current_page = tab_manager.get_active_index()
    current_icons = pages_icons[current_page] if pages_icons else []
    # Clamp selection
    sel_index = max(0, min(sel_index, len(current_icons)-1))

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_LEFT:
                # move left or wrap
                if sel_index % config.GRID_COLS > 0:
                    sel_index -= 1
            elif ev.key == pygame.K_RIGHT:
                if sel_index % config.GRID_COLS < config.GRID_COLS-1 and sel_index+1 < len(current_icons):
                    sel_index += 1
            elif ev.key == pygame.K_UP:
                if sel_index // config.GRID_COLS > 0:
                    sel_index -= config.GRID_COLS
                else:
                    # move to previous tab
                    tab_manager.active = max(0, current_page-1)
                    sel_index = 0
            elif ev.key == pygame.K_DOWN:
                if sel_index // config.GRID_COLS < config.GRID_ROWS-1 and sel_index+config.GRID_COLS < len(current_icons):
                    sel_index += config.GRID_COLS
                else:
                    # next tab
                    tab_manager.active = min(len(pages)-1, current_page+1)
                    sel_index = 0
            elif ev.key == pygame.K_RETURN:
                if current_icons:
                    launch_app(all_apps[current_page * config.GRID_COLS * config.GRID_ROWS + sel_index].get('exec',''))
        # Pass events to UI
        tab_manager.handle_event(ev)
        for icon in current_icons:
            icon.handle_event(ev)

    # Draw
    screen.fill(config.COLORS['background'])
    topbar.draw(screen)
    tab_manager.draw(screen)
    for idx, icon in enumerate(current_icons):
        icon.hovered = (idx == sel_index)
        icon.draw(screen)

    pygame.display.flip()
    clock.tick(config.FPS)

pygame.quit()
