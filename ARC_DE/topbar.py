import pygame
from config import config  # or from config import config
from datetime import datetime

class TopBar:
    def __init__(self, wifi_menu=None, bt_menu=None, wifi_poller=None, bt_poller=None):
        self.h = config.topbar.height
        self.bg = tuple(config.topbar.bg)
        self.fg = tuple(config.topbar.fg)
        self.font = pygame.font.SysFont('Arial', 18)

        self.wifi_poller = wifi_poller
        self.bt_poller = bt_poller
        # Load left-side icons
        self.left_icons = []
        for path in config.topbar.icons:
            try:
                img = pygame.image.load(path).convert_alpha()
                self.left_icons.append(pygame.transform.smoothscale(img, (20, 20)))
            except:
                self.left_icons.append(pygame.Surface((20, 20), pygame.SRCALPHA))

        # WiFi icons (strength)
        self.wifi_icons = []
        for path in config.topbar.wifi_icons:
            try:
                img = pygame.image.load(path).convert_alpha()
                self.wifi_icons.append(pygame.transform.smoothscale(img, (20, 20)))
            except:
                self.wifi_icons.append(pygame.Surface((20, 20), pygame.SRCALPHA))
        self.wifi_rect = None

        # Bluetooth icons (off, on, connected)
        self.bt_icons = []
        for path in [
            config.topbar.icon_bt_off,
            config.topbar.icon_bt_on,
            config.topbar.icon_bt_connected
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
        if config.topbar.show_mobile:
            self.right_icons.append(self._load_icon(config.topbar.icon_mobile))
        if config.topbar.show_battery:
            self.right_icons.append(self._load_icon(config.topbar.icon_battery))

    def _load_icon(self, path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, (20, 20))
        except:
            return pygame.Surface((20, 20), pygame.SRCALPHA)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.wifi_rect and self.wifi_rect.collidepoint(event.pos):
                if self.wifi_menu and self.wifi_menu.active:
                    self.wifi_menu.close()
                elif self.wifi_menu:
                    self.wifi_menu.open()
            if self.bt_rect and self.bt_rect.collidepoint(event.pos):
                if self.bt_menu and self.bt_menu.active:
                    self.bt_menu.close()
                elif self.bt_menu:
                    self.bt_menu.open()

    def draw(self, surface):
        w = config.screen.width
        h = self.h
        pygame.draw.rect(surface, self.bg, (0, 0, w, h))

        # Left icons
        x = config.topbar.padding_left
        for ico in self.left_icons:
            y = (h - ico.get_height()) // 2
            surface.blit(ico, (x, y))
            x += ico.get_width() + config.topbar.icon_spacing

        # Clock
        clock_surf = None
        if config.topbar.show_clock:
            now = datetime.now().strftime(config.topbar.clock_format)
            clock_surf = self.font.render(now, True, self.fg)
            cx = (w - clock_surf.get_width()) // 2
            cy = (h - clock_surf.get_height()) // 2
            surface.blit(clock_surf, (cx, cy))

        # Notifications
        if config.topbar.show_notifications and clock_surf:
            dot_x = cx + clock_surf.get_width() + config.topbar.notification_spacing * 2
            dot_y = h // 2
            pygame.draw.circle(surface, tuple(config.topbar.notification_dot), (dot_x, dot_y), 4)

        # Right-side icons: WiFi, Bluetooth, then others
        rx = w - config.topbar.padding_right
        icons = []
        if config.topbar.show_wifi and self.wifi_icons:
            strength = self.wifi_poller.get() if self.wifi_poller else 0
            if strength is None:
                strength = 0
            idx = min(len(self.wifi_icons) - 1, strength * len(self.wifi_icons) // 101)
            icons.append(('wifi', self.wifi_icons[idx]))
        if config.topbar.show_bt and self.bt_icons:
            bt_status = self.bt_poller.get() if self.bt_poller else 0
            bt_status = bt_status or 0  # Make sure it's always 0, 1, or 2
            bt_icon = self.bt_icons[min(bt_status, 2)]
            icons.append(('bt', bt_icon))
        for ico in self.right_icons:
            icons.append(('other', ico))

        for name, ico in icons:
            rx -= config.topbar.icon_spacing
            rx -= ico.get_width()
            y = (h - ico.get_height()) // 2
            surface.blit(ico, (rx, y))
            if name == 'wifi':
                self.wifi_rect = pygame.Rect(rx, y, ico.get_width(), ico.get_height())
            if name == 'bt':
                self.bt_rect = pygame.Rect(rx, y, ico.get_width(), ico.get_height())
