import pygame
import config
from datetime import datetime


class TopBar:
    def __init__(self):
        self.h      = config.TOPBAR_HEIGHT
        self.bg     = config.TOPBAR_BG
        self.fg     = config.TOPBAR_FG
        self.font   = pygame.font.SysFont('Arial', 18)

        # load left-side icons
        self.left_icons = []
        for path in config.TOPBAR_ICONS:
            try:
                img = pygame.image.load(path).convert_alpha()
                self.left_icons.append(pygame.transform.smoothscale(img, (20,20)))
            except:
                self.left_icons.append(pygame.Surface((20,20), pygame.SRCALPHA))

        # load right-side indicator icons in the order you want them laid out
        self.right_icons = []
        if config.TOPBAR_SHOW_MOBILE:
            self.right_icons.append(self._load_icon(config.TOPBAR_ICON_MOBILE))
        if config.TOPBAR_SHOW_WIFI:
            self.right_icons.append(self._load_icon(config.TOPBAR_ICON_WIFI))
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

    def draw(self, surface):
        w = config.SCREEN_WIDTH
        h = self.h

        # background
        pygame.draw.rect(surface, self.bg, (0, 0, w, h))

        # left icons
        x = config.TOPBAR_PADDING_LEFT
        for ico in self.left_icons:
            y = (h - ico.get_height()) // 2
            surface.blit(ico, (x, y))
            x += ico.get_width() + config.TOPBAR_ICON_SPACING

        # centered clock
        clock_surf = None
        if config.TOPBAR_SHOW_CLOCK:
            now = datetime.now().strftime(config.TOPBAR_CLOCK_FORMAT)
            clock_surf = self.font.render(now, True, self.fg)
            cx = (w - clock_surf.get_width()) // 2
            cy = (h - clock_surf.get_height()) // 2
            surface.blit(clock_surf, (cx, cy))

        # notification dot (to the right of the clock)
        if config.TOPBAR_SHOW_NOTIFICATIONS and clock_surf:
            dot_x = cx + clock_surf.get_width() + config.TOPBAR_NOTIFICATION_SPACING + 5
            dot_y = h // 2
            pygame.draw.circle(surface, config.NOTIFICATION_DOT, (dot_x, dot_y), 4)

        # right-side icons (battery, etc.), flush-right
        rx = w - config.TOPBAR_PADDING_RIGHT
        # iterate reversed so the last in self.right_icons ends up at the far right
        for ico in reversed(self.right_icons):
            rx -= ico.get_width()
            y = (h - ico.get_height()) // 2
            surface.blit(ico, (rx, y))
            rx -= config.TOPBAR_ICON_SPACING
