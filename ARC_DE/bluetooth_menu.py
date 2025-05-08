import pygame
import sys
import threading
import subprocess
import time
import config
from ui_elements import ScrollableList

SCREEN_WIDTH  = config.SCREEN_WIDTH
SCREEN_HEIGHT = config.SCREEN_HEIGHT
BG_COLOR      = config.COLORS['background']
TEXT_COLOR    = config.COLORS['text']
HIGHLIGHT     = config.COLORS['indicator_active']
FONT_NAME     = config.FONT_NAME
FONT_SIZE     = config.FONT_SIZE
LINE_HEIGHT   = FONT_SIZE + 4
FPS           = config.FPS
SCAN_DURATION = getattr(config, 'SCAN_DURATION', 8)  # seconds to scan


def scan_bt(devices, device_list, done_flag):
    try:
        # start scanning
        subprocess.run(['bluetoothctl', 'scan', 'on'], check=True, stderr=subprocess.DEVNULL)
        time.sleep(SCAN_DURATION)
        subprocess.run(['bluetoothctl', 'scan', 'off'], check=True, stderr=subprocess.DEVNULL)
        # retrieve discovered devices
        output = subprocess.check_output(['bluetoothctl', 'devices'], stderr=subprocess.DEVNULL)
        text = output.decode('utf-8', errors='ignore')
        found = []
        for line in text.splitlines():
            if not line.startswith('Device '):
                continue
            parts = line.split(maxsplit=2)
            if len(parts) == 3:
                addr = parts[1]
                name = parts[2]
                found.append(f"{name} ({addr})")
        devices[:] = found if found else ['<no devices found>']
    except Exception:
        devices[:] = ['<scan failed>']
    finally:
        done_flag[0] = True
        device_list.items = list(devices)
        device_list.max_offset = max(
            0,
            len(device_list.items) * LINE_HEIGHT - device_list.rect.height
        )

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Bluetooth Devices')
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
    devices = ['<scanning...>']
    scan_done = [False]

    def on_select(item):
        # called when a device is clicked
        addr = item.split()[-1].strip('()')
        print(f'Selected device: {item} → {addr}')
        # TODO: implement connect logic here

    # calculate layout
    inset = 10
    title_height = FONT_SIZE + inset
    list_rect = (
        inset,
        title_height,
        SCREEN_WIDTH - 2 * inset,
        SCREEN_HEIGHT - title_height - inset
    )

    device_list = ScrollableList(
        items=devices,
        rect=list_rect,
        font=font,
        line_height=LINE_HEIGHT,
        text_color=TEXT_COLOR,
        bg_color=config.COLORS.get('cell_bg', (50, 50, 50)),
        sel_color=HIGHLIGHT,
        callback=on_select
    )

    # start the scan in a background thread
    threading.Thread(
        target=scan_bt,
        args=(devices, device_list, scan_done),
        daemon=True
    ).start()

    # main loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            device_list.handle_event(event)

        device_list.update()

        screen.fill(BG_COLOR)

        # draw title
        title_surf = font.render('Select Bluetooth Device', True, TEXT_COLOR)
        screen.blit(
            title_surf,
            ((SCREEN_WIDTH - title_surf.get_width()) // 2, inset // 2)
        )

        # draw list
        device_list.draw(screen)

        # scanning or error hint
        if not scan_done[0]:
            hint = font.render('Scanning for devices...', True, TEXT_COLOR)
            screen.blit(
                hint,
                (
                    (SCREEN_WIDTH - hint.get_width()) // 2,
                    SCREEN_HEIGHT - inset - hint.get_height()
                )
            )

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()
