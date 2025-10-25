import pygame
import sys
import math
import subprocess
import os
import threading
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from arc.core.config import config
from arc.core.ui_elements import Button, WarningMessage, TabManager

# --- Helper functions for YAML config style ---
def c(name, default=None):
    return getattr(config.colors, name, default or (200, 200, 200))

def r(name, default=12):
    return getattr(config.radius, name, default)

def fnt(size=None):
    return pygame.font.SysFont(getattr(config.font, "name", "Arial"), size or getattr(config.font, "size", 18))

def s(name, default=480):
    return getattr(config.screen, name, default)

def fps():
    return getattr(config, "fps", 30)

# --- BTScanMenu ---
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
            subprocess.run("timeout 6s bluetoothctl scan on", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
        surface.fill(c('background'))
        font = fnt(40)
        surf = font.render("Scan Bluetooth", True, c('accent'))
        surface.blit(surf, surf.get_rect(center=(s("width")//2, 40)))
        info_font = fnt(24)
        info_surf = info_font.render(self.info, True, c('text'))
        surface.blit(info_surf, info_surf.get_rect(center=(s("width")//2, 90)))
        y = 140
        dev_font = fnt(22)
        for i, dev in enumerate(self.devices):
            s_txt = f"{dev['name']}  |  {dev['addr']}"
            color = c('accent') if i == self.selected_idx else c('text')
            surf = dev_font.render(s_txt, True, color)
            rect = surf.get_rect(center=(s("width")//2, y + i*32))
            surface.blit(surf, rect)
        if self.last_error:
            err_font = fnt(20)
            err_surf = err_font.render(self.last_error, True, (255, 80, 80))
            err_pos = (10, s("height")-60)
            err_rect = err_surf.get_rect(topleft=err_pos)
            bg_color = (60, 0, 0)
            padding = 6
            bg_rect = err_rect.inflate(padding, padding)
            pygame.draw.rect(surface, bg_color, bg_rect, border_radius=6)
            surface.blit(err_surf, err_pos)
        hint_font = fnt(18)
        hints = "UP/DOWN = select  |  R = rescan  |  ESC = back"
        hint_surf = hint_font.render(hints, True, c('text'))
        surface.blit(hint_surf, (10, s("height")-30))

# --- BTInfoMenu ---
class BTInfoMenu:
    def __init__(self):
        self.info = "Press ENTER to query info about a device."
        self.result = ""
        self.selected_addr = ""
        self.devices = []
        self.selected_idx = 0
        self.scanning = False
        self.last_error = ""
        self.page = 'list'
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
        if self.page == 'list':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'back'
                elif event.key == pygame.K_DOWN and self.devices:
                    self.selected_idx = (self.selected_idx + 1) % len(self.devices)
                elif event.key == pygame.K_UP and self.devices:
                    self.selected_idx = (self.selected_idx - 1) % len(self.devices)
                elif event.key == pygame.K_RETURN and self.devices:
                    addr = self.devices[self.selected_idx]['addr']
                    self.selected_addr = addr
                    self.result = "Querying info..."
                    self.page = 'info'
                    threading.Thread(target=self.query_info, args=(addr,)).start()
        elif self.page == 'info':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.page = 'list'
                    self.result = ""
        return None

    def update(self):
        pass

    def draw(self, surface):
        surface.fill(c('background'))
        font = fnt(40)
        if self.page == 'list':
            surf = font.render("Device Info", True, c('accent'))
            surface.blit(surf, surf.get_rect(center=(s("width")//2, 40)))
            info_font = fnt(24)
            info_surf = info_font.render(self.info, True, c('text'))
            surface.blit(info_surf, info_surf.get_rect(center=(s("width")//2, 90)))
            y = 140
            dev_font = fnt(22)
            for i, dev in enumerate(self.devices):
                s_txt = f"{dev['name']}  |  {dev['addr']}"
                color = c('accent') if i == self.selected_idx else c('text')
                surf = dev_font.render(s_txt, True, color)
                rect = surf.get_rect(center=(s("width")//2, y + i*32))
                surface.blit(surf, rect)
            hint_font = fnt(18)
            hints = "UP/DOWN = select  |  ENTER = info  |  ESC = back"
            hint_surf = hint_font.render(hints, True, c('text'))
            surface.blit(hint_surf, (10, s("height")-30))
        elif self.page == 'info':
            surf = font.render("Device Details", True, c('accent'))
            surface.blit(surf, surf.get_rect(center=(s("width")//2, 40)))
            info_font = fnt(22)
            addr_line = info_font.render(self.selected_addr, True, c('text'))
            surface.blit(addr_line, (40, 90))
            res_font = fnt(18)
            lines = self.result.splitlines()
            for i, line in enumerate(lines):
                res_surf = res_font.render(line, True, c('text'))
                surface.blit(res_surf, (40, 130 + i*22))
            hint_font = fnt(18)
            hints = "ESC = back"
            hint_surf = hint_font.render(hints, True, c('text'))
            surface.blit(hint_surf, (10, s("height")-30))

# --- BTSpoofMenu ---
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
        surface.fill(c('background'))
        font = fnt(40)
        surf = font.render("Pair Spoof", True, c('accent'))
        surface.blit(surf, surf.get_rect(center=(s("width")//2, 40)))
        info_font = fnt(24)
        info_surf = info_font.render(self.info, True, c('text'))
        surface.blit(info_surf, info_surf.get_rect(center=(s("width")//2, 90)))
        y = 140
        dev_font = fnt(22)
        for i, dev in enumerate(self.devices):
            s_txt = f"{dev['name']}  |  {dev['addr']}"
            color = c('accent') if i == self.selected_idx else c('text')
            surf = dev_font.render(s_txt, True, color)
            rect = surf.get_rect(center=(s("width")//2, y + i*32))
            surface.blit(surf, rect)
        if self.last_action:
            act_font = fnt(18)
            act_surf = act_font.render(self.last_action, True, c('accent'))
            surface.blit(act_surf, (40, s("height")-80))
        hint_font = fnt(18)
        hints = "UP/DOWN = select  |  ENTER = spoof pair  |  ESC = back"
        hint_surf = hint_font.render(hints, True, c('text'))
        surface.blit(hint_surf, (10, s("height")-30))

# --- BTDoSMenu ---
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
        surface.fill(c('background'))
        font = fnt(40)
        surf = font.render("DoS Attack", True, c('accent'))
        surface.blit(surf, surf.get_rect(center=(s("width")//2, 40)))
        info_font = fnt(24)
        info_surf = info_font.render(self.info, True, c('text'))
        surface.blit(info_surf, info_surf.get_rect(center=(s("width")//2, 90)))
        y = 140
        dev_font = fnt(22)
        for i, dev in enumerate(self.devices):
            s_txt = f"{dev['name']}  |  {dev['addr']}"
            color = c('accent') if i == self.selected_idx else c('text')
            surf = dev_font.render(s_txt, True, color)
            rect = surf.get_rect(center=(s("width")//2, y + i*32))
            surface.blit(surf, rect)
        if self.last_action:
            act_font = fnt(18)
            act_surf = act_font.render(self.last_action, True, c('accent'))
            surface.blit(act_surf, (40, s("height")-80))
        hint_font = fnt(18)
        hints = "UP/DOWN = select  |  ENTER = flood  |  ESC = back"
        hint_surf = hint_font.render(hints, True, c('text'))
        surface.blit(hint_surf, (10, s("height")-30))

# --- BTSavedMenu ---
class BTSavedMenu:
    def __init__(self):
        self.info = "No logs implemented yet. (Demo page)"
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'back'
    def update(self): pass
    def draw(self, surface):
        surface.fill(c('background'))
        font = fnt(40)
        surf = font.render("Saved Logs", True, c('accent'))
        surface.blit(surf, surf.get_rect(center=(s("width")//2, 40)))
        info_font = fnt(24)
        info_surf = info_font.render(self.info, True, c('text'))
        surface.blit(info_surf, info_surf.get_rect(center=(s("width")//2, 130)))
        hint_font = fnt(18)
        hints = "ESC = back"
        hint_surf = hint_font.render(hints, True, c('text'))
        surface.blit(hint_surf, (10, s("height")-30))

# --- BTConnectMenu ---
class BTConnectMenu:
    MAX_VISIBLE = 7

    def __init__(self):
        self.info = "O/F: On/Off | R: Scan | C: Connect | D: Disconnect | P: Pair | U: Unpair"
        self.status = self.get_bt_status()
        self.devices = []
        self.selected_idx = 0
        self.last_action = ""
        self.scanning = False
        self.scroll_offset = 0
        self.refresh_thread = None

    def get_bt_status(self):
        try:
            out = subprocess.check_output(['bluetoothctl', 'show'], text=True, stderr=subprocess.DEVNULL)
            for line in out.splitlines():
                if "Powered:" in line:
                    return "On" if "yes" in line else "Off"
        except Exception:
            return "Unknown"

    def set_bt_power(self, enable):
        cmd = ['bluetoothctl', 'power', 'on' if enable else 'off']
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.status = self.get_bt_status()
            self.last_action = f"Bluetooth turned {'on' if enable else 'off'}."
        except Exception as e:
            self.last_action = f"Failed to change power: {e}"

    def scan_devices(self):
        self.scanning = True
        self.info = "Scanning for devices..."
        try:
            subprocess.run("timeout 5s bluetoothctl scan on", shell=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            out = subprocess.check_output("bluetoothctl devices", shell=True, text=True)
            devices = []
            for line in out.strip().split('\n'):
                if line.strip():
                    parts = line.split(' ', 2)
                    if len(parts) >= 3:
                        addr, name = parts[1], parts[2]
                        connected = self.is_connected(addr)
                        paired = self.is_paired(addr)
                        devices.append({'addr': addr, 'name': name, 'connected': connected, 'paired': paired})
            self.devices = devices
            self.info = f"Found {len(self.devices)} devices." if devices else "No devices found."
            self.selected_idx = 0
            self.scroll_offset = 0
        except Exception as e:
            self.info = f"Scan failed: {e}"
            self.devices = []
        self.scanning = False

    def is_connected(self, addr):
        try:
            out = subprocess.check_output(f"bluetoothctl info {addr}", shell=True, text=True)
            for line in out.splitlines():
                if "Connected:" in line:
                    return "yes" in line
        except Exception:
            pass
        return False

    def is_paired(self, addr):
        try:
            out = subprocess.check_output(f"bluetoothctl info {addr}", shell=True, text=True)
            for line in out.splitlines():
                if "Paired:" in line:
                    return "yes" in line
        except Exception:
            pass
        return False

    def pair_device(self, addr):
        self.last_action = f"Pairing with {addr}..."
        try:
            subprocess.run(['bluetoothctl', 'pair', addr], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            subprocess.run(['bluetoothctl', 'trust', addr], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.last_action = f"Paired and trusted {addr}."
        except subprocess.CalledProcessError as e:
            self.last_action = f"Pair failed: {e.stderr.strip() or e.stdout.strip()}"
        self.scan_devices()

    def unpair_device(self, addr):
        self.last_action = f"Unpairing {addr}..."
        try:
            subprocess.run(['bluetoothctl', 'remove', addr], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.last_action = f"Removed {addr}."
        except subprocess.CalledProcessError as e:
            self.last_action = f"Remove failed: {e.stderr.strip() or e.stdout.strip()}"
        self.scan_devices()

    def connect_device(self, addr):
        self.last_action = f"Connecting to {addr}..."
        try:
            subprocess.run(['bluetoothctl', 'connect', addr], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.last_action = f"Connected to {addr}."
        except subprocess.CalledProcessError as e:
            self.last_action = f"Connect failed: {e.stderr.strip() or e.stdout.strip()}"
        self.scan_devices()

    def disconnect_device(self, addr):
        self.last_action = f"Disconnecting {addr}..."
        try:
            subprocess.run(['bluetoothctl', 'disconnect', addr], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.last_action = f"Disconnected {addr}."
        except subprocess.CalledProcessError as e:
            self.last_action = f"Disconnect failed: {e.stderr.strip() or e.stdout.strip()}"
        self.scan_devices()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'back'
            elif event.key == pygame.K_r and not self.scanning:
                threading.Thread(target=self.scan_devices).start()
            elif event.key == pygame.K_DOWN and self.devices:
                self.selected_idx = min(self.selected_idx + 1, len(self.devices) - 1)
                if self.selected_idx - self.scroll_offset >= self.MAX_VISIBLE:
                    self.scroll_offset += 1
            elif event.key == pygame.K_UP and self.devices:
                self.selected_idx = max(self.selected_idx - 1, 0)
                if self.selected_idx < self.scroll_offset:
                    self.scroll_offset = self.selected_idx
            elif event.key == pygame.K_c and self.devices:
                addr = self.devices[self.selected_idx]['addr']
                threading.Thread(target=self.connect_device, args=(addr,)).start()
            elif event.key == pygame.K_d and self.devices:
                addr = self.devices[self.selected_idx]['addr']
                threading.Thread(target=self.disconnect_device, args=(addr,)).start()
            elif event.key == pygame.K_o:
                threading.Thread(target=self.set_bt_power, args=(True,)).start()
            elif event.key == pygame.K_f:
                threading.Thread(target=self.set_bt_power, args=(False,)).start()
            elif event.key == pygame.K_p and self.devices:
                addr = self.devices[self.selected_idx]['addr']
                threading.Thread(target=self.pair_device, args=(addr,)).start()
            elif event.key == pygame.K_u and self.devices:
                addr = self.devices[self.selected_idx]['addr']
                threading.Thread(target=self.unpair_device, args=(addr,)).start()
        return None

    def update(self):
        self.status = self.get_bt_status()

    def draw(self, surface):
        surface.fill(c('background'))
        font = fnt(40)
        surf = font.render("Bluetooth Connect", True, c('accent'))
        surface.blit(surf, surf.get_rect(center=(s("width") // 2, 40)))
        status_font = fnt(24)
        stat_surf = status_font.render(f"Bluetooth: {self.status}", True, c('text'))
        surface.blit(stat_surf, (40, 90))
        info_font = fnt(22)
        info_surf = info_font.render(self.info, True, c('text'))
        surface.blit(info_surf, (40, 130))

        y = 180
        dev_font = fnt(22)
        visible_devices = self.devices[self.scroll_offset:self.scroll_offset + self.MAX_VISIBLE]
        for i, dev in enumerate(visible_devices):
            idx = i + self.scroll_offset
            connected = "✓" if dev.get('connected') else ""
            paired = "[Paired]" if dev.get('paired') else ""
            s_txt = f"{dev['name']} {paired} {connected}  |  {dev['addr']}"
            color = c('accent') if idx == self.selected_idx else c('text')
            surf = dev_font.render(s_txt, True, color)
            rect = surf.get_rect(center=(s("width") // 2, y + i * 32))
            surface.blit(surf, rect)
        arrow_font = fnt(24)
        if self.scroll_offset > 0:
            up_surf = arrow_font.render("^", True, c('text'))
            surface.blit(up_surf, (s("width") // 2, y - 28))
        if self.scroll_offset + self.MAX_VISIBLE < len(self.devices):
            down_surf = arrow_font.render("v", True, c('text'))
            surface.blit(down_surf, (s("width") // 2, y + self.MAX_VISIBLE * 32))

        if self.last_action:
            act_font = fnt(18)
            act_surf = act_font.render(self.last_action, True, c('accent'))
            surface.blit(act_surf, (40, s("height") - 80))

        hint_font = fnt(18)
        hints = "O/F: On/Off | R: Scan | C: Connect | D: Disconnect | P: Pair | U: Unpair"
        hint_surf = hint_font.render(hints, True, c('text'))
        surface.blit(hint_surf, (10, s("height") - 30))

# --- BluetoothMenu (Main) ---
class BluetoothMenu:
    ITEMS_PER_TAB = 3

    def __init__(self):
        self.selected_idx = 0
        self.active_page = None
        self.types_bt = [
            "Connect Menu",
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
            BTConnectMenu(),
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

        surface.fill(c('background'))
        font = fnt(40)
        title_surf = font.render("Bluetooth Tools", True, c('text'))
        surface.blit(title_surf, title_surf.get_rect(center=(s("width")//2, 35)))
        active_tab = self.tabmgr.active
        start = active_tab * self.ITEMS_PER_TAB
        end = start + self.ITEMS_PER_TAB
        for idx, btn in enumerate(self.btns[start:end]):
            global_idx = start + idx
            btn.rect.x = s("width")//2 - btn.rect.width//2
            btn.rect.y = 70 + idx * (btn.rect.height + 10)
            pygame.draw.rect(
                surface,
                c('button'),
                btn.rect,
                border_radius=r('app_button', 12)
            )
            lbl_font = fnt(30)
            lbl_surf = lbl_font.render(btn.text, True, c('text_light'))
            surface.blit(lbl_surf, lbl_surf.get_rect(center=btn.rect.center))
            if global_idx == self.selected_idx:
                pygame.draw.rect(
                    surface,
                    c('accent'),
                    btn.rect.inflate(6, 6),
                    width=4,
                    border_radius=r('app_button', 12) + 4
                )
        self.tabmgr.draw(surface)
        self.warning.draw(surface)

# --- To test standalone ---
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((s("width"), s("height")), pygame.FULLSCREEN)
    pygame.display.set_caption("Bluetooth Tools Menu")
    clock = pygame.time.Clock()
    menu = BluetoothMenu()
    while True:
        for event in pygame.event.get():
            menu.handle_event(event)
        menu.update()
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(30)
