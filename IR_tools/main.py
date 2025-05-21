import pygame
import sys
import math
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config
from ui_elements import Button, WarningMessage, TabManager

class IRMenu:
    ITEMS_PER_TAB = 3

    def __init__(self):
        # state
        self.selected_idx = 0

        # IR tool operations
        self.types_ir = [
            "Transmit IR",
            "Receive IR",
            "Learn IR Signal",
            "Decode IR Signal",
            "Analyze IR Timing"
        ]
        # buttons
        self.btns = [
            Button(t, (0, 0, 400, 60), lambda t=t: self.on_select(t))
            for t in self.types_ir
        ]
        # subpage manager
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

        # allow clicking on TabManager
        self.tabmgr.handle_event(event)

        if event.type == pygame.KEYDOWN:
            # navigate
            if event.key in (pygame.K_DOWN, pygame.K_UP):
                step = 1 if event.key == pygame.K_DOWN else -1
                self.selected_idx = (self.selected_idx + step) % len(self.btns)
                # update subpage
                self.tabmgr.active = self.selected_idx // self.ITEMS_PER_TAB
                return
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.btns[self.selected_idx].callback()
                return

        # mouse interactions
        for i, btn in enumerate(self.btns):
            btn.handle_event(event)
            if btn.hovered:
                self.selected_idx = i
                self.tabmgr.active = i // self.ITEMS_PER_TAB

    def update(self):
        self.warning.update()

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        # title: white text
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        title_surf = font.render("IR Tools", True, config.COLORS['text'])
        surface.blit(title_surf, title_surf.get_rect(center=(config.SCREEN_WIDTH//2, 35)))

        # draw current page items
        active_tab = self.tabmgr.active
        start = active_tab * self.ITEMS_PER_TAB
        end = start + self.ITEMS_PER_TAB
        for idx, btn in enumerate(self.btns[start:end]):
            global_idx = start + idx
            # position
            btn.rect.x = config.SCREEN_WIDTH//2 - btn.rect.width//2
            btn.rect.y = 70 + idx * (btn.rect.height + 10)
            # background with pill-shaped corners
            pygame.draw.rect(
                surface,
                config.COLORS['button'],
                btn.rect,
                border_radius=config.RADIUS['app_button']
            )
            # button text (larger white)
            lbl_font = pygame.font.SysFont(config.FONT_NAME, 30)
            lbl_surf = lbl_font.render(btn.text, True, config.COLORS['text_light'])
            surface.blit(lbl_surf, lbl_surf.get_rect(center=btn.rect.center))
            # highlight border on selected
            if global_idx == self.selected_idx:
                pygame.draw.rect(
                    surface,
                    config.COLORS['accent'],
                    btn.rect.inflate(6, 6),
                    width=4,
                    border_radius=config.RADIUS['app_button'] + 4
                )

        # draw page indicators
        self.tabmgr.draw(surface)

        # draw warning if any
        self.warning.draw(surface)


def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("IR Tools Menu")
    clock = pygame.time.Clock()

    menu = IRMenu()
    while True:
        for event in pygame.event.get():
            menu.handle_event(event)
        menu.update()
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(config.FPS)

if __name__ == '__main__':
    main()
