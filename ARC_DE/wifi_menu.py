import pygame
import sys
import threading
import subprocess
import time
import config
from ui_elements import ScrollableList, MessageBox, SearchBox

SCREEN_WIDTH  = config.SCREEN_WIDTH
SCREEN_HEIGHT = config.SCREEN_HEIGHT
BG_COLOR      = config.COLORS['background_light']
TEXT_COLOR    = config.COLORS['text_light']
HIGHLIGHT     = config.ACCENT_COLOR
FONT_NAME     = config.FONT_NAME
FONT_SIZE     = config.FONT_SIZE
LINE_HEIGHT   = FONT_SIZE + 10
FPS           = config.FPS
SCAN_INTERVAL = getattr(config, 'WIFI_SCAN_INTERVAL', 10)

LOCK_ICON_PATH = "/icons/wifi_locked.png"
OPEN_ICON_PATH = "/icons/wifi_unlocked.png"

def load_icon(path, size):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size)
    except Exception:
        return None

# preload icons
pygame.init()
ICON_SIZE = (24, 24)
lock_icon = load_icon(LOCK_ICON_PATH, ICON_SIZE)
open_icon = load_icon(OPEN_ICON_PATH, ICON_SIZE)
pygame.quit()

def scan_wifi(devices, icons, device_list, done_flag):
    while not done_flag[0]:
        try:
            subprocess.run(['nmcli', 'device', 'wifi', 'rescan'], check=True, stderr=subprocess.DEVNULL)
            output = subprocess.check_output([
                'nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY',
                'device', 'wifi', 'list'
            ], stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
            found, icon_list = [], []
            for line in output.splitlines():
                if not line:
                    continue
                ssid, signal, sec = line.split(':', 2)
                label = f"{ssid or '<hidden>'} [{signal}%] {sec}"
                found.append(label)
                icon_list.append(open_icon if sec.strip().upper() in ('--','NONE','') else lock_icon)
            devices[:] = found or ['<no networks>']
            icons[:]   = icon_list or [None]
        except Exception:
            devices[:] = ['<scan failed>']
            icons[:]   = [None]
        device_list.items = list(devices)
        device_list.icons = list(icons)
        device_list.max_offset = max(0, len(device_list.items) * LINE_HEIGHT - device_list.rect.height)
        done_flag[0] = True
        time.sleep(SCAN_INTERVAL)

def WifiMenu():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('WiFi Networks')
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
    networks = ['<scanning...>']
    icons    = [None]
    scan_done = [False]
    password_box = None
    current_ssid = None

    def do_connect(ssid, password=None):
        nonlocal current_ssid, password_box
        # disconnect existing if different
        if current_ssid and current_ssid != ssid:
            try:
                subprocess.run(['nmcli', 'connection', 'down', 'id', current_ssid], check=True)
            except Exception:
                pass
        # connect new
        cmd = ['nmcli', 'device', 'wifi', 'connect', ssid]
        if password:
            cmd += ['password', password]
        try:
            subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
            MessageBox(f"Connected to {ssid}", lambda: None, lambda: None).show()
            current_ssid = ssid
        except subprocess.CalledProcessError:
            MessageBox(f"Failed to connect to {ssid}", lambda: None, lambda: None).show()
        finally:
            wifi_list.set_enabled(True)
            password_box = None

    def attempt_connect(pw):
        ssid = wifi_list.items[wifi_list.selected_index].split(' [')[0]
        do_connect(ssid, pw)

    def on_connect(selection):
        nonlocal password_box
        ssid = selection.split(' [')[0]
        sec = selection.rsplit('] ', 1)[-1]
        is_open = sec.strip().upper() in ('--','NONE','')
        wifi_list.set_enabled(False)
        if is_open:
            do_connect(ssid)
        else:
            password_box = SearchBox(
                rect=(50, SCREEN_HEIGHT//2 - 20, SCREEN_WIDTH - 100, 40),
                placeholder='Enter WiFi password',
                callback=attempt_connect
            )
            password_box.active = True

    inset = 10
    title_h = FONT_SIZE + inset
    list_rect = (inset, title_h, SCREEN_WIDTH - 2*inset, SCREEN_HEIGHT - title_h - inset)

    wifi_list = ScrollableList(
        items=networks,
        rect=list_rect,
        font=font,
        line_height=LINE_HEIGHT,
        text_color=TEXT_COLOR,
        bg_color=BG_COLOR,
        sel_color=HIGHLIGHT,
        callback=on_connect,
        icons=icons,
        icon_size=ICON_SIZE,
        icon_padding=10
    )

    threading.Thread(target=scan_wifi, args=(networks, icons, wifi_list, scan_done), daemon=True).start()

    running = True
    while running:
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                running = False
            if password_box and evt.type == pygame.KEYDOWN and evt.key == pygame.K_ESCAPE:
                password_box = None
                wifi_list.set_enabled(True)
            elif password_box:
                password_box.handle_event(evt)
            else:
                wifi_list.handle_event(evt)

        if password_box:
            password_box.update()
        else:
            wifi_list.update()

        screen.fill(BG_COLOR)
        title = font.render('Wifi Networks', True, TEXT_COLOR)
        screen.blit(title, ((SCREEN_WIDTH - title.get_width())//2, inset//2))

        wifi_list.draw(screen)
        if password_box:
            password_box.draw(screen)
        elif not scan_done[0]:
            hint = font.render('Scanning WiFi...', True, TEXT_COLOR)
            screen.blit(hint, ((SCREEN_WIDTH - hint.get_width())//2, SCREEN_HEIGHT - inset - hint.get_height()))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()
