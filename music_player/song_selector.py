import pygame, os, math
from mutagen import File
from draw_utils import draw_page_dots

class SongSelector:
    def __init__(self, music_dir, fonts, colors, screen):
        self.screen = screen
        self.font_item = fonts[1]
        self.C_TEXT, self.C_ACCENT, self.C_SCROLL = colors[2], colors[3], colors[4]
        self.ps = 5
        self.sel = 0
        self.page = 0
        self.tracks = []
        for fn in sorted(os.listdir(music_dir)):
            if fn.lower().endswith('.mp3'):
                path = os.path.join(music_dir, fn)
                try:
                    length = File(path).info.length
                except:
                    length = 0
                self.tracks.append({
                    'title': os.path.splitext(fn)[0],
                    'length': length,
                    'file': path
                })

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            total_pages = math.ceil(len(self.tracks) / self.ps)
            if ev.key in (pygame.K_DOWN, pygame.K_RIGHT):
                if self.sel < min(self.ps-1, len(self.tracks)-1-self.page*self.ps):
                    self.sel += 1
                elif self.page < total_pages-1:
                    self.page += 1
                    self.sel = 0
            elif ev.key in (pygame.K_UP, pygame.K_LEFT):
                if self.sel > 0:
                    self.sel -= 1
                elif self.page > 0:
                    self.page -= 1
                    self.sel = min(self.ps-1, len(self.tracks)-1-self.page*self.ps)
            elif ev.key == pygame.K_RETURN:
                idx = self.page*self.ps + self.sel
                return ('PLAY_SONG', idx)
            elif ev.key == pygame.K_ESCAPE:
                return 'BACK'
        return None

    def draw(self):
        w,h = self.screen.get_size()
        self.screen.fill((255,255,255))
        bx,by,btn_h,sp = 48, 64, 32, 48
        subset = self.tracks[self.page*self.ps:(self.page+1)*self.ps]
        for i, tk in enumerate(subset):
            y = by + i*sp
            rect = pygame.Rect(bx, y, 384, btn_h)
            if i == self.sel:
                pygame.draw.rect(self.screen, self.C_ACCENT, rect, 3, border_radius=8)
            txt = self.font_item.render(tk['title'], True, self.C_TEXT)
            self.screen.blit(txt, (bx+8, y+(btn_h-txt.get_height())//2))
        total_pages = math.ceil(len(self.tracks)/self.ps)
        draw_page_dots(
            self.screen,
            pygame.Rect(bx, by, 384, btn_h*self.ps + sp*(self.ps-1)),
            self.page, total_pages,
            self.C_ACCENT, self.C_SCROLL
        )
