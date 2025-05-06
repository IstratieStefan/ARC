import pygame
import config
import time
import os
import glob

class Button:
    def __init__(self, text, rect, callback):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.callback = callback
        self.font = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE)
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def draw(self, surface):
        color = config.COLORS['button_hover'] if self.hovered else config.COLORS['button']
        pygame.draw.rect(surface, color, self.rect, border_radius=config.RADIUS['button'])
        txt_surf = self.font.render(self.text, True, config.COLORS['text_light'])
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)


class WarningMessage:
    def __init__(self, text):
        self.text = text
        self.font = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE)
        self.start_time = 0
        self.visible = False

    def show(self):
        self.start_time = pygame.time.get_ticks()
        self.visible = True

    def update(self):
        if self.visible and pygame.time.get_ticks() - self.start_time > config.WARNING_DURATION:
            self.visible = False

    def draw(self, surface):
        if not self.visible:
            return
        txt_surf = self.font.render(self.text, True, config.COLORS['warning_text'])
        padding = 10
        bg_rect = txt_surf.get_rect()
        bg_rect.inflate_ip(padding * 2, padding * 2)
        bg_rect.midtop = (config.SCREEN_WIDTH // 2, 10)
        pygame.draw.rect(surface, config.COLORS['warning_bg'], bg_rect, border_radius=config.RADIUS['warning'])
        surface.blit(txt_surf, (bg_rect.x + padding, bg_rect.y + padding))


class Tab:
    def __init__(self, name, index):
        self.name = name
        self.index = index
        x = config.TAB_MARGIN
        y = config.TAB_MARGIN + index * (config.TAB_HEIGHT + config.TAB_MARGIN)
        self.base_y = y
        self.rect = pygame.Rect(x, y, config.TAB_WIDTH, config.TAB_HEIGHT)
        self.font = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE)

    def draw(self, surface, y_offset, active=False):
        rect = self.rect.copy()
        rect.y = y_offset
        color = config.COLORS['tab_active'] if active else config.COLORS['tab_bg']
        pygame.draw.rect(surface, color, rect, border_radius=config.RADIUS['tab'])
        txt_surf = self.font.render(self.name, True, config.COLORS['text'])
        txt_rect = txt_surf.get_rect(center=rect.center)
        surface.blit(txt_surf, txt_rect)


class TabManager:
    def __init__(self, tab_names):
        self.tabs = [Tab(name, i) for i, name in enumerate(tab_names)]
        self.active = 0
        self.first_visible = 0
        # how many tabs fit vertically
        self.visible_count = max(1, config.SCREEN_HEIGHT // (config.TAB_HEIGHT + config.TAB_MARGIN))

    def handle_event(self, event):
        # click to switch
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, tab in enumerate(self.tabs[self.first_visible:self.first_visible + self.visible_count]):
                if tab.rect.move(0, -(self.tabs[self.first_visible].base_y - tab.base_y)).collidepoint(event.pos):
                    self.active = self.first_visible + i
                    break
        # scroll tabs
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
            self.first_visible = max(0, self.first_visible - 1)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
            max_first = max(0, len(self.tabs) - self.visible_count)
            self.first_visible = min(max_first, self.first_visible + 1)

    def update_visible(self):
        if self.active < self.first_visible:
            self.first_visible = self.active
        elif self.active >= self.first_visible + self.visible_count:
            self.first_visible = self.active - self.visible_count + 1

    def draw(self, surface):
        # ensure active is visible
        self.update_visible()
        # draw visible tabs
        start_y = config.TAB_MARGIN
        #for tab in self.tabs[self.first_visible:self.first_visible + self.visible_count]:
         #   y_offset = start_y + (config.TAB_HEIGHT + config.TAB_MARGIN) * (tab.index - self.first_visible)
          #  tab.draw(surface, y_offset, active=(tab.index == self.active))

        n = len(self.tabs)
        r = config.INDICATOR_RADIUS
        s = config.INDICATOR_SPACING
        total_h = n * 2 * r + (n - 1) * s
        start_y = config.SCREEN_HEIGHT / 2 - total_h / 2
        x = config.SCREEN_WIDTH - config.TAB_MARGIN - r - 5
        for i in range(n):
            y = start_y + i * (2 * r + s)
            color = config.COLORS['indicator_active'] if i == self.active else config.COLORS['indicator']
            pygame.draw.circle(surface, color, (x, y), r)

    def get_active_index(self):
        return self.active


class MessageBox:
    def __init__(self, text, yes_callback, no_callback):
        self.text = text
        self.yes_callback = yes_callback
        self.no_callback = no_callback
        self.font = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE)
        self.visible = False
        # calculate box dimensions
        self.width = config.SCREEN_WIDTH * 0.6
        self.height = config.SCREEN_HEIGHT * 0.4
        btn_w, btn_h = 80, 40
        x0 = (config.SCREEN_WIDTH - btn_w * 2 - config.TAB_MARGIN) // 2
        y0 = (config.SCREEN_HEIGHT + self.height) // 2 - btn_h - 20
        self.btn_yes = Button('Yes', (x0, y0, btn_w, btn_h), self._on_yes)
        self.btn_no = Button('No', (x0 + btn_w + config.TAB_MARGIN, y0, btn_w, btn_h), self._on_no)

    def show(self):
        self.visible = True

    def _on_yes(self):
        self.visible = False
        self.yes_callback()

    def _on_no(self):
        self.visible = False
        self.no_callback()

    def handle_event(self, event):
        if not self.visible:
            return
        self.btn_yes.handle_event(event)
        self.btn_no.handle_event(event)

    def draw(self, surface):
        if not self.visible:
            return
        # dark overlay
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))
        # modal box
        rect = pygame.Rect((config.SCREEN_WIDTH - self.width) // 2,
                           (config.SCREEN_HEIGHT - self.height) // 2,
                           self.width, self.height)
        pygame.draw.rect(surface, config.COLORS['tab_bg'], rect, border_radius=config.RADIUS['modal'])
        # text
        txt_surf = self.font.render(self.text, True, config.COLORS['text'])
        txt_rect = txt_surf.get_rect(center=(config.SCREEN_WIDTH // 2, rect.y + 30))
        surface.blit(txt_surf, txt_rect)
        # buttons
        self.btn_yes.draw(surface)
        self.btn_no.draw(surface)

class SearchBox:
    def __init__(self, rect, placeholder="", callback=None):
        self.rect = pygame.Rect(rect)
        self.placeholder = placeholder
        self.callback = callback
        self.font = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE)
        self.text = ""
        self.active = False
        self.cursor_visible = True
        self.last_toggle = time.time()
        self.cursor_pos = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if not self.active:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
            elif event.key == pygame.K_RETURN:
                if self.callback:
                    self.callback(self.text)
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos-1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos+1)
            else:
                char = event.unicode
                if char and char.isprintable():
                    self.text = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
                    self.cursor_pos += 1

    def update(self):
        if time.time() - self.last_toggle > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.last_toggle = time.time()

    def draw(self, surface):
        # background
        pygame.draw.rect(surface, config.COLORS['input_bg'], self.rect, border_radius=config.RADIUS['input'])
        # border
        color = config.COLORS['input_border'] if self.active else config.COLORS['tab_bg']
        pygame.draw.rect(surface, color, self.rect, width=2, border_radius=config.RADIUS['input'])
        # text
        txt = self.text if self.text else self.placeholder
        txt_color = config.COLORS['input_text'] if self.text else config.COLORS['input_placeholder']
        txt_surf = self.font.render(txt, True, txt_color)
        surface.blit(txt_surf, (self.rect.x+8, self.rect.y + (self.rect.height-txt_surf.get_height())//2))
        # cursor
        if self.active and self.cursor_visible:
            # compute cursor x
            sub = self.font.render(self.text[:self.cursor_pos], True, config.COLORS['input_text'])
            cx = self.rect.x + 8 + sub.get_width()
            cy_top = self.rect.y + (self.rect.height - self.font.get_height())//2
            cy_bot = cy_top + self.font.get_height()
            pygame.draw.line(surface, config.COLORS['input_text'], (cx, cy_top), (cx, cy_bot), 2)

class AppIcon(Button):
    @staticmethod
    def get_shell_commands(icon_fallback):
        seen = set()
        apps = []
        for d in os.environ.get('.PATH', '').split(':'):
            for path in glob.glob(os.path.join(d, '*')):
                if os.access(path, os.X_OK) and not os.path.isdir(path):
                    name = os.path.basename(path)
                    if name in seen:
                        continue
                    seen.add(name)
                    apps.append((name, name, icon_fallback))
        return sorted(apps, key=lambda x: x[0].lower())

    def __init__(self, name, icon_path, rect, callback):
        super().__init__(name, rect, callback)
        try:
            img = pygame.image.load(icon_path).convert_alpha()
        except Exception:
            img = pygame.Surface((self.rect.width - 15,
                                  self.rect.height - 15),
                                  pygame.SRCALPHA)
        self.icon = pygame.transform.smoothscale(
            img,
            (self.rect.width - 15, self.rect.height - 15)
        )

    def draw(self, surface):
        # draw background cell
        bg_color = (config.COLORS['cell_active']
                    if self.hovered else config.COLORS['cell_bg'])
        pygame.draw.rect(surface, bg_color, self.rect,
                         border_radius=config.RADIUS['app_icon'])
        border_color = config.COLORS['accent']

        # if hovered, draw a cycling-rainbow border
        if self.hovered:
            border_color = getattr(
                config, "ACCENT_COLOR",
                config.COLORS.get("accent", (255, 255, 255))
            )
            outline_w = 3
            outer = self.rect.inflate(outline_w * 2, outline_w * 2)
            outer_radius = config.RADIUS['app_icon'] + outline_w
            pygame.draw.rect(
                surface,
                border_color,
                outer,
                width=outline_w,
                border_radius=outer_radius
            )

        # blit icon (centered)
        ir = self.icon.get_rect()
        ir.centerx = self.rect.centerx
        ir.y = self.rect.y + 5
        surface.blit(self.icon, ir)

        # draw text only for hovered icon at bottom center of screen
        if self.hovered:
            hover_font = pygame.font.SysFont('Arial', config.FONT_SIZE + 6)
            text_surf = hover_font.render(self.text, True, config.COLORS['text'])
            text_rect = text_surf.get_rect()
            sw, sh = surface.get_size()
            text_rect.centerx = sw // 2
            text_rect.centery = sh - (text_surf.get_height() // 2) - 15
            surface.blit(text_surf, text_rect)