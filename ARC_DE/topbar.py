import pygame
import config
import subprocess
from datetime import datetime
from wifi_menu import WifiMenu

class TopBar:
    def __init__(self, wifi_callback=None):
        # Dimensions and colors
        self.h             = config.TOPBAR_HEIGHT
        self.bg            = config.TOPBAR_BG
        self.fg            = config.TOPBAR_FG
        self.font          = pygame.font.SysFont('Arial', 18)
        self.wifi_callback = wifi_callback

        # Load left-side icons
        self.left_icons = []
        for path in config.TOPBAR_ICONS:
            try:
                img = pygame.image.load(path).convert_alpha()
                self.left_icons.append(pygame.transform.smoothscale(img, (20,20)))
            except:
                self.left_icons.append(pygame.Surface((20,20), pygame.SRCALPHA))

        # Prepare WiFi strength icons
        self.wifi_icons = []
        for path in config.TOPBAR_WIFI_ICONS:
            try:
                img = pygame.image.load(path).convert_alpha()
                self.wifi_icons.append(pygame.transform.smoothscale(img, (20,20)))
            except:
                self.wifi_icons.append(pygame.Surface((20,20), pygame.SRCALPHA))
        self.wifi_rect = None

        # Load other right-side icons
        self.right_icons = []
        if config.TOPBAR_SHOW_MOBILE:
            self.right_icons.append(self._load_icon(config.TOPBAR_ICON_MOBILE))
        if config.TOPBAR_SHOW_BT:
            self.right_icons.append(self._load_icon(config.TOPBAR_ICON_BT))
        if config.TOPBAR_SHOW_BATTERY:
            self.right_icons.append(self._load_icon(config.TOPBAR_ICON_BATTERY))

    def _load_icon(self, path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, (20,20))
        except:
            return pygame.Surface((20,20), pygame.SRCALPHA)

    def handle_event(self, event):
        # If clicked on WiFi icon, invoke callback
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.wifi_rect and self.wifi_rect.collidepoint(event.pos):
                if self.wifi_callback:
                    self.wifi_callback()

    def get_wifi_strength(self):
        # Return signal percent or None
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

    def draw(self, surface):
        w = config.SCREEN_WIDTH
        h = self.h
        # Draw background
        pygame.draw.rect(surface, self.bg, (0,0,w,h))

        # Draw left icons
        x = config.TOPBAR_PADDING_LEFT
        for ico in self.left_icons:
            y = (h - ico.get_height())//2
            surface.blit(ico, (x,y))
            x += ico.get_width() + config.TOPBAR_ICON_SPACING

        # Draw clock
        clock_surf = None
        if config.TOPBAR_SHOW_CLOCK:
            now = datetime.now().strftime(config.TOPBAR_CLOCK_FORMAT)
            clock_surf = self.font.render(now, True, self.fg)
            cx = (w - clock_surf.get_width())//2
            cy = (h - clock_surf.get_height())//2
            surface.blit(clock_surf, (cx,cy))

        # Notifications dot
        if config.TOPBAR_SHOW_NOTIFICATIONS and clock_surf:
            dot_x = cx + clock_surf.get_width() + config.TOPBAR_NOTIFICATION_SPACING * 2
            dot_y = h//2
            pygame.draw.circle(surface, config.NOTIFICATION_DOT, (dot_x,dot_y), 4)

        # Draw right-side icons: WiFi then others with consistent spacing
        rx = w - config.TOPBAR_PADDING_RIGHT
        icons = []
        if config.TOPBAR_SHOW_WIFI and self.wifi_icons:
            strength = self.get_wifi_strength() or 0
            idx = min(len(self.wifi_icons)-1, strength * len(self.wifi_icons) // 101)
            icons.append(('wifi', self.wifi_icons[idx]))
        for ico in self.right_icons:
            icons.append(('other', ico))

        for name, ico in icons:
            rx -= config.TOPBAR_ICON_SPACING
            rx -= ico.get_width()
            y = (h - ico.get_height())//2
            surface.blit(ico, (rx,y))
            if name=='wifi':
                # clickable area
                self.wifi_rect = pygame.Rect(rx, y, ico.get_width(), ico.get_height())
