import pygame
import io
from arc.core.config import config
import time
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from mutagen.id3 import ID3

class PlayerScreen:
    ICON_SIZE = 36
    SCROLL_SPEED = 50
    SCROLL_PAUSE = 1.0

    def __init__(self, tracks, current_idx, fonts, colors, screen):
        self.tracks     = tracks
        self.screen     = screen
        self.font_title = fonts[0]
        self.font_item  = fonts[1]
        self.font_small = fonts[2]
        self.C_BG, self.C_TEXT, self.C_ACCENT = colors[0], colors[2], colors[3]

        # Initialize mixer if needed
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Load control icons
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        ASSETS_DIR = os.path.join(BASE_DIR, "controlls")
        self.ic_prev  = self.load_icon(os.path.join(ASSETS_DIR, "previous.png"))
        self.ic_play  = self.load_icon(os.path.join(ASSETS_DIR, "play.png"))
        self.ic_pause = self.load_icon(os.path.join(ASSETS_DIR, "pause.png"))
        self.ic_next  = self.load_icon(os.path.join(ASSETS_DIR, "next.png"))

        # Playback & UI state
        self.title_offset = 0.0
        self.artist_offset = 0.0
        self.scroll_direction = 1
        self.last_scroll_time = time.time()
        self.scroll_paused_until = 0
        self.playing = False
        self.art     = None
        self.artist  = None
        self.album_art_ready = None

        # Track index
        self.current = None
        self.load_track(current_idx)

    def load_icon(self, path):
        try:
            return pygame.transform.smoothscale(
                pygame.image.load(path), (self.ICON_SIZE, self.ICON_SIZE)
            ).convert_alpha()
        except Exception:
            surf = pygame.Surface((self.ICON_SIZE, self.ICON_SIZE), pygame.SRCALPHA)
            surf.fill((255, 0, 0, 160))
            return surf

    def update(self):
        self.update_scroll()

    def load_track(self, idx):
        self.current = idx
        track_info = self.tracks[idx]
        path = track_info['file']
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            self.playing = True
        except Exception as e:
            print(f"Error loading track {path}: {e}")
            self.playing = False

        self.title_offset = 0.0
        self.artist_offset = 0.0
        self.scroll_direction = 1
        self.last_scroll_time = time.time()
        self.scroll_paused_until = 0

        self.art = None
        self.artist = None
        self.album_art_ready = None
        # Extract ID3 tags
        try:
            id3 = ID3(path)
            for tag in id3.getall("APIC"):
                img = pygame.image.load(io.BytesIO(tag.data))
                self.art = img
                break
            if 'TPE1' in id3:
                self.artist = id3['TPE1'].text[0]
        except Exception:
            pass

        # Pre-render album art with rounded corners, only if art exists
        BORDER_RADIUS = 8
        art_size = (192, 192)
        if self.art:
            try:
                img_scaled = pygame.transform.smoothscale(self.art, art_size).convert_alpha()
                mask = pygame.Surface(art_size, pygame.SRCALPHA)
                pygame.draw.rect(mask, (255,255,255,255), mask.get_rect(), border_radius=BORDER_RADIUS)
                img_scaled.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
                self.album_art_ready = img_scaled
            except Exception as e:
                print(f"Failed to render rounded album art: {e}")
                self.album_art_ready = None

    def prev_track(self):
        new_idx = (self.current - 1) % len(self.tracks)
        self.load_track(new_idx)

    def next_track(self):
        new_idx = (self.current + 1) % len(self.tracks)
        self.load_track(new_idx)

    def toggle_play(self):
        if self.playing:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
        self.playing = not self.playing

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.toggle_play()
            elif ev.key == pygame.K_LEFT:
                self.prev_track()
            elif ev.key == pygame.K_RIGHT:
                self.next_track()
            elif ev.key == pygame.K_ESCAPE:
                return 'BACK'
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            x, y = ev.pos
            start_x = 265
            cy = config.screen.height - 130
            prev_r = pygame.Rect(start_x, cy, self.ICON_SIZE, self.ICON_SIZE)
            play_r = pygame.Rect(start_x + self.ICON_SIZE + 20, cy, self.ICON_SIZE, self.ICON_SIZE)
            next_r = pygame.Rect(start_x + 2*(self.ICON_SIZE + 20), cy, self.ICON_SIZE, self.ICON_SIZE)
            if prev_r.collidepoint(x, y):
                self.prev_track()
            elif play_r.collidepoint(x, y):
                self.toggle_play()
            elif next_r.collidepoint(x, y):
                self.next_track()
        return None

    def update_scroll(self):
        now = time.time()
        dt = now - self.last_scroll_time
        self.last_scroll_time = now
        w, _ = self.screen.get_size()
        art_r = pygame.Rect(30, 40, 192, 192)
        max_w = w - art_r.right - 20
        title = self.tracks[self.current]['title']
        tw = self.font_title.size(title)[0]
        if tw > max_w and now >= self.scroll_paused_until:
            self.title_offset += self.scroll_direction * dt * self.SCROLL_SPEED
            if self.title_offset < -(tw - max_w):
                self.title_offset = -(tw - max_w)
                self.scroll_direction *= -1
                self.scroll_paused_until = now + self.SCROLL_PAUSE
            elif self.title_offset > 0:
                self.title_offset = 0
                self.scroll_direction *= -1
                self.scroll_paused_until = now + self.SCROLL_PAUSE
        if self.artist:
            aw = self.font_item.size(self.artist)[0]
            if aw > max_w and now >= self.scroll_paused_until:
                self.artist_offset += self.scroll_direction * dt * self.SCROLL_SPEED
                if self.artist_offset < -(aw - max_w):
                    self.artist_offset = -(aw - max_w)
                    self.scroll_direction *= -1
                    self.scroll_paused_until = now + self.SCROLL_PAUSE
                elif self.artist_offset > 0:
                    self.artist_offset = 0
                    self.scroll_direction *= -1
                    self.scroll_paused_until = now + self.SCROLL_PAUSE

    def draw(self):
        s = self.screen
        w, h = s.get_size()
        s.fill(self.C_BG)
        # Draw album art
        art_r = pygame.Rect(30, 40, 192, 192)
        BORDER_RADIUS = 8
        pygame.draw.rect(s, (200, 200, 200), art_r, border_radius=BORDER_RADIUS)
        if self.album_art_ready:
            s.blit(self.album_art_ready, art_r)
        pygame.draw.rect(s, (10, 10, 10), art_r, width=2, border_radius=BORDER_RADIUS)
        # Draw title
        x0 = art_r.right + 20
        y = art_r.y
        title = self.tracks[self.current]['title']
        title_surf = self.font_title.render(title, True, self.C_TEXT)
        s.set_clip(pygame.Rect(x0, y, w - x0 - 20, title_surf.get_height()))
        s.blit(title_surf, (x0 + self.title_offset, y))
        s.set_clip(None)
        y += title_surf.get_height() + 2
        # Draw artist
        if self.artist:
            art_surf = self.font_item.render(self.artist, True, self.C_TEXT)
            s.set_clip(pygame.Rect(x0, y, w - x0 - 20, art_surf.get_height()))
            s.blit(art_surf, (x0 + self.artist_offset, y))
            s.set_clip(None)
            y += art_surf.get_height() + 8
        else:
            y += 8
        # Draw controls (positioned above progress bar)
        gap = 20
        start_x = 265
        cy = config.screen.height - 130
        s.blit(self.ic_prev, (start_x, cy))
        icon = self.ic_pause if self.playing else self.ic_play
        s.blit(icon, (start_x + self.ICON_SIZE + gap, cy))
        s.blit(self.ic_next, (start_x + 2 * (self.ICON_SIZE + gap), cy))
        # Draw progress bar
        pos = pygame.mixer.music.get_pos() / 1000.0
        try:
            ln = float(self.tracks[self.current].get('length', 0))
        except Exception:
            ln = 0
        frac = min(pos / ln if ln > 0 else 0, 1)
        bar = pygame.Rect(48, 250, 384, 8)
        pygame.draw.rect(s, (200, 200, 200), bar, border_radius=4)
        pygame.draw.rect(s, self.C_ACCENT, (bar.x, bar.y, int(bar.w * frac), bar.h), border_radius=4)
        # Draw time text
        def fmt_time(secs):
            m = int(secs // 60)
            s_ = int(secs % 60)
            return f"{m}:{s_:02d}"
        times = f"{fmt_time(pos)}/{fmt_time(ln)}"
        s.blit(self.font_small.render(times, True, self.C_TEXT), (48, 262))
