# player.py

import pygame
import math
import io
import time
from mutagen.id3 import ID3
from draw_utils import draw_page_dots

def wrap_text(text, font, max_width):
    # (unused now for title/artist; left for reference)
    words, lines, current = text.split(), [], ""
    for w in words:
        test = f"{current} {w}".strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            lines.append(current); current = w
    if current: lines.append(current)
    return lines

class PlayerScreen:
    ICON_SIZE = 36
    SCROLL_SPEED = 50  # pixels per second
    SCROLL_PAUSE = 1.0  # seconds to pause at each end

    def __init__(self, tracks, current_idx, fonts, colors, screen):
        self.tracks     = tracks
        self.screen     = screen
        self.font_title = fonts[0]
        self.font_item  = fonts[1]
        self.font_small = fonts[2]
        self.C_BG, self.C_TEXT, self.C_ACCENT = colors[0], colors[2], colors[3]

        # Controls
        base = "assets/fonts/controlls/"
        self.ic_prev  = pygame.transform.smoothscale(pygame.image.load(base+"previous.png"), (self.ICON_SIZE, self.ICON_SIZE))
        self.ic_play  = pygame.transform.smoothscale(pygame.image.load(base+"play.png"),     (self.ICON_SIZE, self.ICON_SIZE))
        self.ic_pause = pygame.transform.smoothscale(pygame.image.load(base+"pause.png"),    (self.ICON_SIZE, self.ICON_SIZE))
        self.ic_next  = pygame.transform.smoothscale(pygame.image.load(base+"next.png"),     (self.ICON_SIZE, self.ICON_SIZE))

        # Scroll state
        self.title_offset = 0.0
        self.artist_offset = 0.0
        self.scroll_direction = 1
        self.last_scroll_time = time.time()
        self.scroll_paused_until = 0

        # Playback state
        self.playing = False
        self.art     = None
        self.artist  = None

        self.load_track(current_idx)

    def load_track(self, idx):
        self.current = idx
        path = self.tracks[idx]['file']
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            self.playing = True
        except:
            self.playing = False

        # extract art + artist
        self.art = None
        self.artist = None
        try:
            id3 = ID3(path)
            for tag in id3.getall("APIC"):
                img = pygame.image.load(io.BytesIO(tag.data))
                self.art = img; break
            if 'TPE1' in id3:
                self.artist = id3['TPE1'].text[0]
        except:
            pass

        # reset scrolling
        self.title_offset = 0.0
        self.artist_offset = 0.0
        self.scroll_direction = 1
        self.last_scroll_time = time.time()
        self.scroll_paused_until = 0

    def prev_track(self):
        self.load_track((self.current - 1) % len(self.tracks))

    def next_track(self):
        self.load_track((self.current + 1) % len(self.tracks))

    def toggle_play(self):
        if self.playing: pygame.mixer.music.pause()
        else:             pygame.mixer.music.unpause()
        self.playing = not self.playing

    def handle_event(self, ev):
        # keyboard
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_SPACE, pygame.K_RETURN): self.toggle_play()
            elif ev.key == pygame.K_LEFT: self.prev_track()
            elif ev.key == pygame.K_RIGHT: self.next_track()
            elif ev.key == pygame.K_ESCAPE: return 'BACK'
        # touch/mouse
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            x,y = ev.pos; w,h = self.screen.get_size()
            art_r = pygame.Rect(48,64,192,192)
            gap, total_w = 20, 3*self.ICON_SIZE+40
            start_x = art_r.right + ((w-art_r.right)-total_w)//2

            # figure y for controls by measuring title+artist heights
            title_w = w - art_r.right - 20
            title_surf = self.font_title.render(self.tracks[self.current]['title'], True, self.C_TEXT)
            artist_surf = self.font_item.render(self.artist or "", True, self.C_TEXT)
            # assume text is a single line; scroll if too long
            text_block_h = self.font_title.get_height() + (self.font_item.get_height() if self.artist else 0) + 8
            cy = art_r.bottom + 10 + text_block_h + self.ICON_SIZE//2

            prev_r = pygame.Rect(start_x, cy-self.ICON_SIZE//2, self.ICON_SIZE, self.ICON_SIZE)
            play_r = pygame.Rect(start_x+self.ICON_SIZE+gap, cy-self.ICON_SIZE//2, self.ICON_SIZE, self.ICON_SIZE)
            next_r = pygame.Rect(start_x+2*(self.ICON_SIZE+gap), cy-self.ICON_SIZE//2, self.ICON_SIZE, self.ICON_SIZE)

            if prev_r.collidepoint(x,y): self.prev_track()
            elif play_r.collidepoint(x,y): self.toggle_play()
            elif next_r.collidepoint(x,y): self.next_track()

        return None

    def update_scroll(self):
        now = time.time()
        dt = now - self.last_scroll_time
        self.last_scroll_time = now

        # Title
        w,_ = self.screen.get_size()
        art_r = pygame.Rect(48,64,192,192)
        max_w = w - art_r.right - 20
        title = self.tracks[self.current]['title']
        tw = self.font_title.size(title)[0]
        if tw > max_w:
            if now < self.scroll_paused_until:
                return
            self.title_offset += self.scroll_direction * dt * self.SCROLL_SPEED
            if self.title_offset < -(tw - max_w):
                self.title_offset = -(tw - max_w)
                self.scroll_direction = -self.scroll_direction
                self.scroll_paused_until = now + self.SCROLL_PAUSE
            elif self.title_offset > 0:
                self.title_offset = 0
                self.scroll_direction = -self.scroll_direction
                self.scroll_paused_until = now + self.SCROLL_PAUSE

        # Artist (same logic)
        if self.artist:
            aw = self.font_item.size(self.artist)[0]
            if aw > max_w:
                if now < self.scroll_paused_until:
                    return
                self.artist_offset += self.scroll_direction * dt * self.SCROLL_SPEED
                if self.artist_offset < -(aw - max_w):
                    self.artist_offset = -(aw - max_w)
                    self.scroll_direction = -self.scroll_direction
                    self.scroll_paused_until = now + self.SCROLL_PAUSE
                elif self.artist_offset > 0:
                    self.artist_offset = 0
                    self.scroll_direction = -self.scroll_direction
                    self.scroll_paused_until = now + self.SCROLL_PAUSE

    def draw(self):
        # update scroll before drawing
        self.update_scroll()

        s = self.screen; w,h = s.get_size()
        s.fill(self.C_BG)

        # album art + 2px border
        art_r = pygame.Rect(48,64,192,192)
        if self.art:
            s.blit(pygame.transform.scale(self.art, art_r.size), art_r)
        else:
            pygame.draw.rect(s,(200,200,200),art_r,border_radius=8)
        pygame.draw.rect(s,(0,0,0),art_r,width=2,border_radius=8)

        # title (semi-bold) with offset
        x0 = art_r.right + 20
        y = art_r.y
        title = self.tracks[self.current]['title']
        txt_surf = self.font_title.render(title, True, self.C_TEXT)
        s.set_clip(pygame.Rect(x0, y, w-x0-20, txt_surf.get_height()))
        s.blit(txt_surf, (x0 + self.title_offset, y))
        s.set_clip(None)
        y += txt_surf.get_height() + 2

        # artist with offset
        if self.artist:
            art_surf = self.font_item.render(self.artist, True, self.C_TEXT)
            s.set_clip(pygame.Rect(x0, y, w-x0-20, art_surf.get_height()))
            s.blit(art_surf, (x0 + self.artist_offset, y))
            s.set_clip(None)
            y += art_surf.get_height() + 8
        else:
            y += 8

        # controls
        gap = 20
        total_w = 3*self.ICON_SIZE + 2*gap
        start_x = art_r.right + ((w-art_r.right)-total_w)//2
        cy = y + self.ICON_SIZE//2

        s.blit(self.ic_prev,  (start_x,                    cy-self.ICON_SIZE//2))
        icon = self.ic_pause if self.playing else self.ic_play
        s.blit(icon,           (start_x+self.ICON_SIZE+gap, cy-self.ICON_SIZE//2))
        s.blit(self.ic_next,   (start_x+2*(self.ICON_SIZE+gap), cy-self.ICON_SIZE//2))

        # progress bar
        pos = pygame.mixer.music.get_pos()/1000.0
        ln  = self.tracks[self.current]['length']
        frac= min(pos/ln if ln>0 else 0,1)
        bar = pygame.Rect(48,272,384,8)
        pygame.draw.rect(s,(200,200,200),bar,border_radius=4)
        pygame.draw.rect(s,self.C_ACCENT,(bar.x,bar.y,int(bar.w*frac),bar.h),border_radius=4)

        # time text
        times = f"{int(pos//60)}:{int(pos%60):02d}/{int(ln//60)}:{int(ln%60):02d}"
        s.blit(self.font_small.render(times,True,self.C_TEXT),(48,284))
