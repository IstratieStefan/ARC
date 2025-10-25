import pygame
import sys
import os
import json
import subprocess
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from arc.core.config import config
from arc.core.ui_elements import Button, WarningMessage, TabManager

class GameMenu:
    ITEMS_PER_TAB = 3

    def __init__(self, games_file=None):
        if games_file is None:
            games_file = os.path.expanduser(config.game_json)

        print(f"[DEBUG] Loading games from: {games_file}")
        self.games = []
        try:
            with open(games_file, 'r') as f:
                self.games = json.load(f)
            print(f"[DEBUG] Loaded {len(self.games)} games")
        except Exception as e:
            print(f"[ERROR] Failed to load games from {games_file}: {e}")
            self.games = []

        self.selected_idx = 0
        self.btns = [
            Button(
                game.get('name', f'Game {i+1}'),
                (0, 0, 400, 60),
                callback=lambda g=game: self.launch_game(g)
            ) for i, game in enumerate(self.games)
        ]
        print(f"[DEBUG] Created {len(self.btns)} buttons")
        tabs = max(1, (len(self.btns) + self.ITEMS_PER_TAB - 1) // self.ITEMS_PER_TAB)
        self.tabmgr = TabManager(["" for _ in range(tabs)])
        self.warning = WarningMessage("")

    def launch_game(self, game):
        name = game.get('name', 'Game')
        cmd_str = game.get('command', '')
        self.warning.text = f"Launching: {name}"
        self.warning.show()
        if not cmd_str:
            self.warning.text = f"Error: Command missing for {name}"
            self.warning.show()
            return
        try:
            cmd = cmd_str if isinstance(cmd_str, list) else cmd_str.split()
            subprocess.Popen(cmd)
        except Exception as e:
            self.warning.text = f"Error: {e}"
            self.warning.show()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        self.tabmgr.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_DOWN, pygame.K_UP):
                step = 1 if event.key == pygame.K_DOWN else -1
                self.selected_idx = (self.selected_idx + step) % max(1, len(self.btns))
                self.tabmgr.active = self.selected_idx // self.ITEMS_PER_TAB
                return
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.btns:
                self.btns[self.selected_idx].callback()
                return
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        for i, btn in enumerate(self.btns):
            btn.handle_event(event)

    def update(self):
        self.warning.update()

    def draw(self, surface):
        width = getattr(getattr(config, 'screen', None), 'width', 480)
        height = getattr(getattr(config, 'screen', None), 'height', 320)
        bg = getattr(getattr(config, 'colors', None), 'background', (30, 30, 30))
        text_color = getattr(getattr(config, 'colors', None), 'text', (255,255,255))
        button_color = getattr(getattr(config, 'colors', None), 'button', (60, 60, 60))
        accent_color = getattr(getattr(config, 'colors', None), 'accent', (100,150,255))
        text_light = getattr(getattr(config, 'colors', None), 'text_light', (200, 200, 200))
        font_name = getattr(getattr(config, 'font', None), 'name', 'Arial')
        radius = getattr(getattr(config, 'radius', None), 'app_button', 14)

        surface.fill(bg)
        font = pygame.font.SysFont(font_name, 40)
        title_surf = font.render("Game Menu", True, text_color)
        surface.blit(title_surf, title_surf.get_rect(center=(width//2, 35)))

        active_tab = getattr(self.tabmgr, "active", 0)
        start = active_tab * self.ITEMS_PER_TAB
        end = start + self.ITEMS_PER_TAB
        for idx, btn in enumerate(self.btns[start:end]):
            global_idx = start + idx
            btn.rect.x = width//2 - btn.rect.width//2
            btn.rect.y = 70 + idx * (btn.rect.height + 10)
            pygame.draw.rect(surface, button_color, btn.rect, border_radius=radius)
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
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
    pygame.display.set_caption("Game Menu")
    clock = pygame.time.Clock()
    menu = GameMenu()
    while True:
        for event in pygame.event.get():
            menu.handle_event(event)
        menu.update()
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    main()
