import pygame
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
from arc.core.config import config
from arc.core.ui_elements import Button, WarningMessage, TabManager

def safe_get(obj, key, default=None):
    """Safely get attribute or dict key from config, falling back as needed."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

class Settings:
    ITEMS_PER_TAB = 3

    def __init__(self):
        self.selected_idx = 0

        # Safe config reads for all UI parameters
        self.colors = safe_get(config, "COLORS", safe_get(config, "colors", {}))
        self.radius = safe_get(safe_get(config, "RADIUS", {}), "app_button",
                               safe_get(safe_get(config, "radius", {}), "app_button", 14))
        self.screen_width = safe_get(config, "SCREEN_WIDTH", 480)
        self.screen_height = safe_get(config, "SCREEN_HEIGHT", 320)
        self.font_name = safe_get(config, "FONT_NAME", safe_get(getattr(config, "font", {}), "name", "Arial"))
        self.font_size = safe_get(config, "FONT_SIZE", 24)
        self.fps = safe_get(config, "FPS", 30)
        self.accent = safe_get(config, "ACCENT_COLOR", safe_get(config, "accent", (100, 150, 255)))

        # Categories
        self.types_settings = [
            "Audio",
            "Customization",
            "Paths",
            "Other",
            "Information"
        ]
        self.btns = [
            Button(t, (0, 0, 400, 60), lambda t=t: self.on_select(t))
            for t in self.types_settings
        ]
        tabs = math.ceil(len(self.types_settings) / self.ITEMS_PER_TAB)
        self.tabmgr = TabManager(["" for _ in range(tabs)])
        self.warning = WarningMessage("")

    def on_select(self, selection):
        self.warning.text = f"Selected Settings category: {selection}"
        self.warning.show()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        self.tabmgr.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_DOWN, pygame.K_UP):
                step = 1 if event.key == pygame.K_DOWN else -1
                self.selected_idx = (self.selected_idx + step) % len(self.btns)
                self.tabmgr.active = self.selected_idx // self.ITEMS_PER_TAB
                return
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.btns[self.selected_idx].callback()
                return
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        for i, btn in enumerate(self.btns):
            btn.handle_event(event)
            if getattr(btn, "hovered", False):
                self.selected_idx = i
                self.tabmgr.active = i // self.ITEMS_PER_TAB

    def update(self):
        self.warning.update()

    def draw(self, surface):
        bg = safe_get(self.colors, 'background', (36, 42, 48))
        text = safe_get(self.colors, 'text', (255,255,255))
        text_light = safe_get(self.colors, 'text_light', (240,240,240))
        button = safe_get(self.colors, 'button', (60,60,60))
        accent = self.accent
        radius = self.radius

        surface.fill(bg)
        # Title
        font = pygame.font.SysFont(self.font_name, 40)
        title_surf = font.render("Settings", True, text)
        surface.blit(title_surf, title_surf.get_rect(center=(self.screen_width//2, 35)))

        # Draw current tab's buttons
        active_tab = self.tabmgr.active
        start = active_tab * self.ITEMS_PER_TAB
        end = start + self.ITEMS_PER_TAB
        for idx, btn in enumerate(self.btns[start:end]):
            global_idx = start + idx
            btn.rect.x = self.screen_width//2 - btn.rect.width//2
            btn.rect.y = 70 + idx * (btn.rect.height + 10)
            pygame.draw.rect(surface, button, btn.rect, border_radius=radius)
            lbl_font = pygame.font.SysFont(self.font_name, 30)
            lbl_surf = lbl_font.render(btn.text, True, text_light)
            surface.blit(lbl_surf, lbl_surf.get_rect(center=btn.rect.center))
            if global_idx == self.selected_idx:
                pygame.draw.rect(surface, config.accent_color, btn.rect.inflate(6, 6), width=4, border_radius=radius + 4)

        self.tabmgr.draw(surface)
        self.warning.draw(surface)

def main():
    pygame.init()
    screen_width = safe_get(config, "SCREEN_WIDTH", 480)
    screen_height = safe_get(config, "SCREEN_HEIGHT", 320)
    fps = safe_get(config, "FPS", 30)
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Settings")
    clock = pygame.time.Clock()

    menu = Settings()
    while True:
        for event in pygame.event.get():
            menu.handle_event(event)
        menu.update()
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(fps)

if __name__ == '__main__':
    main()