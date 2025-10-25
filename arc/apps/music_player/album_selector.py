import pygame
import os
import sys
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from arc.core.ui_elements import ScrollableList
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class AlbumSelector:
    def __init__(self, tracks, fonts, colors, screen,
                 rect=(16, 16, 448, 288), line_height=40):
        """
        Group the provided tracks by album tag and build the scrollable album list.
        tracks    – list of dicts, as loaded by SongSelector
        """
        self.screen = screen
        self.font = fonts[1]
        self.text_color = colors[2]
        self.sel_color = colors[3]
        self.bg_color = colors[4]
        self.rect = pygame.Rect(rect)
        self.line_height = line_height

        self.albums = {}  # album_name -> list of tracks
        for t in tracks:
            album = t.get('album', 'Unknown Album')
            if not album:
                album = "Unknown Album"
            if album not in self.albums:
                self.albums[album] = []
            self.albums[album].append(t)

        self.album_names = sorted(self.albums.keys())
        self.list = ScrollableList(
            items=self.album_names,
            rect=rect,
            font=self.font,
            line_height=self.line_height,
            text_color=self.text_color,
            bg_color=self.bg_color,
            sel_color=self.sel_color,
            callback=self.on_select
        )
        self.selected_index = None

    def on_select(self, album_name):
        idx = self.list.items.index(album_name)
        self.selected_index = idx

    def handle_event(self, ev):
        self.list.handle_event(ev)
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_DOWN, pygame.K_UP):
                self.selected_index = self.list.selected_index
            elif ev.key == pygame.K_RETURN and self.selected_index is not None:
                selected_album = self.album_names[self.selected_index]
                tracks = self.albums[selected_album]
                return ('SELECT_ALBUM', tracks)
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
        surf.fill((255, 255, 255))
        old_clip = surf.get_clip()
        surf.set_clip(self.rect)
        for i, name in enumerate(self.album_names):
            y = y0 + i * self.line_height - self.list.offset_y
            if y + self.line_height < y0 or y > y0 + h:
                continue
            # Selected/hover effect
            if self.selected_index == i:
                pygame.draw.rect(surf, self.sel_color, (x, y, w, self.line_height), 2, border_radius=4)
            elif self.list.enabled and self.list.hover_index == i:
                pygame.draw.rect(surf, self.sel_color, (x, y, w, self.line_height), border_radius=4)
            # Album name
            album_surf = self.font.render(name, True, self.text_color)
            surf.blit(album_surf, (x + 8, y + (self.line_height - album_surf.get_height()) // 2))
            # Number of songs
            num_songs = len(self.albums[name])
            num_surf = self.font.render(str(num_songs), True, self.text_color)
            surf.blit(num_surf, (x + w - 40, y + (self.line_height - num_surf.get_height()) // 2))
        surf.set_clip(old_clip)
