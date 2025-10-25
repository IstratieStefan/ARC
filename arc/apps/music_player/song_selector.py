import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pygame
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from arc.core.ui_elements import ScrollableList

def scan_music_dir(music_dir):
    """Scans a directory for MP3s, returning a list of dicts with all tags."""
    tracks = []
    for fn in sorted(os.listdir(music_dir)):
        if fn.lower().endswith('.mp3'):
            path = os.path.join(music_dir, fn)
            try:
                audio = MP3(path, ID3=EasyID3)
                duration = audio.info.length
                title = audio.get('title', [os.path.splitext(fn)[0]])[0]
                album = audio.get('album', ['Unknown'])[0]
                artist = audio.get('artist', ['Unknown'])[0]
            except Exception:
                duration = 0
                title = os.path.splitext(fn)[0]
                album = 'Unknown'
                artist = 'Unknown'
            tracks.append({
                'title': title,
                'file': path,
                'length': duration,
                'album': album,
                'artist': artist
            })
    return tracks

class SongSelector:
    def __init__(self, music_dir, fonts, colors, screen,
                 rect=(16, 16, 448, 288), line_height=40, tracks=None):
        """
        If tracks is provided, uses those, else scans music_dir.
        Each track must be a dict with 'title', 'file', 'length', 'album', 'artist'.
        """
        self.screen = screen
        self.font = fonts[1]
        self.text_color = colors[2]
        self.sel_color = colors[3]
        self.bg_color = colors[4]

        # Store layout
        self.rect = pygame.Rect(rect)
        self.line_height = line_height

        # Always get tracks as list-of-dicts with full metadata
        if tracks is not None:
            self.tracks = tracks
        else:
            self.tracks = scan_music_dir(music_dir)

        # Prepare display strings (only titles; durations drawn manually)
        self.items = [t['title'] for t in self.tracks]

        # Create scrollable list
        self.list = ScrollableList(
            items=self.items,
            rect=rect,
            font=self.font,
            line_height=self.line_height,
            text_color=self.text_color,
            bg_color=self.bg_color,
            sel_color=self.sel_color,
            callback=self.on_select
        )
        self.selected_index = None

    def on_select(self, item):
        idx = self.list.items.index(item)
        self.selected_index = idx

    def handle_event(self, ev):
        self.list.handle_event(ev)
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_DOWN, pygame.K_UP):
                self.selected_index = self.list.selected_index
            elif ev.key == pygame.K_RETURN and self.selected_index is not None:
                return ('PLAY_SONG', self.selected_index)
            elif ev.key == pygame.K_ESCAPE:
                return 'BACK'
        return None

    def update(self):
        self.list.update()
        if self.selected_index is not None:
            self.list.selected_index = self.selected_index
            self.list._ensure_visible()

    def draw(self):
        surf = self.screen
        x, y0, w, h = self.rect
        old_clip = surf.get_clip()
        surf.set_clip(self.rect)

        for i, track in enumerate(self.tracks):
            y = y0 + i * self.line_height - self.list.offset_y
            if y + self.line_height < y0 or y > y0 + h:
                continue
            # Selected highlight (background)
            if self.selected_index == i:
                pygame.draw.rect(surf, self.sel_color, (x, y, w, self.line_height), 2, border_radius=4)
            # Hover highlight (border)
            elif self.list.enabled and self.list.hover_index == i:
                pygame.draw.rect(surf, self.sel_color, (x, y, w, self.line_height), border_radius=4)

            # Duration text (fixed right)
            dur = track['length']
            m, s = divmod(int(dur), 60)
            dur_s = f"{m:02d}:{s:02d}"
            dur_surf = self.font.render(dur_s, True, self.text_color)
            dw, dh = dur_surf.get_size()
            surf.blit(dur_surf, (x + w - dw - 5, y + (self.line_height - dh) // 2))

            # Title text with horizontal scroll, clipped before duration area
            title = track['title']
            title_surf = self.font.render(title, True, self.text_color)
            max_title_w = w - dw - 15
            surf.set_clip(pygame.Rect(x + 5, y, max_title_w, self.line_height))
            if title_surf.get_width() > max_title_w:
                offset_x = -(pygame.time.get_ticks() // 150 % (title_surf.get_width() + 20))
            else:
                offset_x = 0
            surf.blit(title_surf, (x + 5 + offset_x, y + (self.line_height - title_surf.get_height()) // 2))
            surf.set_clip(self.rect)

        surf.set_clip(old_clip)
