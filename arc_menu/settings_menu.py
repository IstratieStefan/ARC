import pygame
import os
import subprocess

# Load icons (ensure these files exist)
VOLUME_ICON = pygame.image.load("assets/settings_menu/volume_high.png")
BRIGHTNESS_ICON = pygame.image.load("assets/settings_menu/brightness.png")
ACCENT_ICON = pygame.image.load("assets/settings_menu/palette.png")

# State for touch interaction
slider_dragging = None
slider_value = {}
scroll_offset = 0
scroll_start_y = None


def draw_settings_menu(screen, rect, font, events):
    """
    Draw a scrollable settings menu inside `rect`. Sliders respond to touch anywhere on the track.
    `events` should be pygame.event.get() passed in.
    """
    global scroll_offset, scroll_start_y

    content_height = 500
    # Create a transparent surface for all settings content
    content = pygame.Surface((rect.width, content_height), pygame.SRCALPHA)

    # Handle vertical scroll
    for ev in events:
        if ev.type == pygame.MOUSEBUTTONDOWN and rect.collidepoint(ev.pos):
            scroll_start_y = ev.pos[1]
        elif ev.type == pygame.MOUSEMOTION and ev.buttons[0] and scroll_start_y is not None:
            dy = ev.pos[1] - scroll_start_y
            scroll_offset = max(rect.height - content_height, min(0, scroll_offset + dy))
            scroll_start_y = ev.pos[1]
        elif ev.type == pygame.MOUSEBUTTONUP:
            scroll_start_y = None

    # Draw white background for the menu container
    pygame.draw.rect(screen, (255, 255, 255), rect, border_radius=12)

    # Populate content surface
    y = 10
    x = 20
    width = rect.width - 40

    # Volume slider
    y += draw_slider(content, VOLUME_ICON, x, y, width,
                     get_volume, set_volume, 'volume', events)
    # Brightness slider
    y += draw_slider(content, BRIGHTNESS_ICON, x, y, width,
                     get_brightness, set_brightness, 'brightness', events)
    y += 20

    # Other settings entries (with labels)
    options = ["Display", "Sound", "About"]
    for opt in options:
        r = pygame.Rect(x, y, width, 40)
        pygame.draw.rect(content, (240, 240, 240), r, border_radius=8)
        label_surf = font.render(opt, True, (0, 0, 0))
        content.blit(label_surf, (r.x + 10, r.y + (40 - label_surf.get_height()) // 2))
        y += 50

    # Accent color picker stub
    draw_color_picker(content, ACCENT_ICON, x, y, width)

    # Blit the content surface at the scrolled offset
    screen.blit(content, (rect.x, rect.y + scroll_offset))


def draw_slider(surface, icon, x, y, width, get_func, set_func, key, events):
    """
    Draws a slider without text label. Responds to touch anywhere on the slider rect.
    Returns the total vertical space used (height + margin).
    """
    global slider_dragging, slider_value

    height = 40
    slider_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (240, 240, 240), slider_rect, border_radius=8)
    surface.blit(icon, (x + 10, y + 8))

    # Track coordinates (leaving space for icon)
    track_x = x + 50
    track_w = width - 60
    track_y = y + height // 2

    # Initialize stored value
    if key not in slider_value:
        slider_value[key] = get_func()

    # Handle touch/mouse events for this slider
    for ev in events:
        if ev.type == pygame.MOUSEBUTTONDOWN and slider_rect.collidepoint(ev.pos):
            slider_dragging = key
            # Jump knob to touch point
            rel = ev.pos[0] - track_x
            slider_value[key] = int(max(0, min(rel, track_w)) / track_w * 100)
            set_func(slider_value[key])
        elif ev.type == pygame.MOUSEMOTION and ev.buttons[0] and slider_dragging == key:
            rel = ev.pos[0] - track_x
            slider_value[key] = int(max(0, min(rel, track_w)) / track_w * 100)
            set_func(slider_value[key])
        elif ev.type == pygame.MOUSEBUTTONUP and slider_dragging == key:
            slider_dragging = None

    # Draw track and knob
    pygame.draw.line(surface, (200, 200, 200), (track_x, track_y), (track_x + track_w, track_y), 4)
    knob_x = track_x + int(slider_value[key] / 100 * track_w)
    pygame.draw.circle(surface, (0, 122, 255), (knob_x, track_y), 7)

    return height + 20


def draw_color_picker(surface, icon, x, y, width):
    height = 40
    r = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (240, 240, 240), r, border_radius=8)
    surface.blit(icon, (x + 10, y + 8))
    # Placeholder circle
    pygame.draw.circle(surface, (5, 148, 250), (x + width - 25, y + height // 2), 10)

# ───────────────────────────────
# ALSA Volume Control

def get_volume():
    try:
        out = subprocess.check_output(["amixer", "get", "Master"]).decode()
        return int(out.split("[")[1].split("%")[0])
    except:
        return 50


def set_volume(pct):
    try:
        subprocess.run(["amixer", "set", "Master", f"{pct}%"], check=True)
    except:
        pass

# ───────────────────────────────
# SysFS Brightness Control

def get_brightness():
    try:
        base = "/sys/class/backlight"
        device = os.listdir(base)[0]
        with open(f"{base}/{device}/brightness") as f:
            cur = int(f.read())
        with open(f"{base}/{device}/max_brightness") as f:
            mx = int(f.read())
        return int(cur / mx * 100)
    except:
        return 50


def set_brightness(pct):
    try:
        base = "/sys/class/backlight"
        device = os.listdir(base)[0]
        with open(f"{base}/{device}/max_brightness") as f:
            mx = int(f.read())
        new = int(pct / 100 * mx)
        with open(f"{base}/{device}/brightness", "w") as f:
            f.write(str(new))
    except:
        pass

# ───────────────────────────────
# Helper to disable app touches when settings is open

def event_consumed_by_settings(ev, rect):
    return hasattr(ev, 'pos') and rect.collidepoint(ev.pos)
