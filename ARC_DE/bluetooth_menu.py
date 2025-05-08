import pygame
import sys
import threading
import subprocess
import time
import config
from ui_elements import ScrollableList, MessageBox

# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------
SCREEN_WIDTH   = config.SCREEN_WIDTH
SCREEN_HEIGHT  = config.SCREEN_HEIGHT
BG_COLOR       = config.COLORS['background_light']
TEXT_COLOR     = config.COLORS['text_light']
HIGHLIGHT      = config.ACCENT_COLOR
FONT_NAME      = config.FONT_NAME
FONT_SIZE      = config.FONT_SIZE
LINE_HEIGHT    = FONT_SIZE + 10
FPS            = config.FPS
SCAN_INTERVAL  = getattr(config, 'BT_SCAN_INTERVAL', 10)  # seconds

# ------------------------------------------------------------------
# SCAN BLUETOOTH DEVICES (using bluetoothctl)
# ------------------------------------------------------------------
def scan_bt(devices, device_list, done_flag):
    # Ensure adapter is on and agent is ready
    subprocess.run(['bluetoothctl', 'power', 'on'], check=True)
    subprocess.run(['bluetoothctl', 'agent', 'on'], stderr=subprocess.DEVNULL)
    subprocess.run(['bluetoothctl', 'default-agent'], stderr=subprocess.DEVNULL)
    subprocess.run(['bluetoothctl', 'agent', 'NoInputNoOutput'], check=True)
    subprocess.run(['bluetoothctl', 'default-agent'], check=True)
    while not done_flag[0]:
        try:
            # start scan
            res = subprocess.run(['bluetoothctl', 'scan', 'on'],
                                 capture_output=True, text=True)
            if res.returncode != 0:
                print("Error starting scan:", res.stderr)
                raise RuntimeError("scan-on failed")

            time.sleep(SCAN_INTERVAL)

            subprocess.run(['bluetoothctl', 'scan', 'off'], check=True)

            out = subprocess.check_output(['bluetoothctl', 'devices'],
                                          stderr=subprocess.STDOUT,
                                          text=True)
            # parse 'Device AA:BB:CC:DD:EE:FF Name' lines
            found = []
            for line in out.splitlines():
                parts = line.split(None, 2)
                if len(parts) == 3 and parts[0] == 'Device':
                    addr, name = parts[1], parts[2]
                    found.append(f"{name} ({addr})")
            devices[:] = found or ['<no devices found>']

        except Exception as e:
            print("Scan exception:", e)
            devices[:] = ['<scan failed>']

        # refresh UI
        device_list.items      = list(devices)
        device_list.max_offset = max(0,
            len(device_list.items) * LINE_HEIGHT - device_list.rect.height
        )
        done_flag[0] = True
        time.sleep(SCAN_INTERVAL)

# ------------------------------------------------------------------
# MAIN BLUETOOTH MENU
# ------------------------------------------------------------------
def BluetoothMenu():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Bluetooth Devices')
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
    devices = ['<scanning...>']
    scan_done = [False]

    # Create the scrollable list
    inset    = 10
    title_h  = FONT_SIZE + inset
    list_rect = (inset, title_h, SCREEN_WIDTH - 2*inset, SCREEN_HEIGHT - title_h - inset)

    bluetooth_list = ScrollableList(
        items=devices,
        rect=list_rect,
        font=font,
        line_height=LINE_HEIGHT,
        text_color=TEXT_COLOR,
        bg_color=BG_COLOR,
        sel_color=HIGHLIGHT,
        callback=lambda sel: on_connect(sel, bluetooth_list)
    )

    # Background scan thread
    threading.Thread(target=scan_bt, args=(devices, bluetooth_list, scan_done), daemon=True).start()

    def do_connect(addr):
        """
        Pair, trust, and connect to the Bluetooth device at address `addr`.
        """
        try:
            subprocess.run(['bluetoothctl', 'pair', addr], check=True)
            subprocess.run(['bluetoothctl', 'trust', addr], check=True)
            subprocess.run(['bluetoothctl', 'connect', addr], check=True)
            MessageBox(f"Connected to {addr}", lambda: None, lambda: None).show()
        except subprocess.CalledProcessError:
            MessageBox(f"Failed to connect to {addr}", lambda: None, lambda: None).show()
        finally:
            bluetooth_list.set_enabled(True)

    def on_connect(selection, list_widget):
        # Disable list while connecting
        list_widget.set_enabled(False)
        # Extract MAC address from selection "Name (ADDR)"
        addr = selection.split('(')[-1].strip(')')
        do_connect(addr)

    running = True
    while running:
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                running = False
            else:
                bluetooth_list.handle_event(evt)

        bluetooth_list.update()

        # Draw UI
        screen.fill(BG_COLOR)
        title = font.render('Bluetooth Devices', True, TEXT_COLOR)
        screen.blit(title, ((SCREEN_WIDTH - title.get_width())//2, inset//2))

        bluetooth_list.draw(screen)
        if not scan_done[0]:
            hint = font.render('Scanning Bluetooth...', True, TEXT_COLOR)
            screen.blit(hint, ((SCREEN_WIDTH - hint.get_width())//2, SCREEN_HEIGHT - inset - hint.get_height()))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    BluetoothMenu()