import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pygame
from mutagen.mp3 import MP3
from ui_elements import ScrollableList

class SongSelector:
    def __init__(self, music_dir, fonts, colors, screen,
                 rect=(16, 16, 448, 288), line_height=40):
        """
        A scrollable song list UI using ScrollableList with separate title scroll and fixed duration.

        music_dir   – folder containing .mp3 files
        fonts       – tuple of pygame.Fonts; use fonts[1] for list items
        colors      – tuple where colors[2]=text, [3]=accent, [4]=scroll bg
        screen      – pygame display Surface
        rect        – (x,y,width,height) for list area (smaller margins)
        line_height – pixel height per line
        """
        self.screen = screen
        self.font = fonts[1]
        self.text_color = colors[2]
        self.sel_color = colors[3]
        self.bg_color = colors[4]

        # Store layout
        self.rect = pygame.Rect(rect)
        self.line_height = line_height

        # Load track metadata into list of dicts
        self.tracks = []
        for fn in sorted(os.listdir(music_dir)):
            if fn.lower().endswith('.mp3'):
                path = os.path.join(music_dir, fn)
                try:
                    duration = MP3(path).info.length
                except Exception:
                    duration = 0
                title = os.path.splitext(fn)[0]
                self.tracks.append({'title': title, 'file': path, 'length': duration})

        # Prepare display strings (only titles; durations drawn manually)
        items = [t['title'] for t in self.tracks]

        # Create scrollable list
        self.list = ScrollableList(
            items=items,
            rect=rect,
            font=self.font,
            line_height=self.line_height,
            text_color=self.text_color,
            bg_color=self.bg_color,
            sel_color=self.sel_color,
            callback=self.on_select
        )
        # Track selected index for highlighting
        self.selected_index = None

    def on_select(self, item):
        idx = self.list.items.index(item)
        self.selected_index = idx

    def handle_event(self, ev):
        """
        Forward to ScrollableList; allow keyboard navigation, Enter to play, Escape to back.
        """
        # Handle scrolling and clicking
        self.list.handle_event(ev)
        # Keyboard navigation: sync selected_index with list's cursor
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_DOWN, pygame.K_UP):
                self.selected_index = self.list.selected_index
            elif ev.key == pygame.K_RETURN and self.selected_index is not None:
                return ('PLAY_SONG', self.selected_index)
            elif ev.key == pygame.K_ESCAPE:
                return 'BACK'
        return None

    def update(self):
        """Update hover/scroll states."""
        self.list.update()
        # Optionally keep selection within visible range
        if self.selected_index is not None:
            self.list.selected_index = self.selected_index
            self.list._ensure_visible()

    def draw(self):
        surf = self.screen
        x, y0, w, h = self.rect
        # clear background
        surf.fill((255, 255, 255))
        # clip to list area
        old_clip = surf.get_clip()
        surf.set_clip(self.rect)

        # Draw each item
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
            # Set clip for title region
            surf.set_clip(pygame.Rect(x + 5, y, max_title_w, self.line_height))
            if title_surf.get_width() > max_title_w:
                offset_x = -(pygame.time.get_ticks() // 150 % (title_surf.get_width() + 20))
            else:
                offset_x = 0
            surf.blit(title_surf, (x + 5 + offset_x, y + (self.line_height - title_surf.get_height()) // 2))
            # Restore clip for subsequent items
            surf.set_clip(self.rect)

        # restore original clip
        surf.set_clip(old_clip)

