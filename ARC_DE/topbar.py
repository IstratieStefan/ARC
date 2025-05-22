import pygame
import config
import subprocess
import threading
from datetime import datetime


class TopBar:
    def __init__(self, wifi_menu=None, bt_menu=None):
        self.h = config.TOPBAR_HEIGHT
        self.bg = config.TOPBAR_BG
        self.fg = config.TOPBAR_FG
        self.font = pygame.font.SysFont('Arial', 18)

        # Load left-side icons
        self.left_icons = []
        for path in config.TOPBAR_ICONS:
            try:
                img = pygame.image.load(path).convert_alpha()
                self.left_icons.append(pygame.transform.smoothscale(img, (20, 20)))
            except:
                self.left_icons.append(pygame.Surface((20, 20), pygame.SRCALPHA))

        # WiFi icons (strength)
        self.wifi_icons = []
        for path in config.TOPBAR_WIFI_ICONS:
            try:
                img = pygame.image.load(path).convert_alpha()
                self.wifi_icons.append(pygame.transform.smoothscale(img, (20, 20)))
            except:
                self.wifi_icons.append(pygame.Surface((20, 20), pygame.SRCALPHA))
        self.wifi_rect = None

        # Bluetooth icons (off, on, connected)
        self.bt_icons = []
        for path in [
            config.TOPBAR_ICON_BT_OFF,
            config.TOPBAR_ICON_BT_ON,
            config.TOPBAR_ICON_BT_CONNECTED
        ]:
            try:
                img = pygame.image.load(path).convert_alpha()
                self.bt_icons.append(pygame.transform.smoothscale(img, (20, 20)))
            except:
                self.bt_icons.append(pygame.Surface((20, 20), pygame.SRCALPHA))
        self.bt_rect = None

        # Store menu refs
        self.wifi_menu = wifi_menu
        self.bt_menu = bt_menu

        # Other right-side icons
        self.right_icons = []
        if config.TOPBAR_SHOW_MOBILE:
            self.right_icons.append(self._load_icon(config.TOPBAR_ICON_MOBILE))
        if config.TOPBAR_SHOW_BATTERY:
            self.right_icons.append(self._load_icon(config.TOPBAR_ICON_BATTERY))

    def _load_icon(self, path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, (20, 20))
        except:
            return pygame.Surface((20, 20), pygame.SRCALPHA)

    def get_wifi_strength(self):
        try:
            out = subprocess.check_output([
                'nmcli', '-t', '-f', 'ACTIVE,SIGNAL',
                'device', 'wifi', 'list'
            ], stderr=subprocess.DEVNULL).decode()
            for line in out.splitlines():
                parts = line.split(':')
                if parts[0] == 'yes' and len(parts) >= 2:
                    return int(parts[1])
        except:
            pass
        return None

    def get_bt_status(self):
        """
          0 - Bluetooth OFF
          1 - Bluetooth ON, not connected
          2 - Bluetooth ON, at least one device connected
        """
        try:
            out = subprocess.check_output(['bluetoothctl', 'show'], stderr=subprocess.DEVNULL, text=True)
            powered = False
            for line in out.splitlines():
                if line.strip().startswith("Powered:"):
                    powered = "yes" in line
                    break
            if not powered:
                return 0  # OFF

            out = subprocess.check_output(['bluetoothctl', 'devices'], stderr=subprocess.DEVNULL, text=True)
            for line in out.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    addr = parts[1]
                    info = subprocess.check_output(['bluetoothctl', 'info', addr], stderr=subprocess.DEVNULL, text=True)
                    for il in info.splitlines():
                        if il.strip().startswith("Connected:") and "yes" in il:
                            return 2  # CONNECTED

            return 1  # ON, but not connected

        except Exception:
            return 0  # If any error, treat as OFF

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.wifi_rect and self.wifi_rect.collidepoint(event.pos):
                if self.wifi_menu and self.wifi_menu.active:
                    self.wifi_menu.close()
                elif self.wifi_menu:
                    self.wifi_menu.open()
            if self.bt_rect and self.bt_rect.collidepoint(event.pos):
                print("bluetooth icon clicked")
                if self.bt_menu and self.bt_menu.active:
                    self.bt_menu.close()
                elif self.bt_menu:
                    self.bt_menu.open()

    def draw(self, surface):
        w = config.SCREEN_WIDTH
        h = self.h
        pygame.draw.rect(surface, self.bg, (0, 0, w, h))

        # Left icons
        x = config.TOPBAR_PADDING_LEFT
        for ico in self.left_icons:
            y = (h - ico.get_height()) // 2
            surface.blit(ico, (x, y))
            x += ico.get_width() + config.TOPBAR_ICON_SPACING

        # Clock
        clock_surf = None
        if config.TOPBAR_SHOW_CLOCK:
            now = datetime.now().strftime(config.TOPBAR_CLOCK_FORMAT)
            clock_surf = self.font.render(now, True, self.fg)
            cx = (w - clock_surf.get_width()) // 2
            cy = (h - clock_surf.get_height()) // 2
            surface.blit(clock_surf, (cx, cy))

        # Notifications
        if config.TOPBAR_SHOW_NOTIFICATIONS and clock_surf:
            dot_x = cx + clock_surf.get_width() + config.TOPBAR_NOTIFICATION_SPACING * 2
            dot_y = h // 2
            pygame.draw.circle(surface, config.NOTIFICATION_DOT, (dot_x, dot_y), 4)

        # Right-side icons: WiFi, Bluetooth, then others
        rx = w - config.TOPBAR_PADDING_RIGHT
        icons = []
        if config.TOPBAR_SHOW_WIFI and self.wifi_icons:
            strength = self.get_wifi_strength() or 0
            idx = min(len(self.wifi_icons) - 1, strength * len(self.wifi_icons) // 101)
            icons.append(('wifi', self.wifi_icons[idx]))
        if config.TOPBAR_SHOW_BT and self.bt_icons:
            bt_status = self.get_bt_status()  # 0=off, 1=on, 2=connected
            bt_icon = self.bt_icons[min(bt_status, 2)]
            icons.append(('bt', bt_icon))
        for ico in self.right_icons:
            icons.append(('other', ico))

        for name, ico in icons:
            rx -= config.TOPBAR_ICON_SPACING
            rx -= ico.get_width()
            y = (h - ico.get_height()) // 2
            surface.blit(ico, (rx, y))
            if name == 'wifi':
                self.wifi_rect = pygame.Rect(rx, y, ico.get_width(), ico.get_height())
            if name == 'bt':
                self.bt_rect = pygame.Rect(rx, y, ico.get_width(), ico.get_height())