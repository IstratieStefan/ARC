import pygame
import sys
import math
import time
import serial
import serial.tools.list_ports
import config
import json
import datetime
from ui_elements import Button, WarningMessage, TabManager

class NFCMenu:
    ITEMS_PER_TAB = 3

    def __init__(self):
        self.selected_idx = 0
        self.serial = None
        self.loading = False
        self.connecting = True
        self.loading_text = "Connecting to NFC module..."
        self.last_response = ""
        self.response_pending = False

        self.pending_save = None
        self.awaiting_title = False
        self.title_input = ""

        self.types_nfc = [
            ("Scan Tag", "scan"),
            ("Read Tag", "read"),
            ("Write", "write https://github.com/IstratieStefan/ARC"),
            ("Authenticate Sector", "auth"),
            ("P2P Exchange", "p2p"),
            ("List Tag Types", "list")
        ]

        self.btns = [
            Button(label, (0, 0, 400, 60), lambda cmd=cmd, lbl=label: self.send_command(cmd, lbl))
            for label, cmd in self.types_nfc
        ]

        tabs = math.ceil(len(self.types_nfc) / self.ITEMS_PER_TAB)
        self.tabmgr = TabManager(["" for _ in range(tabs)])

        self.warning = WarningMessage("")

        pygame.time.set_timer(pygame.USEREVENT + 1, 100, loops=1)

    def connect_serial(self):
        ports = list(serial.tools.list_ports.comports())
        print("Available ports:")
        for p in ports:
            print(f" - {p.device} : {p.description}")

        for p in ports:
            if "ttyACM" in p.device or "ttyUSB" in p.device or "wchusbserial" in p.device:
                try:
                    print(f"Trying {p.device}...")
                    ser = serial.Serial(p.device, 115200, timeout=1)
                    time.sleep(1)
                    id_str = ser.read(100).decode(errors="ignore")
                    print(f"Received: {id_str}")
                    if "PN532 NFC ready." in id_str:
                        self.serial = ser
                        self.connecting = False
                        self.warning.text = f"Connected to NFC module on {p.device}"
                        self.warning.show()
                        return
                    else:
                        ser.close()
                except serial.SerialException as e:
                    print(f"Failed to connect to {p.device}: {e}")

        self.connecting = False
        self.warning.text = "Failed to connect to any NFC module"
        self.warning.show()

    def send_command(self, command, label):
        if self.serial and self.serial.is_open:
            self.loading = True
            self.loading_text = f"{label}..."
            self.response_pending = True
            self.serial.write((command + '\n').encode())
            pygame.time.set_timer(pygame.USEREVENT, 100)
        else:
            self.warning.text = "Serial not connected."
            self.warning.show()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.USEREVENT + 1 and self.connecting:
            self.connect_serial()
            return

        if event.type == pygame.USEREVENT and self.response_pending:
            self.check_response()
            return

        if self.pending_save and not self.awaiting_title:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    self.awaiting_title = True
                    self.warning.text = "Enter a title for the tag:"
                    self.title_input = ""
                    self.warning.show()
                elif event.key == pygame.K_n:
                    self.warning.text = "Tag discarded."
                    self.warning.show()
                    self.pending_save = None
            return

        if self.awaiting_title:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.title_input.strip():
                    uid_hex, data_bytes = self.pending_save
                    self.save_tag(uid_hex, data_bytes, self.title_input.strip())
                    self.warning.text = f"Saved as: {self.title_input.strip()}"
                    self.pending_save = None
                    self.awaiting_title = False
                    self.title_input = ""
                    self.warning.show()
                elif event.key == pygame.K_BACKSPACE:
                    self.title_input = self.title_input[:-1]
                else:
                    if len(event.unicode) == 1 and len(self.title_input) < 30:
                        self.title_input += event.unicode
            return

        self.tabmgr.handle_event(event)

        if not self.loading and not self.connecting:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_UP):
                    step = 1 if event.key == pygame.K_DOWN else -1
                    self.selected_idx = (self.selected_idx + step) % len(self.btns)
                    self.tabmgr.active = self.selected_idx // self.ITEMS_PER_TAB
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.btns[self.selected_idx].callback()

            for i, btn in enumerate(self.btns):
                btn.handle_event(event)
                if btn.hovered:
                    self.selected_idx = i
                    self.tabmgr.active = i // self.ITEMS_PER_TAB

    def check_response(self):
        response = self.serial.read_all().decode(errors='ignore').strip()
        if response:
            self.loading = False
            self.response_pending = False
            self.last_response = response
            self.warning.text = response
            self.warning.show()

            if "Found tag UID:" in response and "Data:" in response:
                try:
                    uid_line = [line for line in response.splitlines() if "Found tag UID:" in line][0]
                    uid_parts = uid_line.split("Found tag UID:")[-1].strip().split()
                    uid_hex = ''.join(uid_parts)

                    data_line = [line for line in response.splitlines() if "Data:" in line][0]
                    data_str = data_line.split("Data:")[-1].strip()
                    data_bytes = bytes(data_str, 'latin1')

                    self.pending_save = (uid_hex, data_bytes)
                    self.warning.text = f"Tag UID: {uid_hex}\nSave this tag? [Y/N]"
                    self.warning.show()
                except Exception as e:
                    print(f"Error parsing tag data: {e}")

    def save_tag(self, uid_hex, data_bytes, title):
        tag = {
            "uid": uid_hex,
            "data_block_4": data_bytes.hex().upper(),
            "title": title,
            "timestamp": datetime.datetime.now().isoformat()
        }

        try:
            with open("saved_tags.json", "r") as f:
                tags = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            tags = []

        tags.append(tag)

        with open("saved_tags.json", "w") as f:
            json.dump(tags, f, indent=2)

    def update(self):
        self.warning.update()

    def draw(self, surface):
        surface.fill(config.COLORS['background'])

        font = pygame.font.SysFont(config.FONT_NAME, 40)
        title_surf = font.render("NFC Tools", True, config.COLORS['text'])
        surface.blit(title_surf, title_surf.get_rect(center=(config.SCREEN_WIDTH // 2, 35)))

        if self.connecting or self.loading:
            font = pygame.font.SysFont(config.FONT_NAME, 30)
            txt = font.render(self.loading_text, True, config.COLORS['accent'])
            surface.blit(txt, txt.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)))
            return

        active_tab = self.tabmgr.active
        start = active_tab * self.ITEMS_PER_TAB
        end = start + self.ITEMS_PER_TAB

        for idx, btn in enumerate(self.btns[start:end]):
            global_idx = start + idx
            btn.rect.x = config.SCREEN_WIDTH // 2 - btn.rect.width // 2
            btn.rect.y = 70 + idx * (btn.rect.height + 10)

            pygame.draw.rect(surface, config.COLORS['button'], btn.rect, border_radius=config.RADIUS['app_button'])
            lbl_font = pygame.font.SysFont(config.FONT_NAME, 30)
            lbl_surf = lbl_font.render(btn.text, True, config.COLORS['text_light'])
            surface.blit(lbl_surf, lbl_surf.get_rect(center=btn.rect.center))

            if global_idx == self.selected_idx:
                pygame.draw.rect(
                    surface,
                    config.ACCENT_COLOR,
                    btn.rect.inflate(6, 6),
                    width=3,
                    border_radius=config.RADIUS['app_button'] + 3
                )

        self.tabmgr.draw(surface)
        self.warning.draw(surface)

        if self.awaiting_title:
            font = pygame.font.SysFont(config.FONT_NAME, 24)
            prompt = font.render("Title: " + self.title_input, True, config.COLORS['text'])
            surface.blit(prompt, (config.SCREEN_WIDTH // 2 - 150, config.SCREEN_HEIGHT - 50))


def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("NFC Tools Menu")
    clock = pygame.time.Clock()

    menu = NFCMenu()
    while True:
        for event in pygame.event.get():
            menu.handle_event(event)
        menu.update()
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(config.FPS)


if __name__ == '__main__':
    main()