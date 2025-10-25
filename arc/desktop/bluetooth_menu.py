import pygame
import threading
import subprocess
import time
import sys
import os
from arc.core import config, ScrollableList, MessageBox

def safe_color(val, fallback):
    # Accept list/tuple of 3 ints as color
    if isinstance(val, (list, tuple)) and len(val) == 3:
        return tuple(val)
    return fallback

class BluetoothMenu:
    def __init__(self):
        # --- Use YAML-based config everywhere! ---
        self.WIDTH = config.screen.width
        self.HEIGHT = config.screen.height
        self.BG_COLOR = safe_color(getattr(config.colors, "popup_bg", None), (36, 42, 48))
        self.TEXT_COLOR = safe_color(getattr(config.colors, "popup_fg", None), (240, 240, 240))
        self.HIGHLIGHT = safe_color(getattr(config, "accent_color", None), (204, 99, 36))
        self.FONT_NAME = getattr(config.font, "name", None)
        self.FONT_SIZE = 18
        self.LINE_HEIGHT = self.FONT_SIZE + 10
        self.SCAN_INTERVAL = getattr(config, "bt_scan_interval", 8)

        # Surface (should be passed in real use, but this keeps compat for demo)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN)

        self.active = True
        self.rect = pygame.Rect(0, getattr(config.topbar, "height", 30), self.WIDTH, self.HEIGHT - getattr(config.topbar, "height", 30))
        self.font = pygame.font.SysFont(self.FONT_NAME, self.FONT_SIZE)
        self.devices = ['<scanning...>']
        self.scanning = False
        self.selected_addr = None
        self.device_list = ScrollableList(
            items=self.devices,
            rect=(20, 60, self.WIDTH - 40, self.HEIGHT - 110),
            font=self.font,
            line_height=self.LINE_HEIGHT,
            text_color=self.TEXT_COLOR,
            bg_color=self.BG_COLOR,
            sel_color=self.HIGHLIGHT,
            callback=self.on_select_device,
        )
        self._scan_thread = None
        self._stop_scan = threading.Event()
        self.status_msg = ""
        self.last_update = 0

    def open(self):
        self.active = True
        self.devices[:] = ['<scanning...>']
        self.device_list.items = self.devices[:]
        self.device_list.selected = 0
        self._stop_scan.clear()
        self.status_msg = ""
        self._scan_thread = threading.Thread(target=self.scan_loop, daemon=True)
        self._scan_thread.start()

    def close(self):
        self.active = False
        self._stop_scan.set()

    def scan_loop(self):
        self.scanning = True
        while not self._stop_scan.is_set():
            self.devices[:] = self.scan_bt_devices()
            self.device_list.items = self.devices[:]
            self.device_list.max_offset = max(0, len(self.device_list.items) * self.LINE_HEIGHT - self.device_list.rect.height)
            time.sleep(self.SCAN_INTERVAL)
        self.scanning = False

    def scan_bt_devices(self):
        try:
            subprocess.run(['bluetoothctl', 'power', 'on'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['bluetoothctl', 'agent', 'NoInputNoOutput'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['bluetoothctl', 'default-agent'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['bluetoothctl', 'scan', 'on'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(4)  # short scan
            subprocess.run(['bluetoothctl', 'scan', 'off'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            out = subprocess.check_output(['bluetoothctl', 'devices'], stderr=subprocess.DEVNULL, text=True)
            found = []
            for line in out.splitlines():
                parts = line.split(None, 2)
                if len(parts) == 3 and parts[0] == 'Device':
                    addr, name = parts[1], parts[2]
                    found.append(f"{name} ({addr})")
            return found or ['<no devices found>']
        except Exception as e:
            print("Bluetooth scan failed:", e)
            return ['<scan failed>']

    def on_select_device(self, selection):
        # Parse MAC address from "Name (AA:BB:CC:DD:EE:FF)"
        if '(' in selection and ')' in selection:
            addr = selection.split('(')[-1].strip(')')
            self.selected_addr = addr
            self.status_msg = f"Connecting to {addr}..."
            self.device_list.set_enabled(False)
            threading.Thread(target=self.do_connect, args=(addr,), daemon=True).start()

    def do_connect(self, addr):
        try:
            subprocess.run(['bluetoothctl', 'pair', addr], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['bluetoothctl', 'trust', addr], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['bluetoothctl', 'connect', addr], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.status_msg = f"Connected to {addr}"
        except subprocess.CalledProcessError:
            self.status_msg = f"Failed to connect to {addr}"
        finally:
            self.device_list.set_enabled(True)
            self.last_update = time.time()

    def handle_event(self, event):
        if not self.active:
            return
        self.device_list.handle_event(event)
        # Optional: Esc or click outside closes menu
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()
        if event.type == pygame.MOUSEBUTTONDOWN and not self.rect.collidepoint(event.pos):
            self.close()

    def update(self):
        pass  # For future expansion

    def draw(self):
        surface = self.screen
        if not self.active:
            return
        # Draw background
        pygame.draw.rect(surface, self.BG_COLOR, self.rect)
        pygame.draw.rect(surface, self.HIGHLIGHT, self.rect, 2)

        # Draw title
        title = self.font.render("Bluetooth Devices", True, self.TEXT_COLOR)
        surface.blit(title, (self.rect.left + 20, self.rect.top + 15))

        # Draw status/info
        if self.status_msg:
            msg_surf = self.font.render(self.status_msg, True, self.TEXT_COLOR)
            surface.blit(msg_surf, (self.rect.left + 20, self.rect.bottom - 35))
        elif self.scanning:
            hint = self.font.render('Scanning...', True, self.TEXT_COLOR)
            surface.blit(hint, (self.rect.left + 20, self.rect.bottom - 35))

        # Draw device list
        self.device_list.draw(surface)

# --- Demo usage, using config for sizing/colors ---
if __name__ == "__main__":
    pygame.init()
    clock = pygame.time.Clock()
    bt_menu = BluetoothMenu()
    bt_menu.open()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            bt_menu.handle_event(event)

        bt_menu.screen.fill((0, 0, 0))
        bt_menu.update()
        bt_menu.draw()
        pygame.display.flip()
        clock.tick(60)
