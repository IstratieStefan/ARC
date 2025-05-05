import pygame, sys, os, math
from menu import MainMenu
from song_selector import SongSelector
from album_selector import AlbumSelector
from player import PlayerScreen
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((480,320))
    clock  = pygame.time.Clock()
    pygame.font.init()

    fonts = (
        pygame.font.Font("assets/fonts/Inter/Inter_28pt-SemiBold.ttf", 28),
        pygame.font.Font("assets/fonts/Inter/Inter_24pt-Regular.ttf", 22),
        pygame.font.Font("assets/fonts/Inter/Inter_18pt-Regular.ttf", 16),
    )
    colors = (
        (255,255,255),  # BG
        (240,240,240),  # PANEL unused
        (30,30,30),     # TEXT
        (5,148,250),    # ACCENT
        (200,200,200),  # SCROLL
        (200,200,200)   # OUTLINE
    )

    base_dir = '.'
    state = 'MENU'
    menu     = MainMenu(fonts, colors, screen)
    songs    = SongSelector(base_dir, fonts, colors, screen)
    albums   = []
    # Example grouping: 5 songs per album
    for i in range(0, len(songs.tracks), 5):
        albums.append({'name': f"Album {i//5+1}", 'songs': songs.tracks[i:i+5]})
    album_sel = AlbumSelector(albums, fonts, colors, screen)
    player    = None

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

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
                    state = 'SONGS'

            elif state == 'PLAYER':
                res = player.handle_event(ev)
                if res == 'BACK':
                    state = 'MENU'

        # Draw
        if state == 'MENU':
            menu.draw()
        elif state == 'SONGS':
            songs.draw()
        elif state == 'ALBUMS':
            album_sel.draw()
        elif state == 'PLAYER':
            player.draw()

        pygame.display.flip()
        clock.tick(60)
