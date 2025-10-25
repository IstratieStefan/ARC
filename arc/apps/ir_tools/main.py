import pygame
import sys
import math
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from arc.core.config import config
from arc.core.ui_elements import Button, WarningMessage, TabManager

class IRMenu:
    ITEMS_PER_TAB = 3

    def __init__(self):
        self.selected_idx = 0

        self.types_ir = [
            "Transmit IR",
            "Receive IR",
            "Learn IR Signal",
            "Decode IR Signal",
            "Analyze IR Timing"
        ]
        self.btns = [
            Button(t, (0, 0, 400, 60), lambda t=t: self.on_select(t))
            for t in self.types_ir
        ]
        tabs = math.ceil(len(self.types_ir) / self.ITEMS_PER_TAB)
        self.tabmgr = TabManager(["" for _ in range(tabs)])
        self.warning = WarningMessage("")

    def on_select(self, selection):
        self.warning.text = f"Selected IR Tool: {selection}"
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
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.btns[self.selected_idx].callback()
                return
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        for i, btn in enumerate(self.btns):
            btn.handle_event(event)
            if getattr(btn, 'hovered', False):
                self.selected_idx = i
                self.tabmgr.active = i // self.ITEMS_PER_TAB

    def update(self):
        self.warning.update()

    def draw(self, surface):
        width = getattr(getattr(config, 'screen', None), 'width', 480)
        height = getattr(getattr(config, 'screen', None), 'height', 320)
        colors = getattr(config, 'colors', None)
        bg_color = getattr(colors, 'background', (30, 30, 30))
        text_color = getattr(colors, 'text', (255, 255, 255))
        accent_color = getattr(colors, 'accent', (100, 150, 255))
        button_color = getattr(colors, 'button', (60, 60, 60))
        text_light = getattr(colors, 'text_light', (200, 200, 200))
        radius = getattr(getattr(config, 'radius', None), 'app_button', 14)
        font_name = getattr(getattr(config, 'font', None), 'name', 'Arial')

        surface.fill(bg_color)
        font = pygame.font.SysFont(font_name, 40)
        title_surf = font.render("IR Tools", True, text_color)
        surface.blit(title_surf, title_surf.get_rect(center=(width // 2, 35)))

        active_tab = getattr(self.tabmgr, "active", 0)
        start = active_tab * self.ITEMS_PER_TAB
        end = start + self.ITEMS_PER_TAB
        for idx, btn in enumerate(self.btns[start:end]):
            global_idx = start + idx
            btn.rect.x = width // 2 - btn.rect.width // 2
            btn.rect.y = 70 + idx * (btn.rect.height + 10)
            pygame.draw.rect(
                surface,
                button_color,
                btn.rect,
                border_radius=radius
            )
            lbl_font = pygame.font.SysFont(font_name, 30)
            lbl_surf = lbl_font.render(btn.text, True, text_light)
            surface.blit(lbl_surf, lbl_surf.get_rect(center=btn.rect.center))
            if global_idx == self.selected_idx:
                pygame.draw.rect(
                    surface,
                    accent_color,
                    btn.rect.inflate(6, 6),
                    width=4,
                    border_radius=radius + 4
                )

        self.tabmgr.draw(surface)
        self.warning.draw(surface)

def main():
    pygame.init()
    width = getattr(getattr(config, 'screen', None), 'width', 480)
    height = getattr(getattr(config, 'screen', None), 'height', 320)
    fps = getattr(config, 'fps', 30)
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
    pygame.display.set_caption("IR Tools Menu")
    clock = pygame.time.Clock()
    menu = IRMenu()
    while True:
        for event in pygame.event.get():
            menu.handle_event(event)
        menu.update()
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    main()
