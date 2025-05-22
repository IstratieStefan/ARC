import pygame
import threading
import subprocess
import time
import config
from ui_elements import ScrollableList, MessageBox

class BluetoothMenu:
    WIDTH = 480
    HEIGHT = 320
    BG_COLOR = config.COLORS.get('popup_bg', (36, 42, 48))
    TEXT_COLOR = config.COLORS.get('popup_fg', (240, 240, 240))
    HIGHLIGHT = config.ACCENT_COLOR
    FONT_NAME = config.FONT_NAME
    FONT_SIZE = 18
    LINE_HEIGHT = FONT_SIZE + 10
    SCAN_INTERVAL = getattr(config, 'BT_SCAN_INTERVAL', 8)  # seconds

    def __init__(self):
        self.active = False
        self.rect = pygame.Rect(0, config.TOPBAR_HEIGHT, self.WIDTH, self.HEIGHT - config.TOPBAR_HEIGHT)
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

    def get_wifi_strength(self):
        try:
            out = subprocess.check_output([
                'nmcli', '-t', '-f', 'ACTIVE,SIGNAL',
                'device', 'wifi', 'list'
            ], stderr=subprocess.DEVNULL).decode()
            for line in out.splitlines():
                parts = line.split(':')
                if parts[0] == 'yes' and len(parts) >= 2:
                    return int(parts[1])
        except:
            pass
        return 0

    def get_bt_status(self):
        try:
            out = subprocess.check_output(['bluetoothctl', 'show'], stderr=subprocess.DEVNULL, text=True)
            powered = False
            for line in out.splitlines():
                if line.strip().startswith("Powered:"):
                    powered = "yes" in line
                    break
            if not powered:
                return 0  # OFF

            out = subprocess.check_output(['bluetoothctl', 'devices'], stderr=subprocess.DEVNULL, text=True)
            for line in out.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    addr = parts[1]
                    info = subprocess.check_output(['bluetoothctl', 'info', addr], stderr=subprocess.DEVNULL, text=True)
                    for il in info.splitlines():
                        if il.strip().startswith("Connected:") and "yes" in il:
                            return 2  # CONNECTED

            return 1  # ON, but not connected
        except Exception:
            return 0  # If any error, treat as OFF

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

    def draw(self, surface):
        if not self.active:
            return
        # Draw background
        pygame.draw.rect(surface, self.BG_COLOR, self.rect)
        pygame.draw.rect(surface, config.ACCENT_COLOR, self.rect, 2)

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