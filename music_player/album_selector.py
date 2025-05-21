import pygame
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class AlbumSelector:
    def __init__(self, albums, fonts, colors, screen):
        self.albums = albums
        self.screen = screen
        self.font_item = fonts[1]
        self.C_TEXT, self.C_ACCENT = colors[2], colors[3]
        self.sel = 0

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_DOWN, pygame.K_RIGHT):
                self.sel = (self.sel + 1) % len(self.albums)
            elif ev.key in (pygame.K_UP, pygame.K_LEFT):
                self.sel = (self.sel - 1) % len(self.albums)
            elif ev.key == pygame.K_RETURN:
                return ('SELECT_ALBUM', self.sel)
            elif ev.key == pygame.K_ESCAPE:
                return 'BACK'
        return None

    def draw(self):
        self.screen.fill((255,255,255))
        w,h = self.screen.get_size()
        for i, alb in enumerate(self.albums):
            txt = self.font_item.render(alb['name'], True, self.C_TEXT)
            x = (w - txt.get_width())//2
            y = 80 + i*40
            if i == self.sel:
                rect = pygame.Rect(x-10, y-5, txt.get_width()+20, txt.get_height()+10)
                pygame.draw.rect(self.screen, self.C_ACCENT, rect, 3, border_radius=8)
            self.screen.blit(txt, (x, y))
