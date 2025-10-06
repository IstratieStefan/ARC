#!/usr/bin/env python3
"""
Pygame Frontend for ESP32 Marauder (480x320)
--------------------------------------------

A tiny, keyboard-driven UI that talks to an ESP32 running the
Marauder firmware over a serial port.

Dependencies:
  pip install pygame pyserial

Run:
  python marauder_frontend.py

Default keybindings:
  Global
    Q           Quit
    C           Connect / Disconnect
    P           Cycle serial ports
    B           Toggle baud (115200 ↔ 921600)
    T           Type & send a custom command
    S           Save console log to file (logs/marauder_<timestamp>.txt)
    L           Toggle auto-scroll for console
    R           Refresh serial port list

  Menu
    ↑/↓         Move selection
    ENTER/RETURN  Send command for selected item

Notes:
- The command strings are sent verbatim to the Marauder over serial,
  followed by a newline ("\n"). Adjust the menu items to match your
  firmware's command names if they differ.
- The console (right pane) shows all lines received from serial.
- The app is fixed to 480×320 to fit small TFTs.
"""

import os
import sys
import time
import threading
import queue
from datetime import datetime
from config import config

import pygame
import serial
import serial.tools.list_ports as list_ports

# --------------------------- Config ---------------------------------
WIDTH, HEIGHT = 480, 320
FPS = 30
LEFT_W = 180
MARGIN = 6
LINE_SPACING = 4
BG = (8, 10, 14)
PANEL = (18, 22, 30)
PANEL_DARK = (14, 17, 24)
ACCENT = (90, 200, 250)
TEXT = (232, 236, 243)
TEXT_DIM = (160, 170, 185)
OK = (100, 220, 100)
ERR = (240, 90, 90)

DEFAULT_BAUD_1 = 115200
DEFAULT_BAUD_2 = 921600

# Menu items: (label, command)
MENU_ITEMS = [
    ("Help", "help"),
    ("List Commands", "?"),
    ("Scan WiFi APs", "scanap"),
    ("Scan Stations", "scanst"),
    ("Sniff Packets", "sniff"),
    ("Deauth (selected)", "deauth"),
    ("Probe Requests", "probereq"),
    ("Bluetooth Scan", "bt scan"),
    ("HCIDump", "bt sniff"),
    ("Stop Current Task", "stop"),
]

# ------------------------ Serial Manager ----------------------------
class SerialManager:
    def __init__(self):
        self.ser = None
        self.port = None
        self.baud = DEFAULT_BAUD_1
        self.rx_q = queue.Queue()
        self._stop = threading.Event()
        self._reader = None

    def available_ports(self):
        return [p.device for p in list_ports.comports()]

    def connect(self, port, baud):
        self.disconnect()
        try:
            self.ser = serial.Serial(port=port, baudrate=baud, timeout=0.05)
            self.port = port
            self.baud = baud
            self._stop.clear()
            self._reader = threading.Thread(target=self._read_loop, daemon=True)
            self._reader.start()
            self._put_local(f"[connected] {port} @ {baud}")
            return True, None
        except Exception as e:
            self._put_local(f"[error] connect failed: {e}")
            return False, str(e)

    def disconnect(self):
        if self.ser:
            try:
                self._stop.set()
                time.sleep(0.05)
                self.ser.close()
            except Exception:
                pass
        self.ser = None
        self.port = None

    def send(self, text):
        if not self.ser:
            self._put_local("[warn] not connected")
            return False
        try:
            data = (text.strip() + "\n").encode("utf-8", errors="ignore")
            self.ser.write(data)
            return True
        except Exception as e:
            self._put_local(f"[error] write failed: {e}")
            return False

    def _read_loop(self):
        buf = b""
        while not self._stop.is_set() and self.ser:
            try:
                chunk = self.ser.read(256)
                if chunk:
                    buf += chunk
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        try:
                            s = line.decode("utf-8", errors="replace")
                        except Exception:
                            s = str(line)
                        self.rx_q.put(s)
                else:
                    time.sleep(0.01)
            except Exception as e:
                self.rx_q.put(f"[error] read failed: {e}")
                break

    def _put_local(self, s):
        self.rx_q.put(s)

    def poll_lines(self, limit=500):
        out = []
        try:
            while len(out) < limit:
                out.append(self.rx_q.get_nowait())
        except queue.Empty:
            pass
        return out

    def is_connected(self):
        return self.ser is not None

# --------------------------- UI Helpers -----------------------------
class Label:
    def __init__(self, text, font, color=TEXT):
        self.text = text
        self.font = font
        self.color = color
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect()

    def draw(self, surface, x, y):
        surface.blit(self.image, (x, y))

class ScrollingText:
    def __init__(self, rect, font):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.lines = []
        self.auto_scroll = True
        self.offset = 0  # top line index

    def append(self, text):
        # Split incoming text into wrapped lines that fit width
        max_w = self.rect.w - 2*MARGIN
        for raw in text.split("\n"):
            self._wrap_and_add(raw, max_w)
        if self.auto_scroll:
            self.scroll_to_end()

    def _wrap_and_add(self, raw, max_w):
        if raw == "":
            self.lines.append("")
            return
        words = raw.split(" ")
        cur = ""
        for w in words:
            test = w if not cur else cur + " " + w
            if self.font.size(test)[0] <= max_w:
                cur = test
            else:
                if cur:
                    self.lines.append(cur)
                cur = w
        self.lines.append(cur)

    def scroll_to_end(self):
        # Show last N lines that fit area
        visible = self.visible_line_count()
        self.offset = max(0, len(self.lines) - visible)

    def visible_line_count(self):
        lh = self.font.get_linesize() + LINE_SPACING
        return max(1, (self.rect.h - 2*MARGIN) // lh)

    def draw(self, surface):
        pygame.draw.rect(surface, PANEL, self.rect, border_radius=8)
        inner = self.rect.inflate(-2*MARGIN, -2*MARGIN)

        lh = self.font.get_linesize() + LINE_SPACING
        start = self.offset
        end = min(len(self.lines), start + self.visible_line_count())
        y = inner.y
        for i in range(start, end):
            img = self.font.render(self.lines[i], True, TEXT)
            surface.blit(img, (inner.x, y))
            y += lh

        # Scrollbar (simple)
        if len(self.lines) > self.visible_line_count():
            bar_w = 6
            rail = pygame.Rect(self.rect.right - bar_w - 3, self.rect.y + 6,
                               bar_w, self.rect.h - 12)
            pygame.draw.rect(surface, PANEL_DARK, rail, border_radius=3)
            frac = self.visible_line_count() / max(1, len(self.lines))
            handle_h = max(20, int(rail.h * frac))
            max_off = max(1, len(self.lines) - self.visible_line_count())
            off_frac = self.offset / max_off
            handle_y = rail.y + int((rail.h - handle_h) * off_frac)
            handle = pygame.Rect(rail.x, handle_y, bar_w, handle_h)
            pygame.draw.rect(surface, ACCENT, handle, border_radius=3)

# --------------------------- App -----------------------------------
class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Marauder Frontend")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        # Fonts
        self.font = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 18)
        self.font_title = pygame.font.Font(None, 26)

        # Serial
        self.sm = SerialManager()
        self.ports = self.sm.available_ports()
        self.port_idx = 0 if self.ports else -1

        # Console
        right_rect = pygame.Rect(LEFT_W + MARGIN*2, MARGIN*2,
                                 WIDTH - LEFT_W - MARGIN*3,
                                 HEIGHT - 60)
        self.console = ScrollingText(right_rect, self.font_small)

        # Menu state
        self.menu_idx = 0

        # Status
        self.status = "ready"
        self.status_color = TEXT_DIM

        # Ensure logs dir exists
        os.makedirs("logs", exist_ok=True)

        self._push_local_help()

    # ------------------------ UI Drawing ---------------------------
    def draw(self):
        self.screen.fill(BG)

        # Left panel (menu)
        left = pygame.Rect(MARGIN, MARGIN, LEFT_W - MARGIN, HEIGHT - 2*MARGIN - 40)
        pygame.draw.rect(self.screen, PANEL, left, border_radius=10)

        title = self.font_title.render("Marauder", True, TEXT)
        self.screen.blit(title, (left.x + MARGIN, left.y + MARGIN))

        y = left.y + 36
        for i, (label, _cmd) in enumerate(MENU_ITEMS):
            is_sel = (i == self.menu_idx)
            txt_col = ACCENT if is_sel else TEXT
            bullet = "> " if is_sel else "  "
            img = self.font.render(bullet + label, True, txt_col)
            self.screen.blit(img, (left.x + MARGIN, y))
            y += self.font.get_linesize() + 6

        # Right panel (console)
        self.console.draw(self.screen)

        # Bottom status bar
        status_bar = pygame.Rect(MARGIN, HEIGHT - 36, WIDTH - 2*MARGIN, 28)
        pygame.draw.rect(self.screen, PANEL, status_bar, border_radius=8)

        port = self.ports[self.port_idx] if self.port_idx >= 0 and self.ports else "<no port>"
        conn = "connected" if self.sm.is_connected() else "disconnected"
        status_text = (
            f"[{conn}] port={port} baud={self.sm.baud} | "
            f"↑/↓ select  ENTER send   C connect   T type   P ports   B baud   L autoscroll   S save log   Q quit"
        )
        img = self.font_small.render(status_text, True, TEXT_DIM)
        self.screen.blit(img, (status_bar.x + 8, status_bar.y + 6))

        # Ephemeral status (top-right)
        if self.status:
            si = self.font_small.render(self.status, True, self.status_color)
            self.screen.blit(si, (WIDTH - si.get_width() - 12, 8))

        pygame.display.flip()

    # --------------------- Event Handling ---------------------------
    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_q,):
                    return False
                elif e.key in (pygame.K_UP,):
                    self.menu_idx = (self.menu_idx - 1) % len(MENU_ITEMS)
                elif e.key in (pygame.K_DOWN,):
                    self.menu_idx = (self.menu_idx + 1) % len(MENU_ITEMS)
                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._send_selected()
                elif e.key == pygame.K_c:
                    self._toggle_connect()
                elif e.key == pygame.K_p:
                    self._cycle_ports()
                elif e.key == pygame.K_b:
                    self._toggle_baud()
                elif e.key == pygame.K_t:
                    self._prompt_and_send()
                elif e.key == pygame.K_l:
                    self.console.auto_scroll = not self.console.auto_scroll
                    self._flash_status(f"auto-scroll: {self.console.auto_scroll}")
                elif e.key == pygame.K_s:
                    self._save_log()
                elif e.key == pygame.K_r:
                    self._refresh_ports()
        return True

    # --------------------- Actions ---------------------------------
    def _send_selected(self):
        label, cmd = MENU_ITEMS[self.menu_idx]
        self.console.append(f"> {cmd}")
        ok = self.sm.send(cmd)
        if not ok:
            self._flash_status("send failed", ERR)

    def _prompt_and_send(self):
        # Very simple text prompt in-console
        cmd = self._get_text_input("Type command: ")
        if cmd is None or cmd.strip() == "":
            self._flash_status("cancelled", TEXT_DIM)
            return
        self.console.append(f"> {cmd}")
        ok = self.sm.send(cmd)
        if not ok:
            self._flash_status("send failed", ERR)

    def _get_text_input(self, prompt):
        # Block until ENTER or ESC; render minimal prompt overlay
        overlay = pygame.Surface((WIDTH, 60), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        text = ""
        caret_on = True
        last_toggle = time.time()

        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return None
                elif e.type == pygame.KEYDOWN:
                    if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        return text
                    elif e.key == pygame.K_ESCAPE:
                        return None
                    elif e.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        ch = e.unicode
                        if ch and ch.isprintable():
                            text += ch

            if time.time() - last_toggle > 0.5:
                caret_on = not caret_on
                last_toggle = time.time()

            # draw underlying UI dimmed + prompt bar
            self.draw()
            self.screen.blit(overlay, (0, HEIGHT//2 - 30))
            bar = pygame.Rect(10, HEIGHT//2 - 25, WIDTH - 20, 50)
            pygame.draw.rect(self.screen, PANEL, bar, border_radius=8)
            msg = self.font.render(prompt + text + ("|" if caret_on else " "), True, TEXT)
            self.screen.blit(msg, (bar.x + 10, bar.y + 12))
            pygame.display.flip()
            self.clock.tick(FPS)

    def _toggle_connect(self):
        if self.sm.is_connected():
            self.sm.disconnect()
            self._flash_status("disconnected", TEXT_DIM)
        else:
            if self.port_idx < 0 or not self.ports:
                self._flash_status("no ports", ERR)
                return
            ok, err = self.sm.connect(self.ports[self.port_idx], self.sm.baud)
            if ok:
                self._flash_status("connected", OK)
            else:
                self._flash_status(f"connect error", ERR)

    def _cycle_ports(self):
        if not self.ports:
            self._flash_status("no ports", ERR)
            return
        self.port_idx = (self.port_idx + 1) % len(self.ports)
        self._flash_status(f"port: {self.ports[self.port_idx]}")

    def _refresh_ports(self):
        self.ports = self.sm.available_ports()
        self.port_idx = 0 if self.ports else -1
        msg = f"ports: {', '.join(self.ports) if self.ports else '<none>'}"
        self._flash_status(msg)

    def _toggle_baud(self):
        self.sm.baud = DEFAULT_BAUD_2 if self.sm.baud == DEFAULT_BAUD_1 else DEFAULT_BAUD_1
        self._flash_status(f"baud: {self.sm.baud}")

    def _save_log(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join("logs", f"marauder_{ts}.txt")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(self.console.lines))
            self._flash_status(f"saved {os.path.basename(path)}", OK)
        except Exception as e:
            self._flash_status(f"save failed: {e}", ERR)

    def _flash_status(self, text, color=TEXT_DIM):
        self.status = text
        self.status_color = color

    def _push_local_help(self):
        intro = [
            "Pygame Marauder Frontend",
            "- Select a serial port (P) and connect (C).",
            "- Use ↑/↓ to choose a menu item, ENTER to send.",
            "- Press T to type any custom command.",
            "- Press S to save the current log to file.",
        ]
        for line in intro:
            self.console.append(line)

    # --------------------- Main Loop --------------------------------
    def run(self):
        running = True
        while running:
            running = self.handle_events()

            # Drain serial lines
            for line in self.sm.poll_lines():
                self.console.append(line)

            self.draw()
            self.clock.tick(FPS)

        # Cleanup
        self.sm.disconnect()
        pygame.quit()


if __name__ == "__main__":
    try:
        App().run()
    except KeyboardInterrupt:
        pass
