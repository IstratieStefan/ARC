import pygame
import sys
import math
import subprocess
import os
import threading
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config
from ui_elements import Button, WarningMessage, TabManager

# --- Bluetooth Submenus ---

class BTScanMenu:
    def __init__(self):
        self.info = "Press R to scan for Bluetooth devices."
        self.devices = []
        self.selected_idx = 0
        self.scanning = False
        self.last_error = ""

    def scan_devices(self):
        self.scanning = True
        self.info = "Scanning..."
        self.devices = []
        try:
            # Uses bluetoothctl scan (works on most Linux distros)
            scan_cmd = "timeout 6s bluetoothctl scan on"
            subprocess.run(scan_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            out = subprocess.check_output("bluetoothctl devices", shell=True, text=True)
            devices = []
            for line in out.strip().split('\n'):
                if line.strip():
                    parts = line.split(' ', 2)
                    if len(parts) >= 3:
                        addr, name = parts[1], parts[2]
                        devices.append({'addr': addr, 'name': name})
            self.devices = devices
            self.info = f"Found {len(self.devices)} devices." if devices else "No devices found."
            self.selected_idx = 0
        except Exception as e:
            self.last_error = f"Scan failed: {e}"
            self.info = "Scan failed."
            self.devices = []
        self.scanning = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'back'
            elif event.key == pygame.K_r and not self.scanning:
                threading.Thread(target=self.scan_devices).start()
            elif event.key == pygame.K_DOWN and self.devices:
                self.selected_idx = (self.selected_idx + 1) % len(self.devices)
            elif event.key == pygame.K_UP and self.devices:
                self.selected_idx = (self.selected_idx - 1) % len(self.devices)
        return None

    def update(self):
        pass

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        surf = font.render("Scan Bluetooth", True, config.COLORS['accent'])
        surface.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH//2, 40)))
        info_font = pygame.font.SysFont(config.FONT_NAME, 24)
        info_surf = info_font.render(self.info, True, config.COLORS['text'])
        surface.blit(info_surf, info_surf.get_rect(center=(config.SCREEN_WIDTH//2, 90)))
        # List devices
        y = 140
        dev_font = pygame.font.SysFont(config.FONT_NAME, 22)
        for i, dev in enumerate(self.devices):
            s = f"{dev['name']}  |  {dev['addr']}"
            color = config.COLORS['accent'] if i == self.selected_idx else config.COLORS['text']
            surf = dev_font.render(s, True, color)
            rect = surf.get_rect(center=(config.SCREEN_WIDTH//2, y + i*32))
            surface.blit(surf, rect)
        # Error message
        if self.last_error:
            err_font = pygame.font.SysFont(config.FONT_NAME, 20)
            err_surf = err_font.render(self.last_error, True, (255, 80, 80))
            err_pos = (10, config.SCREEN_HEIGHT-60)
            err_rect = err_surf.get_rect(topleft=err_pos)
            bg_color = (60, 0, 0)
            padding = 6
            bg_rect = err_rect.inflate(padding, padding)
            pygame.draw.rect(surface, bg_color, bg_rect, border_radius=6)
            surface.blit(err_surf, err_pos)
        # Instructions
        hint_font = pygame.font.SysFont(config.FONT_NAME, 18)
        hints = "UP/DOWN = select  |  R = rescan  |  ESC = back"
        hint_surf = hint_font.render(hints, True, config.COLORS['text'])
        surface.blit(hint_surf, (10, config.SCREEN_HEIGHT-30))

class BTInfoMenu:
    def __init__(self):
        self.info = "Press ENTER to query info about a device."
        self.result = ""
        self.selected_addr = ""
        self.devices = []
        self.selected_idx = 0
        self.scanning = False
        self.last_error = ""
        self.refresh_devices()

    def refresh_devices(self):
        try:
            out = subprocess.check_output("bluetoothctl devices", shell=True, text=True)
            devices = []
            for line in out.strip().split('\n'):
                if line.strip():
                    parts = line.split(' ', 2)
                    if len(parts) >= 3:
                        addr, name = parts[1], parts[2]
                        devices.append({'addr': addr, 'name': name})
            self.devices = devices
            self.selected_idx = 0
        except Exception as e:
            self.last_error = f"Failed to list: {e}"
            self.devices = []

    def query_info(self, addr):
        self.result = "Querying info..."
        try:
            out = subprocess.check_output(f"bluetoothctl info {addr}", shell=True, text=True)
            self.result = out.strip()
        except Exception as e:
            self.result = f"Failed: {e}"

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'back'
            elif event.key == pygame.K_DOWN and self.devices:
                self.selected_idx = (self.selected_idx + 1) % len(self.devices)
            elif event.key == pygame.K_UP and self.devices:
                self.selected_idx = (self.selected_idx - 1) % len(self.devices)
            elif event.key == pygame.K_RETURN and self.devices:
                addr = self.devices[self.selected_idx]['addr']
                threading.Thread(target=self.query_info, args=(addr,)).start()
        return None

    def update(self):
        pass

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        surf = font.render("Device Info", True, config.COLORS['accent'])
        surface.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH//2, 40)))
        info_font = pygame.font.SysFont(config.FONT_NAME, 24)
        info_surf = info_font.render(self.info, True, config.COLORS['text'])
        surface.blit(info_surf, info_surf.get_rect(center=(config.SCREEN_WIDTH//2, 90)))
        # List devices
        y = 140
        dev_font = pygame.font.SysFont(config.FONT_NAME, 22)
        for i, dev in enumerate(self.devices):
            s = f"{dev['name']}  |  {dev['addr']}"
            color = config.COLORS['accent'] if i == self.selected_idx else config.COLORS['text']
            surf = dev_font.render(s, True, color)
            rect = surf.get_rect(center=(config.SCREEN_WIDTH//2, y + i*32))
            surface.blit(surf, rect)
        # Show result
        if self.result:
            res_font = pygame.font.SysFont(config.FONT_NAME, 18)
            lines = self.result.splitlines()
            for i, line in enumerate(lines):
                res_surf = res_font.render(line, True, config.COLORS['text'])
                surface.blit(res_surf, (40, config.SCREEN_HEIGHT - 100 + i*22))
        # Instructions
        hint_font = pygame.font.SysFont(config.FONT_NAME, 18)
        hints = "UP/DOWN = select  |  ENTER = info  |  ESC = back"
        hint_surf = hint_font.render(hints, True, config.COLORS['text'])
        surface.blit(hint_surf, (10, config.SCREEN_HEIGHT-30))

class BTSpoofMenu:
    def __init__(self):
        self.info = "Pair spoof: simulate pairing requests (demo)."
        self.devices = []
        self.selected_idx = 0
        self.last_action = ""
        self.refresh_devices()

    def refresh_devices(self):
        try:
            out = subprocess.check_output("bluetoothctl devices", shell=True, text=True)
            devices = []
            for line in out.strip().split('\n'):
                if line.strip():
                    parts = line.split(' ', 2)
                    if len(parts) >= 3:
                        addr, name = parts[1], parts[2]
                        devices.append({'addr': addr, 'name': name})
            self.devices = devices
            self.selected_idx = 0
        except Exception:
            self.devices = []

    def spoof_pair(self, addr):
        self.last_action = f"Pairing request sent to {addr} (demo)."
        # Real spoofing would require lower-level stack access (or tools like btproxy/ubertooth)
        # This is a placeholder.

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'back'
            elif event.key == pygame.K_DOWN and self.devices:
                self.selected_idx = (self.selected_idx + 1) % len(self.devices)
            elif event.key == pygame.K_UP and self.devices:
                self.selected_idx = (self.selected_idx - 1) % len(self.devices)
            elif event.key == pygame.K_RETURN and self.devices:
                addr = self.devices[self.selected_idx]['addr']
                threading.Thread(target=self.spoof_pair, args=(addr,)).start()
        return None

    def update(self):
        pass

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        surf = font.render("Pair Spoof", True, config.COLORS['accent'])
        surface.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH//2, 40)))
        info_font = pygame.font.SysFont(config.FONT_NAME, 24)
        info_surf = info_font.render(self.info, True, config.COLORS['text'])
        surface.blit(info_surf, info_surf.get_rect(center=(config.SCREEN_WIDTH//2, 90)))
        # List devices
        y = 140
        dev_font = pygame.font.SysFont(config.FONT_NAME, 22)
        for i, dev in enumerate(self.devices):
            s = f"{dev['name']}  |  {dev['addr']}"
            color = config.COLORS['accent'] if i == self.selected_idx else config.COLORS['text']
            surf = dev_font.render(s, True, color)
            rect = surf.get_rect(center=(config.SCREEN_WIDTH//2, y + i*32))
            surface.blit(surf, rect)
        # Last action
        if self.last_action:
            act_font = pygame.font.SysFont(config.FONT_NAME, 18)
            act_surf = act_font.render(self.last_action, True, config.COLORS['accent'])
            surface.blit(act_surf, (40, config.SCREEN_HEIGHT-80))
        # Instructions
        hint_font = pygame.font.SysFont(config.FONT_NAME, 18)
        hints = "UP/DOWN = select  |  ENTER = spoof pair  |  ESC = back"
        hint_surf = hint_font.render(hints, True, config.COLORS['text'])
        surface.blit(hint_surf, (10, config.SCREEN_HEIGHT-30))

class BTDoSMenu:
    def __init__(self):
        self.info = "DoS: L2Ping flood (demo)."
        self.devices = []
        self.selected_idx = 0
        self.last_action = ""
        self.attacking = False
        self.refresh_devices()

    def refresh_devices(self):
        try:
            out = subprocess.check_output("bluetoothctl devices", shell=True, text=True)
            devices = []
            for line in out.strip().split('\n'):
                if line.strip():
                    parts = line.split(' ', 2)
                    if len(parts) >= 3:
                        addr, name = parts[1], parts[2]
                        devices.append({'addr': addr, 'name': name})
            self.devices = devices
            self.selected_idx = 0
        except Exception:
            self.devices = []

    def start_attack(self, addr):
        self.attacking = True
        self.last_action = f"L2Ping flood started (to {addr})"
        # Run l2ping flood in background (demo, 10 packets)
        cmd = f"sudo l2ping -i hci0 -f -c 10 {addr}"
        try:
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=6)
            self.last_action = "Flood finished."
        except Exception as e:
            self.last_action = f"Failed: {e}"
        self.attacking = False

    def handle_event(self, event):
        if self.attacking:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'back'
            elif event.key == pygame.K_DOWN and self.devices:
                self.selected_idx = (self.selected_idx + 1) % len(self.devices)
            elif event.key == pygame.K_UP and self.devices:
                self.selected_idx = (self.selected_idx - 1) % len(self.devices)
            elif event.key == pygame.K_RETURN and self.devices:
                addr = self.devices[self.selected_idx]['addr']
                threading.Thread(target=self.start_attack, args=(addr,)).start()
        return None

    def update(self):
        pass

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        surf = font.render("DoS Attack", True, config.COLORS['accent'])
        surface.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH//2, 40)))
        info_font = pygame.font.SysFont(config.FONT_NAME, 24)
        info_surf = info_font.render(self.info, True, config.COLORS['text'])
        surface.blit(info_surf, info_surf.get_rect(center=(config.SCREEN_WIDTH//2, 90)))
        # List devices
        y = 140
        dev_font = pygame.font.SysFont(config.FONT_NAME, 22)
        for i, dev in enumerate(self.devices):
            s = f"{dev['name']}  |  {dev['addr']}"
            color = config.COLORS['accent'] if i == self.selected_idx else config.COLORS['text']
            surf = dev_font.render(s, True, color)
            rect = surf.get_rect(center=(config.SCREEN_WIDTH//2, y + i*32))
            surface.blit(surf, rect)
        # Last action
        if self.last_action:
            act_font = pygame.font.SysFont(config.FONT_NAME, 18)
            act_surf = act_font.render(self.last_action, True, config.COLORS['accent'])
            surface.blit(act_surf, (40, config.SCREEN_HEIGHT-80))
        # Instructions
        hint_font = pygame.font.SysFont(config.FONT_NAME, 18)
        hints = "UP/DOWN = select  |  ENTER = flood  |  ESC = back"
        hint_surf = hint_font.render(hints, True, config.COLORS['text'])
        surface.blit(hint_surf, (10, config.SCREEN_HEIGHT-30))

class BTSavedMenu:
    def __init__(self):
        self.info = "No logs implemented yet. (Demo page)"
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'back'
    def update(self): pass
    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        surf = font.render("Saved Logs", True, config.COLORS['accent'])
        surface.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH//2, 40)))
        info_font = pygame.font.SysFont(config.FONT_NAME, 24)
        info_surf = info_font.render(self.info, True, config.COLORS['text'])
        surface.blit(info_surf, info_surf.get_rect(center=(config.SCREEN_WIDTH//2, 130)))
        # Instructions
        hint_font = pygame.font.SysFont(config.FONT_NAME, 18)
        hints = "ESC = back"
        hint_surf = hint_font.render(hints, True, config.COLORS['text'])
        surface.blit(hint_surf, (10, config.SCREEN_HEIGHT-30))

# --- Bluetooth Main Menu ---

class BluetoothMenu:
    ITEMS_PER_TAB = 3

    def __init__(self):
        self.selected_idx = 0
        self.active_page = None
        self.types_bt = [
            "Scan Devices",
            "Device Info",
            "Pair Spoof",
            "DoS Attack",
            "Saved Logs"
        ]
        self.btns = [
            Button(t, (0, 0, 400, 60), lambda idx=i: self.open_page(idx))
            for i, t in enumerate(self.types_bt)
        ]
        tabs = math.ceil(len(self.types_bt) / self.ITEMS_PER_TAB)
        self.tabmgr = TabManager(["" for _ in range(tabs)])
        self.warning = WarningMessage("")
        self.pages = [
            BTScanMenu(),
            BTInfoMenu(),
            BTSpoofMenu(),
            BTDoSMenu(),
            BTSavedMenu()
        ]

    def open_page(self, idx):
        self.active_page = self.pages[idx]

    def handle_event(self, event):
        if self.active_page:
            result = self.active_page.handle_event(event)
            if result == 'back':
                self.active_page = None
            return

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        self.tabmgr.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_DOWN, pygame.K_UP):
                step = 1 if event.key == pygame.K_DOWN else -1
                self.selected_idx = (self.selected_idx + step) % len(self.btns)
                self.tabmgr.active = self.selected_idx // self.ITEMS_PER_TAB
                return
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.btns[self.selected_idx].callback()
                return
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()

        for i, btn in enumerate(self.btns):
            btn.handle_event(event)
            if btn.hovered:
                self.selected_idx = i
                self.tabmgr.active = i // self.ITEMS_PER_TAB

    def update(self):
        if self.active_page:
            self.active_page.update()
        self.warning.update()

    def draw(self, surface):
        if self.active_page:
            self.active_page.draw(surface)
            return

        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        title_surf = font.render("Bluetooth Tools", True, config.COLORS['text'])
        surface.blit(title_surf, title_surf.get_rect(center=(config.SCREEN_WIDTH//2, 35)))
        active_tab = self.tabmgr.active
        start = active_tab * self.ITEMS_PER_TAB
        end = start + self.ITEMS_PER_TAB
        for idx, btn in enumerate(self.btns[start:end]):
            global_idx = start + idx
            btn.rect.x = config.SCREEN_WIDTH//2 - btn.rect.width//2
            btn.rect.y = 70 + idx * (btn.rect.height + 10)
            pygame.draw.rect(
                surface,
                config.COLORS['button'],
                btn.rect,
                border_radius=config.RADIUS['app_button']
            )
            lbl_font = pygame.font.SysFont(config.FONT_NAME, 30)
            lbl_surf = lbl_font.render(btn.text, True, config.COLORS['text_light'])
            surface.blit(lbl_surf, lbl_surf.get_rect(center=btn.rect.center))
            if global_idx == self.selected_idx:
                pygame.draw.rect(
                    surface,
                    config.COLORS['accent'],
                    btn.rect.inflate(6, 6),
                    width=4,
                    border_radius=config.RADIUS['app_button'] + 4
                )
        self.tabmgr.draw(surface)
        self.warning.draw(surface)

# --- To test standalone ---
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Bluetooth Tools Menu")
    clock = pygame.time.Clock()
    menu = BluetoothMenu()
    while True:
        for event in pygame.event.get():
            menu.handle_event(event)
        menu.update()
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(config.FPS)
