import pygame
import sys
import math
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config
from ui_elements import Button, WarningMessage, TabManager

# --- Per-page Submenus ---

class ScanMenu:
    def __init__(self):
        self.info = "This page will show scanned WiFi networks."

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'back'

    def update(self):
        pass

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        surf = font.render("Scan Networks", True, config.COLORS['accent'])
        surface.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH//2, 40)))
        # Display info text
        info_font = pygame.font.SysFont(config.FONT_NAME, 28)
        info_surf = info_font.render(self.info, True, config.COLORS['text'])
        surface.blit(info_surf, info_surf.get_rect(center=(config.SCREEN_WIDTH//2, 150)))

class HandshakeMenu:
    def __init__(self):
        self.info = "Capture WPA/WPA2 handshakes here."

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'back'

    def update(self):
        pass

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        surf = font.render("Capture Handshake", True, config.COLORS['accent'])
        surface.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH//2, 40)))
        info_font = pygame.font.SysFont(config.FONT_NAME, 28)
        info_surf = info_font.render(self.info, True, config.COLORS['text'])
        surface.blit(info_surf, info_surf.get_rect(center=(config.SCREEN_WIDTH//2, 150)))

class DeauthMenu:
    def __init__(self):
        self.info = "Perform deauthentication attacks here."

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'back'

    def update(self):
        pass

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        surf = font.render("Deauth Attack", True, config.COLORS['accent'])
        surface.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH//2, 40)))
        info_font = pygame.font.SysFont(config.FONT_NAME, 28)
        info_surf = info_font.render(self.info, True, config.COLORS['text'])
        surface.blit(info_surf, info_surf.get_rect(center=(config.SCREEN_WIDTH//2, 150)))

class CrackMenu:
    def __init__(self):
        self.info = "Crack captured handshakes here."

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'back'

    def update(self):
        pass

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        surf = font.render("Crack Handshake", True, config.COLORS['accent'])
        surface.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH//2, 40)))
        info_font = pygame.font.SysFont(config.FONT_NAME, 28)
        info_surf = info_font.render(self.info, True, config.COLORS['text'])
        surface.blit(info_surf, info_surf.get_rect(center=(config.SCREEN_WIDTH//2, 150)))

class MonitorMenu:
    def __init__(self):
        self.info = "Enable/disable monitor mode here."

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'back'

    def update(self):
        pass

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        surf = font.render("Monitor Mode", True, config.COLORS['accent'])
        surface.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH//2, 40)))
        info_font = pygame.font.SysFont(config.FONT_NAME, 28)
        info_surf = info_font.render(self.info, True, config.COLORS['text'])
        surface.blit(info_surf, info_surf.get_rect(center=(config.SCREEN_WIDTH//2, 150)))

class SavedMenu:
    def __init__(self):
        self.info = "View and manage saved captures here."

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'back'

    def update(self):
        pass

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        surf = font.render("Saved Captures", True, config.COLORS['accent'])
        surface.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH//2, 40)))
        info_font = pygame.font.SysFont(config.FONT_NAME, 28)
        info_surf = info_font.render(self.info, True, config.COLORS['text'])
        surface.blit(info_surf, info_surf.get_rect(center=(config.SCREEN_WIDTH//2, 150)))


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
