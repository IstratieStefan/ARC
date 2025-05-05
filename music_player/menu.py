import pygame

class MainMenu:
    OPTIONS = ["Songs", "Albums", "Now Playing"]
    def __init__(self, fonts, colors, screen):
        self.font_item = fonts[1]
        self.C_TEXT, self.C_ACCENT = colors[2], colors[3]
        self.screen = screen
        self.sel = 0

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_DOWN, pygame.K_RIGHT):
                self.sel = (self.sel + 1) % len(self.OPTIONS)
            elif ev.key in (pygame.K_UP, pygame.K_LEFT):
                self.sel = (self.sel - 1) % len(self.OPTIONS)
            elif ev.key == pygame.K_RETURN:
                return self.OPTIONS[self.sel]
        return None

    def draw(self):
        w,h = self.screen.get_size()
        self.screen.fill((255,255,255))
        for i, opt in enumerate(self.OPTIONS):
            txt = self.font_item.render(opt, True, self.C_TEXT)
            x = (w - txt.get_width())//2
            y = int(h*0.3 + i * 40)
            if i == self.sel:
                rect = pygame.Rect(x-10, y-5, txt.get_width()+20, txt.get_height()+10)
                pygame.draw.rect(self.screen, self.C_ACCENT, rect, 3, border_radius=8)
            self.screen.blit(txt, (x,y))
