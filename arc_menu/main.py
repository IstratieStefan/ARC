import pygame
import sys
import subprocess
from topbar import TopBar
from settings_menu import draw_settings_menu
from wifi_menu import draw_wifi_menu
from bluetooth_menu import draw_bluetooth_menu
from app_list import apps

pygame.init()

# Screen setup
WIDTH, HEIGHT = 480, 320
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Menu")
clock = pygame.time.Clock()
font = pygame.font.Font("assets/fonts/Inter/Inter_24pt-SemiBold.ttf", 24)
floating_menu_box = pygame.Rect(0, 42, 480, 300)

# Colors
BG = (15, 15, 15)
BLACK = (0, 0, 0)
WHITE = (217, 217, 217)
GRAY = (240, 240, 240)
ACCENT = (5, 148, 250)

# Grid layout
ICON_SIZE = 84
SPACING_X = 15
SPACING_Y = 15
COLS = 4
ROWS = 2
APPS_PER_PAGE = ROWS * COLS

GRID_WIDTH = COLS * ICON_SIZE + (COLS - 1) * SPACING_X
GRID_HEIGHT = ROWS * ICON_SIZE + (ROWS - 1) * SPACING_Y
START_X = (WIDTH - GRID_WIDTH) // 2
START_Y = (HEIGHT - GRID_HEIGHT) // 2

# Top bar
topbar = TopBar()

# State
selected_index = 0
current_page = 0
wifi_menu_open = False
bluetooth_menu_open = False
settings_menu_open = False
start_pos = None  # For swipe gesture

app_pressed = None       # Index of tapped app
app_press_time = 0
ANIMATION_DURATION = 150  # ms
did_scroll = False        # Whether this touch was a scroll


def get_visible_apps():
    start = current_page * APPS_PER_PAGE
    end = start + APPS_PER_PAGE
    return apps[start:end]


def draw_icons():
    visible_apps = get_visible_apps()
    now = pygame.time.get_ticks()

    for idx, app in enumerate(visible_apps):
        row = idx // COLS
        col = idx % COLS
        x = START_X + col * (ICON_SIZE + SPACING_X)
        y = START_Y + row * (ICON_SIZE + SPACING_Y)
        rect = pygame.Rect(x, y, ICON_SIZE, ICON_SIZE)

        # Pressed animation
        is_pressed = (idx == app_pressed and now - app_press_time < ANIMATION_DURATION)
        scale = 0.95 if is_pressed else 1.0
        scaled_rect = rect.inflate(-ICON_SIZE * (1 - scale), -ICON_SIZE * (1 - scale))

        if idx == selected_index:
            pygame.draw.rect(screen, ACCENT, scaled_rect.inflate(8, 8), border_radius=15)
        pygame.draw.rect(screen, WHITE, scaled_rect, border_radius=12)

        icon = app["icon"]
        icon_rect = icon.get_rect(center=scaled_rect.center)
        screen.blit(icon, icon_rect)


def draw_bottom_label():
    visible_apps = get_visible_apps()
    global selected_index  # needed if you want to modify it here

    if selected_index >= len(visible_apps):
        selected_index = max(0, len(visible_apps) - 1)

    if visible_apps:
        label = font.render(visible_apps[selected_index]["label"], True, WHITE)
        screen.blit(label, ((WIDTH - label.get_width()) // 2, HEIGHT - 24 - 26))



def draw_page_dots():
    total_pages = (len(apps) + APPS_PER_PAGE - 1) // APPS_PER_PAGE
    if total_pages <= 1:
        return

    dot_radius = 5
    spacing = 16
    padding_y = 6
    padding_x = 6

    rect_height = total_pages * spacing + padding_y * 2 - 3
    rect_width = dot_radius * 2 + padding_x * 2
    rect_x = WIDTH - rect_width - 10
    rect_y = START_Y + (GRID_HEIGHT - rect_height) // 2

    start_y = rect_y + padding_y + dot_radius + 1
    center_x = rect_x + rect_width // 2

    for i in range(total_pages):
        y = start_y + i * spacing
        if i == current_page:
            pygame.draw.circle(screen, ACCENT, (center_x, y), dot_radius)
        else:
            pygame.draw.circle(screen, WHITE, (center_x, y), dot_radius - 1)


def launch_app(app):
    try:
        subprocess.Popen(app["command"].split())
        print(f"Launched: {app['command']}")
    except Exception as e:
        print(f"Failed to launch {app['label']}: {e}")


# Main loop
running = True
while running:
    screen.fill(BG)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if wifi_menu_open or bluetooth_menu_open:
                continue

            visible_apps = get_visible_apps()
            if event.key == pygame.K_RIGHT:
                selected_index = (selected_index + 1) % min(len(visible_apps), APPS_PER_PAGE)
            elif event.key == pygame.K_LEFT:
                selected_index = (selected_index - 1) % min(len(visible_apps), APPS_PER_PAGE)
            elif event.key == pygame.K_UP:
                if selected_index >= COLS:
                    selected_index -= COLS
                elif current_page > 0:
                    current_page -= 1
                    visible = get_visible_apps()
                    selected_index = min(len(visible) - 1, selected_index + (APPS_PER_PAGE - COLS))
            elif event.key == pygame.K_DOWN:
                visible = get_visible_apps()
                if selected_index + COLS < len(visible):
                    selected_index += COLS
                elif (current_page + 1) * APPS_PER_PAGE < len(apps):
                    current_page += 1
                    selected_index = max(0, selected_index - (APPS_PER_PAGE - COLS))
            elif event.key == pygame.K_RETURN:
                if visible_apps:
                    launch_app(visible_apps[selected_index])
            elif event.key == pygame.K_PAGEUP:
                if current_page > 0:
                    current_page -= 1
                    selected_index = 0
            elif event.key == pygame.K_PAGEDOWN:
                if (current_page + 1) * APPS_PER_PAGE < len(apps):
                    current_page += 1
                    selected_index = 0

        elif event.type == pygame.MOUSEBUTTONDOWN:
            start_pos = event.pos
            did_scroll = False  # reset
            clicked = topbar.handle_click(event.pos)
            if clicked == "apps":
                wifi_menu_open = False
                bluetooth_menu_open = False
            elif clicked == "settings":
                wifi_menu_open = False
                bluetooth_menu_open = False
                settings_menu_open = not settings_menu_open
            elif clicked == "wifi":
                bluetooth_menu_open = False
                wifi_menu_open = not wifi_menu_open
            elif clicked == "bluetooth":
                wifi_menu_open = False
                bluetooth_menu_open = not bluetooth_menu_open

            # App tap detection
            visible = get_visible_apps()
            for idx, app in enumerate(visible):
                row = idx // COLS
                col = idx % COLS
                x = START_X + col * (ICON_SIZE + SPACING_X)
                y = START_Y + row * (ICON_SIZE + SPACING_Y)
                rect = pygame.Rect(x, y, ICON_SIZE, ICON_SIZE)
                if rect.collidepoint(event.pos):
                    selected_index = idx
                    app_pressed = idx
                    app_press_time = pygame.time.get_ticks()

        elif event.type == pygame.MOUSEBUTTONUP and start_pos:
            end_pos = event.pos
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]

            if abs(dy) > abs(dx) and abs(dy) > 30:
                did_scroll = True
                if dy < 0 and (current_page + 1) * APPS_PER_PAGE < len(apps):
                    current_page += 1
                    selected_index = 0
                elif dy > 0 and current_page > 0:
                    current_page -= 1
                    selected_index = 0

            start_pos = None

    topbar.draw(screen)

    if wifi_menu_open:
        draw_wifi_menu(screen, floating_menu_box)
        pygame.display.set_caption("Wi-Fi Menu")
    elif bluetooth_menu_open:
        draw_bluetooth_menu(screen, floating_menu_box)
        pygame.display.set_caption("Bluetooth Menu")
    elif settings_menu_open:
        draw_settings_menu(screen, floating_menu_box, font, pygame.event.get())
        pygame.display.set_caption("Settings Menu")
    else:
        draw_icons()
        draw_bottom_label()
        draw_page_dots()
        pygame.display.set_caption(f"Apps — Page {current_page + 1}")

    # Launch after animation if no scroll
    if app_pressed is not None:
        if pygame.time.get_ticks() - app_press_time >= ANIMATION_DURATION:
            if not did_scroll:
                visible = get_visible_apps()
                if 0 <= app_pressed < len(visible):
                    launch_app(visible[app_pressed])
            app_pressed = None
            did_scroll = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
