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

class RFMenu:
    ITEMS_PER_TAB = 3

    def __init__(self):
        self.page = 0
        self.selected_idx = 0

        # Get config values safely (works with YAML or old object config)
        self.btn_w = 400
        self.btn_h = 60
        self.spacing = 10
        self.top_offset = 60

        self.screen_width = safe_get(config, "SCREEN_WIDTH", 480)
        self.screen_height = safe_get(config, "SCREEN_HEIGHT", 320)
        self.colors = safe_get(config, "COLORS", safe_get(config, "colors", {}))
        self.radius = safe_get(safe_get(config, "RADIUS", {}), "app_button",
                               safe_get(safe_get(config, "radius", {}), "app_button", 14))
        self.font_name = safe_get(config, "FONT_NAME", safe_get(getattr(config, "font", {}), "name", "Arial"))
        self.font_size = safe_get(config, "FONT_SIZE", 24)
        self.accent = safe_get(config, "ACCENT_COLOR", safe_get(config, "accent_color", (100,150,255)))

        cx = self.screen_width // 2 - self.btn_w // 2
        cy = self.screen_height // 2 - self.btn_h

        # Page 0
        self.types_0 = ["2.4 GHz", "Sub-1 GHz"]
        self.btns_0 = [
            Button(self.types_0[i],
                   (cx, cy + i*(self.btn_h + self.spacing), self.btn_w, self.btn_h),
                   lambda idx=i: self.set_page(idx+1))
            for i in range(2)
        ]

        # Page 1: 2.4 GHz
        self.types_24 = [
            "Continuous Wave (CW)", "Frequency Hopping (FHSS)",
            "Direct Sequence Spread Spectrum (DSSS)", "Orthogonal FDM (OFDM)"
        ]
        self.btns_1 = [Button(t, (0,0,self.btn_w,self.btn_h), lambda t=t: self.on_select(t))
                       for t in self.types_24]
        count1 = math.ceil(len(self.types_24) / self.ITEMS_PER_TAB)
        self.tabmgr_1 = TabManager([f"" for _ in range(count1)])

        # Page 2: Sub-1 GHz
        self.types_sub1 = ["Narrowband", "LoRa", "FSK", "Sigfox"]
        self.btns_2 = [Button(t, (0,0,self.btn_w,self.btn_h), lambda t=t: self.on_select(t))
                       for t in self.types_sub1]
        count2 = math.ceil(len(self.types_sub1) / self.ITEMS_PER_TAB)
        self.tabmgr_2 = TabManager([f"" for _ in range(count2)])

        self.warning = WarningMessage("")

    def set_page(self, idx):
        self.page = idx
        self.selected_idx = 0
        if idx == 1:
            self.tabmgr_1.active = 0
        elif idx == 2:
            self.tabmgr_2.active = 0

    def on_select(self, selection):
        self.warning.text = f"Selected: {selection}"
        self.warning.show()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if self.page == 1:
            self.tabmgr_1.handle_event(event)
        elif self.page == 2:
            self.tabmgr_2.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.page != 0:
                self.set_page(0)
                return
            elif event.key == pygame.K_ESCAPE and self.page == 0:
                pygame.quit()
                sys.exit()
            if event.key in (pygame.K_DOWN, pygame.K_UP):
                btns = self._current_buttons_list()
                max_idx = len(btns) - 1
                step = 1 if event.key == pygame.K_DOWN else -1
                self.selected_idx = (self.selected_idx + step) % (max_idx + 1)
                if self.page == 1:
                    self.tabmgr_1.active = self.selected_idx // self.ITEMS_PER_TAB
                elif self.page == 2:
                    self.tabmgr_2.active = self.selected_idx // self.ITEMS_PER_TAB
                return
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._current_buttons_list()[self.selected_idx].callback()
                return

        for i, btn in enumerate(self._current_buttons_list()):
            btn.handle_event(event)

    def update(self):
        self.warning.update()

    def draw(self, surface):
        colors = self.colors
        background = config.colors.background if isinstance(config.colors, dict) else (0, 0, 0)
        text = config.colors.text if isinstance(config.colors, dict) else (255, 255, 255)
        text_light = config.colors.text_light if isinstance(config.colors, dict) else (200, 200, 200)
        button = config.colors.button if isinstance(config.colors, dict) else (50, 50, 50)
        accent = self.accent
        radius = self.radius

        surface.fill(background)
        height = 60 if self.page == 0 else 35
        title = "Select RF type" if self.page == 0 else "Select Operation"
        font = pygame.font.SysFont(self.font_name, 40)
        txt = font.render(title, True, text)
        surface.blit(txt, txt.get_rect(center=(self.screen_width//2, height)))

        if self.page == 0:
            for idx, btn in enumerate(self.btns_0):
                btn.rect.x = self.screen_width//2 - self.btn_w//2
                btn.rect.y = self.screen_height//2 - self.btn_h + idx*(self.btn_h+self.spacing)
                pygame.draw.rect(surface, button, btn.rect, border_radius=radius)
                lbl = pygame.font.SysFont(self.font_name, 30).render(btn.text, True, text_light)
                surface.blit(lbl, lbl.get_rect(center=btn.rect.center))
                if idx == self.selected_idx:
                    pygame.draw.rect(surface, accent, btn.rect.inflate(6,6), width=4, border_radius=radius)
        else:
            if self.page == 1:
                btns_all, tabmgr = self.btns_1, self.tabmgr_1
            else:
                btns_all, tabmgr = self.btns_2, self.tabmgr_2
            active_tab = tabmgr.active
            start = active_tab * self.ITEMS_PER_TAB
            end = start + self.ITEMS_PER_TAB
            for idx, btn in enumerate(btns_all[start:end]):
                btn.rect.x = self.screen_width//2 - self.btn_w//2
                btn.rect.y = self.top_offset + idx*(self.btn_h+self.spacing)
                pygame.draw.rect(surface, button, btn.rect, border_radius=radius)
                lbl = pygame.font.SysFont(self.font_name, self.font_size).render(btn.text, True, text_light)
                surface.blit(lbl, lbl.get_rect(center=btn.rect.center))
                global_idx = start + idx
                if global_idx == self.selected_idx:
                    pygame.draw.rect(surface, accent, btn.rect.inflate(6,6), width=4, border_radius=radius+4)
            tabmgr.draw(surface)

        self.warning.draw(surface)

    def _current_buttons_list(self):
        if self.page == 0:
            return self.btns_0
        elif self.page == 1:
            return self.btns_1
        return self.btns_2


def main():
    pygame.init()
    screen_width = safe_get(config, "SCREEN_WIDTH", 480)
    screen_height = safe_get(config, "SCREEN_HEIGHT", 320)
    fps = safe_get(config, "FPS", 30)
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("RF Tools Menu")
    clock = pygame.time.Clock()

    menu = RFMenu()
    while True:
        for event in pygame.event.get():
            menu.handle_event(event)
        menu.update()
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(fps)

if __name__ == '__main__':
    main()
