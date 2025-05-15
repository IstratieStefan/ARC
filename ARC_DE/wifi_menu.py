import pygame
import subprocess
import threading
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

class WifiMenu:
    def __init__(self, screen):
        # dependencies
        self.screen = screen
        self.active = False

        # preload icons once
        ICON_SIZE = (24, 24)
        self.lock_icon = load_icon(LOCK_ICON_PATH, ICON_SIZE)
        self.open_icon = load_icon(OPEN_ICON_PATH, ICON_SIZE)

        # font and timing
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
        self.clock = pygame.time.Clock()

        # Wi-Fi state
        self.networks = ['<scanning...>']
        self.icons    = [None]
        self.scan_done = [False]
        self.password_box = None
        self.current_ssid = None

        # setup scrollable list
        inset = 10
        title_h = FONT_SIZE + inset
        list_rect = (inset, title_h,
                     SCREEN_WIDTH - 2*inset,
                     SCREEN_HEIGHT - title_h - inset)

        self.wifi_list = ScrollableList(
            items=self.networks,
            rect=list_rect,
            font=self.font,
            line_height=LINE_HEIGHT,
            text_color=TEXT_COLOR,
            bg_color=BG_COLOR,
            sel_color=HIGHLIGHT,
            callback=self.on_connect,
            icons=self.icons,
            icon_size=ICON_SIZE,
            icon_padding=10
        )

        # start scanning thread
        threading.Thread(target=self._scan_loop,
                         daemon=True).start()

    def open(self):
        """Show the Wi-Fi overlay"""
        self.active = True

    def close(self):
        """Hide the Wi-Fi overlay"""
        self.active = False
        self.password_box = None
        self.wifi_list.set_enabled(True)

    def _scan_loop(self):
        while True:
            try:
                subprocess.run(['nmcli','device','wifi','rescan'],
                               check=True, stderr=subprocess.DEVNULL)
                output = subprocess.check_output([
                    'nmcli','-t','-f','SSID,SIGNAL,SECURITY',
                    'device','wifi','list'
                ], stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
                found, icon_list = [], []
                for line in output.splitlines():
                    if not line:
                        continue
                    ssid, signal, sec = line.split(':',2)
                    label = f"{ssid or '<hidden>'} [{signal}%] {sec}"
                    found.append(label)
                    icon_list.append(
                        self.open_icon if sec.strip().upper() in ('--','NONE','')
                        else self.lock_icon
                    )
                self.networks[:] = found or ['<no networks>']
                self.icons[:]    = icon_list or [None]
            except Exception:
                self.networks[:] = ['<scan failed>']
                self.icons[:]    = [None]

            # update list widget
            self.wifi_list.items = list(self.networks)
            self.wifi_list.icons = list(self.icons)
            self.wifi_list.max_offset = max(
                0,
                len(self.wifi_list.items)*LINE_HEIGHT - self.wifi_list.rect.height
            )
            self.scan_done[0] = True
            time.sleep(SCAN_INTERVAL)

    def on_connect(self, selection):
        ssid = selection.split(' [')[0]
        sec  = selection.rsplit('] ',1)[-1]
        is_open = sec.strip().upper() in ('--','NONE','')
        self.wifi_list.set_enabled(False)
        if is_open:
            self._do_connect(ssid)
        else:
            self.password_box = SearchBox(
                rect=(50, SCREEN_HEIGHT//2 - 20,
                      SCREEN_WIDTH-100, 40),
                placeholder='Enter WiFi password',
                callback=lambda pw: self._do_connect(ssid, pw)
            )
            self.password_box.active = True

    def _do_connect(self, ssid, password=None):
        # disconnect existing
        if self.current_ssid and self.current_ssid != ssid:
            try:
                subprocess.run(
                    ['nmcli','connection','down','id', self.current_ssid],
                    check=True
                )
            except Exception:
                pass

        # connect new
        cmd = ['nmcli','device','wifi','connect', ssid]
        if password:
            cmd += ['password', password]
        try:
            subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
            MessageBox(f"Connected to {ssid}", lambda: None, lambda: None).show()
            self.current_ssid = ssid
        except subprocess.CalledProcessError:
            MessageBox(f"Failed to connect to {ssid}", lambda: None, lambda: None).show()
        finally:
            self.wifi_list.set_enabled(True)
            self.password_box = None

    def handle_event(self, evt):
        if self.password_box:
            if evt.type == pygame.KEYDOWN and evt.key == pygame.K_ESCAPE:
                self.password_box = None
                self.wifi_list.set_enabled(True)
            else:
                self.password_box.handle_event(evt)
        else:
            self.wifi_list.handle_event(evt)

    def update(self):
        if self.password_box:
            self.password_box.update()
        else:
            self.wifi_list.update()

    def draw(self):
        self.screen.fill(BG_COLOR)
        # title
        title = self.font.render('Wi-Fi Networks', True, TEXT_COLOR)
        self.screen.blit(
            title,
            ((SCREEN_WIDTH - title.get_width())//2, LINE_HEIGHT//2)
        )
        # list or password prompt
        self.wifi_list.draw(self.screen)
        if self.password_box:
            self.password_box.draw(self.screen)
        elif not self.scan_done[0]:
            hint = self.font.render('Scanning Wi-Fi...', True, TEXT_COLOR)
            self.screen.blit(
                hint,
                ((SCREEN_WIDTH - hint.get_width())//2,
                 SCREEN_HEIGHT - 30)
            )