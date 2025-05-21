import pygame
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import config
from music_player.menu import MainMenu
from music_player.song_selector import SongSelector
from music_player.album_selector import AlbumSelector
from music_player.player import PlayerScreen


def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((480, 320), pygame.FULLSCREEN)
    pygame.display.set_caption("Arc Music Player")
    clock = pygame.time.Clock()
    pygame.font.init()

    # Load fonts
    fonts = (
        pygame.font.Font("assets/fonts/Inter/Inter_28pt-SemiBold.ttf", 28),
        pygame.font.Font("assets/fonts/Inter/Inter_24pt-Regular.ttf", 22),
        pygame.font.Font("assets/fonts/Inter/Inter_18pt-Regular.ttf", 16),
    )
    # Define colors
    colors = (
        config.COLORS['background_light'],  # BG
        (240, 240, 240),  # PANEL (unused)
        config.COLORS['text_light'],     # TEXT
        config.ACCENT_COLOR,    # ACCENT
        (200, 200, 200),  # SCROLL
        (200, 200, 200),  # OUTLINE
    )

    # Base directory for media
    base_dir = os.path.abspath('.')

    # State machine
    state = 'MENU'
    menu = MainMenu(fonts, colors, screen)
    songs = SongSelector(config.MUSIC_DIR, fonts, colors, screen)

    # Build simple album grouping (5 songs per album)
    albums_data = []
    for i in range(0, len(songs.tracks), 5):
        albums_data.append({
            'name': f"Album {i//5+1}",
            'songs': songs.tracks[i:i+5]
        })
    album_sel = AlbumSelector(albums_data, fonts, colors, screen)
    player = None

    # Main loop
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle input based on current state
            if state == 'MENU':
                res = menu.handle_event(ev)
                if res == 'Songs':
                    state = 'SONGS'
                elif res == 'Albums':
                    state = 'ALBUMS'
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
                    # You can pass album index or data to SongSelector if needed
                    state = 'SONGS'


            elif state == 'PLAYER' and player:
                res = player.handle_event(ev)
                player.update()  # now valid

        # Update logic
        if state == 'SONGS':
            songs.update()
        elif state == 'ALBUMS':
            album_sel.update()
        elif state == 'PLAYER' and player:
            player.update()

        # Draw current screen
        screen.fill(colors[0])  # clear to background color
        if state == 'MENU':
            menu.draw()
        elif state == 'SONGS':
            songs.draw()
        elif state == 'ALBUMS':
            album_sel.draw()
        elif state == 'PLAYER' and player:
            player.draw()

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
