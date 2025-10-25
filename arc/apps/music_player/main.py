import pygame
import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from arc.core.config import config
from arc.apps.music_player.menu import MainMenu
from arc.apps.music_player.song_selector import SongSelector, scan_music_dir
from arc.apps.music_player.album_selector import AlbumSelector
from arc.apps.music_player.player import PlayerScreen
from arc.apps.music_player.artist_selector import ArtistSelector

def main():
    # ---- Init Pygame and Config ----
    pygame.init()
    screen_width = getattr(getattr(config, "screen", None), "width", 480)
    screen_height = getattr(getattr(config, "screen", None), "height", 320)
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Arc Music Player")
    clock = pygame.time.Clock()
    pygame.font.init()

    # ---- Fonts (get path from config if available) ----
    font_paths = getattr(getattr(config, "font", None), "paths", None) or {}
    fonts = (
        pygame.font.Font(font_paths.get("semibold", "assets/fonts/Inter/Inter_28pt-SemiBold.ttf"), 28),
        pygame.font.Font(font_paths.get("regular", "assets/fonts/Inter/Inter_24pt-Regular.ttf"), 22),
        pygame.font.Font(font_paths.get("small", "assets/fonts/Inter/Inter_18pt-Regular.ttf"), 16),
    )

    # ---- Colors from config ----
    colors = (
        getattr(getattr(config, "colors", None), "background_light", (28, 32, 40)),  # BG
        (240, 240, 240),  # PANEL (unused)
        getattr(getattr(config, "colors", None), "text_light", (210, 210, 210)),    # TEXT
        getattr(config, "accent_color", (100, 150, 255)),                          # ACCENT
        (200, 200, 200),  # SCROLL
        (200, 200, 200),  # OUTLINE
    )

    # ---- Music directory ----
    music_dir = getattr(config, "music_dir", "./Music")

    # ---- State Machine Setup ----
    state = 'MENU'
    menu = MainMenu(fonts, colors, screen)
    all_tracks = scan_music_dir(music_dir)
    songs = SongSelector(None, fonts, colors, screen, tracks=all_tracks)
    album_sel = AlbumSelector(all_tracks, fonts, colors, screen)
    artist_sel = ArtistSelector(all_tracks, fonts, colors, screen)

    player = None
    album_songs_selector = None

    # ---- Main Loop ----
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                if state == "MENU":
                    pygame.quit()
                    sys.exit()
                if state in ("PLAYER", "SONGS", "ALBUMS", "ALBUM_SONGS", "ARTISTS"):
                    state = "MENU"

            # State handling
            if state == 'MENU':
                res = menu.handle_event(ev)
                if res == 'Songs':
                    state = 'SONGS'
                elif res == 'Albums':
                    state = 'ALBUMS'
                elif res == 'Artists':
                    state = 'ARTISTS'
                elif res == 'Now Playing' and player:
                    state = 'PLAYER'
            elif state == 'SONGS':
                res = songs.handle_event(ev)
                if res == 'BACK':
                    state = 'MENU'
                elif isinstance(res, tuple) and res[0] == 'PLAY_SONG':
                    idx = res[1]
                    player = PlayerScreen(songs.tracks, idx, fonts, colors, screen)
                    state = 'PLAYER'
            elif state == 'ALBUMS':
                res = album_sel.handle_event(ev)
                if res == 'BACK':
                    state = 'MENU'
                elif isinstance(res, tuple) and res[0] == 'SELECT_ALBUM':
                    album_tracks = res[1]
                    songs = SongSelector(None, fonts, colors, screen, tracks=album_tracks)
                    state = 'SONGS'
            elif state == 'ARTISTS':
                res = artist_sel.handle_event(ev)
                if res == 'BACK':
                    state = 'MENU'
                elif isinstance(res, tuple) and res[0] == 'SELECT_ARTIST':
                    artist_tracks = res[1]
                    songs = SongSelector(None, fonts, colors, screen, tracks=artist_tracks)
                    state = 'SONGS'
            elif state == 'PLAYER' and player:
                res = player.handle_event(ev)
                if res == 'BACK':
                    state = 'MENU'
                player.update()

        # Update Logic
        if state == 'SONGS':
            songs.update()
        elif state == 'ALBUMS':
            album_sel.update()
        elif state == 'ARTISTS':
            artist_sel.update()
        elif state == 'PLAYER' and player:
            player.update()

        # Draw
        screen.fill(colors[0])
        if state == 'MENU':
            menu.draw()
        elif state == 'SONGS':
            songs.draw()
        elif state == 'ALBUMS':
            album_sel.draw()
        elif state == 'ALBUM_SONGS' and album_songs_selector:
            album_songs_selector.draw()
        elif state == 'ARTISTS':
            artist_sel.draw()
        elif state == 'PLAYER' and player:
            player.draw()

        pygame.display.flip()
        clock.tick(20)

if __name__ == '__main__':
    main()
