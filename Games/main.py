import pygame
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import subprocess
import config
from ui_elements import Button, WarningMessage, TabManager

class GameMenu:
    ITEMS_PER_TAB = 3

    def __init__(self, games_file= config.GAME_JSON):
        # Load games from JSON
        with open(games_file, 'r') as f:
            self.games = json.load(f)

        # state
        self.selected_idx = 0

        # buttons
        self.btns = []
        for game in self.games:
            self.btns.append(
                Button(
                    game['name'],
                    (0, 0, 400, 60),
                    callback=lambda g=game: self.launch_game(g)
                )
            )

        # subpage manager
        tabs = (len(self.btns) + self.ITEMS_PER_TAB - 1) // self.ITEMS_PER_TABx
        self.tabmgr = TabManager(["" for _ in range(tabs)])

        self.warning = WarningMessage("")

    def launch_game(self, game):
        # Show warning then execute
        self.warning.text = f"Launching: {game['name']}"
        self.warning.show()
        try:
            # split command for subprocess
            cmd = game['command'].split()
            subprocess.Popen(cmd)
            pygame.quit()
            sys.exit()
        except Exception as e:
            self.warning.text = f"Error: {e}"
            self.warning.show()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


        # allow clicking on TabManager
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

        # mouse interactions
        for i, btn in enumerate(self.btns):
            btn.handle_event(event)


    def update(self):
        self.warning.update()

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        # title
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        title_surf = font.render("Game Menu", True, config.COLORS['text'])
        surface.blit(
            title_surf,
            title_surf.get_rect(center=(config.SCREEN_WIDTH//2, 35))
        )

        # draw buttons for current tab
        active_tab = self.tabmgr.active
        start = active_tab * self.ITEMS_PER_TAB
        end = start + self.ITEMS_PER_TAB
        for idx, btn in enumerate(self.btns[start:end]):
            global_idx = start + idx
            btn.rect.x = config.SCREEN_WIDTH//2 - btn.rect.width//2
            btn.rect.y = 70 + idx * (btn.rect.height + 10)
            pygame.draw.rect(
                surface,
                config.COLORS['button'],
                btn.rect,
                border_radius=config.RADIUS['app_button']
            )
            lbl_font = pygame.font.SysFont(config.FONT_NAME, 30)
            lbl_surf = lbl_font.render(btn.text, True, config.COLORS['text_light'])
            surface.blit(
                lbl_surf,
                lbl_surf.get_rect(center=btn.rect.center)
            )
            if global_idx == self.selected_idx:
                pygame.draw.rect(
                    surface,
                    config.COLORS['accent'],
                    btn.rect.inflate(6, 6),
                    width=4,
                    border_radius=config.RADIUS['app_button']+4
                )

        # draw page indicators and warnings
        self.tabmgr.draw(surface)
        self.warning.draw(surface)


def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Game Menu")
    clock = pygame.time.Clock()

    menu = GameMenu()
    while True:
        for event in pygame.event.get():
            menu.handle_event(event)
        menu.update()
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(config.FPS)

if __name__ == '__main__':
    main()
