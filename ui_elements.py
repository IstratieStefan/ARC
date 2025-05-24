import pygame
import subprocess
from config import config
import time
import os
import glob

class Button:
    def __init__(self, text, rect, callback):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.callback = callback
        self.font = pygame.font.SysFont(config.font.name, config.font.size)
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def draw(self, surface):
        color = config.colors.button_hover if self.hovered else config.colors.button
        pygame.draw.rect(surface, color, self.rect, border_radius=config.radius.button)
        txt_surf = self.font.render(self.text, True, config.colors.text_light)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)


class WarningMessage:
    def __init__(self, text):
        self.text = text
        self.font = pygame.font.SysFont(config.font.name, config.font.size)
        self.start_time = 0
        self.visible = False

    def show(self):
        self.start_time = pygame.time.get_ticks()
        self.visible = True

    def update(self):
        if self.visible and pygame.time.get_ticks() - self.start_time > config.warning_duration:
            self.visible = False

    def draw(self, surface):
        if not self.visible:
            return
        txt_surf = self.font.render(self.text, True, config.colors.warning_text)
        padding = 10
        bg_rect = txt_surf.get_rect()
        bg_rect.inflate_ip(padding * 2, padding * 2)
        bg_rect.midtop = (config.screen.width // 2, 10)
        pygame.draw.rect(surface, config.colors.warning_bg, bg_rect, border_radius=config.radius.warning)
        surface.blit(txt_surf, (bg_rect.x + padding, bg_rect.y + padding))


class Tab:
    def __init__(self, name, index):
        self.name = name
        self.index = index
        x = config.tab.margin
        y = config.tab.margin + index * (config.tab.height + config.tab.margin)
        self.base_y = y
        self.rect = pygame.Rect(x, y, config.tab.width, config.tab.height)
        self.font = pygame.font.SysFont(config.font.name, config.font.size)

    def draw(self, surface, y_offset, active=False):
        rect = self.rect.copy()
        rect.y = y_offset
        color = config.colors.tab_active if active else config.colors.tab_bg
        pygame.draw.rect(surface, color, rect, border_radius=config.radius.tab)
        txt_surf = self.font.render(self.name, True, config.colors.text)
        txt_rect = txt_surf.get_rect(center=rect.center)
        surface.blit(txt_surf, txt_rect)


class TabManager:
    def __init__(self, tab_names):
        # Defensive: fallback if config values are missing or None
        tab_height = getattr(getattr(config, "tab", {}), "height", 40) or 40
        tab_margin = getattr(getattr(config, "tab", {}), "margin", 5) or 5
        screen_height = getattr(getattr(config, "screen", {}), "height", 320) or 320

        self.tabs = [Tab(name, i) for i, name in enumerate(tab_names)]
        self.active = 0
        self.first_visible = 0
        self.visible_count = max(1, screen_height // (tab_height + tab_margin))

    def handle_event(self, event):
        tab_height = getattr(getattr(config, "tab", {}), "height", 40) or 40
        tab_margin = getattr(getattr(config, "tab", {}), "margin", 5) or 5

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, tab in enumerate(self.tabs[self.first_visible:self.first_visible + self.visible_count]):
                if tab.rect.move(0, -(self.tabs[self.first_visible].base_y - tab.base_y)).collidepoint(event.pos):
                    self.active = self.first_visible + i
                    break
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
        # Defensive: fallback to defaults
        screen_height = getattr(getattr(config, "screen", {}), "height", 320) or 320
        screen_width  = getattr(getattr(config, "screen", {}), "width", 480) or 480
        tab_margin    = getattr(getattr(config, "tab", {}), "margin", 5) or 5
        indicator     = getattr(config, "indicator", {})
        r = getattr(indicator, "radius", 4) or 4
        s = getattr(indicator, "spacing", 10) or 10

        self.update_visible()
        n = len(self.tabs)

        total_h = n * 2 * r + (n - 1) * s
        start_y = screen_height / 2 - total_h / 2
        x = screen_width - tab_margin - r - 5

        # Robust color fetching
        colors = getattr(config, "colors", {})
        color_indicator      = getattr(colors, "indicator", (180, 180, 180))
        color_indicator_actv = getattr(colors, "indicator_active", (255, 255, 255))

        for i in range(n):
            y = start_y + i * (2 * r + s)
            color = color_indicator_actv if i == self.active else color_indicator
            pygame.draw.circle(surface, color, (x, int(y)), r)

    def get_active_index(self):
        return self.active

class MessageBox:
    def __init__(self, text, yes_callback, no_callback):
        # Defensive config values
        font_obj   = getattr(config, "font", None)
        screen     = getattr(config, "screen", None)
        tab        = getattr(config, "tab", None)
        colors     = getattr(config, "colors", {})
        radius     = getattr(config, "radius", {})

        font_name  = getattr(font_obj, "name", None) or "Arial"
        font_size  = getattr(font_obj, "size", None) or 20
        screen_w   = getattr(screen, "width", 480)
        screen_h   = getattr(screen, "height", 320)
        tab_margin = getattr(tab, "margin", 5)
        tab_bg     = getattr(colors, "tab_bg", (50, 50, 50))
        text_col   = getattr(colors, "text", (220, 220, 220))
        modal_rad  = getattr(radius, "modal", 6)

        self.text = text
        self.yes_callback = yes_callback
        self.no_callback = no_callback
        self.font = pygame.font.SysFont(font_name, font_size)
        self.visible = False
        # calculate box dimensions
        self.width = screen_w * 0.6
        self.height = screen_h * 0.4
        btn_w, btn_h = 80, 40
        x0 = int((screen_w - btn_w * 2 - tab_margin) // 2)
        y0 = int((screen_h + self.height) // 2 - btn_h - 20)
        self.btn_yes = Button('Yes', (x0, y0, btn_w, btn_h), self._on_yes)
        self.btn_no = Button('No', (x0 + btn_w + tab_margin, y0, btn_w, btn_h), self._on_no)
        # cache for draw
        self._draw_params = (screen_w, screen_h, tab_bg, modal_rad, text_col)

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
        screen_w, screen_h, tab_bg, modal_rad, text_col = self._draw_params
        # dark overlay
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))
        # modal box
        rect = pygame.Rect((screen_w - self.width) // 2,
                           (screen_h - self.height) // 2,
                           self.width, self.height)
        pygame.draw.rect(surface, tab_bg, rect, border_radius=modal_rad)
        # text
        txt_surf = self.font.render(self.text, True, text_col)
        txt_rect = txt_surf.get_rect(center=(screen_w // 2, rect.y + 30))
        surface.blit(txt_surf, txt_rect)
        # buttons
        self.btn_yes.draw(surface)
        self.btn_no.draw(surface)

class SearchBox:
    def __init__(self, rect, placeholder="", callback=None):
        # Defensive config values
        font_obj   = getattr(config, "font", None)
        colors     = getattr(config, "colors", {})
        radius     = getattr(config, "radius", {})

        font_name  = getattr(font_obj, "name", None) or "Arial"
        font_size  = getattr(font_obj, "size", None) or 20
        input_bg   = getattr(colors, "input_bg", (255, 255, 255))
        input_border = getattr(colors, "input_border", (100, 100, 100))
        tab_bg     = getattr(colors, "tab_bg", (50, 50, 50))
        input_text = getattr(colors, "input_text", (0, 0, 0))
        input_placeholder = getattr(colors, "input_placeholder", (150, 150, 150))
        input_rad  = getattr(radius, "input", 6)

        self.rect = pygame.Rect(rect)
        self.placeholder = placeholder
        self.callback = callback
        self.font = pygame.font.SysFont(font_name, font_size)
        self.text = ""
        self.active = False
        self.cursor_visible = True
        self.last_toggle = time.time()
        self.cursor_pos = 0

        # cache for draw
        self._draw_params = (input_bg, input_border, tab_bg, input_text, input_placeholder, input_rad)

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
        input_bg, input_border, tab_bg, input_text, input_placeholder, input_rad = self._draw_params
        # background
        pygame.draw.rect(surface, input_bg, self.rect, border_radius=input_rad)
        # border
        color = input_border if self.active else tab_bg
        pygame.draw.rect(surface, color, self.rect, width=2, border_radius=input_rad)
        # text
        txt = self.text if self.text else self.placeholder
        txt_color = input_text if self.text else input_placeholder
        txt_surf = self.font.render(txt, True, txt_color)
        surface.blit(txt_surf, (self.rect.x+8, self.rect.y + (self.rect.height-txt_surf.get_height())//2))
        # cursor
        if self.active and self.cursor_visible:
            sub = self.font.render(self.text[:self.cursor_pos], True, input_text)
            cx = self.rect.x + 8 + sub.get_width()
            cy_top = self.rect.y + (self.rect.height - self.font.get_height())//2
            cy_bot = cy_top + self.font.get_height()
            pygame.draw.line(surface, input_text, (cx, cy_top), (cx, cy_bot), 2)


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
        # Get config values safely
        colors = getattr(config, "colors", {})
        radius = getattr(config, "radius", {})
        accent_color = getattr(config, "accent_color", (255, 255, 255))
        font_obj = getattr(config, "font", None)
        font_size = getattr(font_obj, "size", None) or 20

        self.bg_active = getattr(colors, "cell_active", (240, 240, 240))
        self.bg_idle = getattr(colors, "cell_bg", (220, 220, 220))
        self.border_radius = getattr(radius, "app_icon", 15)
        self.border_color = getattr(colors, "accent", accent_color)
        self.text_color = getattr(colors, "text", (220, 220, 220))

        self.icon_path = icon_path
        print(f"AppIcon: Attempting to load '{icon_path}' for '{name}'")
        if not os.path.isfile(icon_path):
            print(f"AppIcon WARNING: File does not exist: {icon_path}")
        try:
            img = pygame.image.load(icon_path).convert_alpha()
        except Exception as e:
            print(f"AppIcon: Failed to load icon '{icon_path}' for '{name}'. Error: {e}")
            img = pygame.Surface((self.rect.width - 25,
                                  self.rect.height - 25),
                                  pygame.SRCALPHA)
            img.fill((255, 0, 0))  # Bright red for missing
        self.icon = pygame.transform.smoothscale(
            img,
            (self.rect.width - 25, self.rect.height - 25)
        )
        self._font_size = font_size

    def draw(self, surface):
        # draw background cell
        bg_color = self.bg_active if self.hovered else self.bg_idle
        pygame.draw.rect(surface, bg_color, self.rect,
                         border_radius=self.border_radius)
        border_color = self.border_color

        # if hovered, draw a colored border
        if self.hovered:
            border_color = getattr(config, "accent_color", self.border_color)
            outline_w = 3
            outer = self.rect.inflate(outline_w * 2, outline_w * 2)
            outer_radius = self.border_radius + outline_w
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
        ir.y = self.rect.y + 12
        surface.blit(self.icon, ir)

        # draw text only for hovered icon at bottom center of screen
        if self.hovered:
            font_name = getattr(getattr(config, "font", None), "name", "Arial")
            hover_font = pygame.font.SysFont(font_name, self._font_size + 6)
            text_surf = hover_font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect()
            sw, sh = surface.get_size()
            text_rect.centerx = sw // 2
            text_rect.centery = sh - (text_surf.get_height() // 2) - 15
            surface.blit(text_surf, text_rect)



class Slider:
    def __init__(self, rect, min_val, max_val, init_val, callback=None):
        self.rect      = pygame.Rect(rect)
        self.min_val   = min_val
        self.max_val   = max_val
        self.callback  = callback
        self.knob_w    = 12
        self.knob_h    = self.rect.height + 4
        self.value     = max(min_val, min(max_val, init_val))
        self._update_knob_x()
        self.dragging  = False

        # Robust YAML config
        colors = getattr(config, "colors", None)
        radius = getattr(config, "radius", None)
        self.slider_bg   = getattr(colors, "slider_bg", (80, 80, 80))
        self.slider_fill = getattr(colors, "slider_fill", (50, 150, 250))
        self.knob_col    = getattr(colors, "slider_knob", (200, 200, 200))
        self.knob_active = getattr(colors, "slider_active_knob", (255, 255, 255))
        self.bar_radius  = getattr(radius, "slider", 4)
        self.knob_radius = getattr(radius, "slider_knob", 6)

    def _update_knob_x(self):
        pct = (self.value - self.min_val) / (self.max_val - self.min_val)
        bar_x0 = self.rect.x
        bar_x1 = self.rect.x + self.rect.width
        self.knob_x = int(bar_x0 + pct * (bar_x1 - bar_x0))
        self.knob_rect = pygame.Rect(
            self.knob_x - self.knob_w // 2,
            self.rect.y - (self.knob_h - self.rect.height) // 2,
            self.knob_w,
            self.knob_h
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.knob_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mx = event.pos[0]
            bar_x0 = self.rect.x
            bar_x1 = self.rect.x + self.rect.width
            pct = (mx - bar_x0) / (bar_x1 - bar_x0)
            pct = max(0.0, min(1.0, pct))
            new_val = self.min_val + pct * (self.max_val - self.min_val)
            if new_val != self.value:
                self.value = new_val
                self._update_knob_x()
                if self.callback:
                    self.callback(self.value)

    def draw(self, surface):
        # draw bar
        pygame.draw.rect(surface, self.slider_bg, self.rect, border_radius=self.bar_radius)
        # draw fill up to knob
        filled = pygame.Rect(self.rect.x, self.rect.y, self.knob_x - self.rect.x, self.rect.height)
        pygame.draw.rect(surface, self.slider_fill, filled, border_radius=self.bar_radius)
        # draw knob
        col = self.knob_active if self.dragging else self.knob_col
        pygame.draw.rect(surface, col, self.knob_rect, border_radius=self.knob_radius)


class ScrollableList:
    def __init__(self, items, rect, font, line_height,
                 text_color, bg_color, sel_color, callback=None,
                 icons=None, icon_size=(24, 24), icon_padding=5):
        """
        items       – list of strings
        rect        – (x,y,w,h) for the list area
        font        – a pygame.Font instance
        line_height – pixel height per line (>= font.get_linesize())
        text_color  – color for normal entries
        bg_color    – list background color
        sel_color   – highlight color for borders on selected entry
        callback    – fn(item_text) on click or Enter
        icons       – optional list of pygame.Surface objects or None
        icon_size   – (w, h) to scale each icon
        icon_padding– space between icon and right edge
        """
        self.items          = items
        self.rect           = pygame.Rect(rect)
        self.font           = font
        self.line_h         = line_height
        self.text_color     = text_color
        self.bg_color       = bg_color
        self.sel_color      = sel_color
        self.callback       = callback
        self.icons          = icons if icons else [None] * len(items)
        self.icon_size      = icon_size
        self.icon_padding   = icon_padding

        # control whether list accepts input
        self.enabled        = True
        # internal scroll offset in pixels
        self.offset_y       = 0
        # which index is currently under the mouse
        self.hover_index    = None
        # which index is selected by keyboard
        self.selected_index = 0

        # max scroll so last item lines up at bottom
        self.max_offset = max(0, len(self.items) * self.line_h - self.rect.height)

    def set_enabled(self, enabled: bool):
        """Enable or disable interaction."""
        self.enabled = enabled
        if not enabled:
            self.hover_index = None

    def _ensure_visible(self):
        """Adjust offset_y so selected_index is in view."""
        top = self.selected_index * self.line_h
        bottom = top + self.line_h
        if top < self.offset_y:
            self.offset_y = top
        elif bottom > self.offset_y + self.rect.height:
            self.offset_y = bottom - self.rect.height
        # clamp
        self.offset_y = max(0, min(self.offset_y, self.max_offset))

    def handle_event(self, event):
        if not self.enabled:
            return
        # Mouse click or wheel
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                rel_y = event.pos[1] - self.rect.y + self.offset_y
                idx = rel_y // self.line_h
                if 0 <= idx < len(self.items):
                    self.selected_index = idx
                    self._ensure_visible()
                    if self.callback:
                        self.callback(self.items[idx])
        elif event.type == pygame.MOUSEWHEEL:
            self.offset_y = min(
                max(0, self.offset_y - event.y * self.line_h),
                self.max_offset
            )

        # Keyboard navigation
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if self.selected_index < len(self.items) - 1:
                    self.selected_index += 1
                    self._ensure_visible()
            elif event.key == pygame.K_UP:
                if self.selected_index > 0:
                    self.selected_index -= 1
                    self._ensure_visible()
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if 0 <= self.selected_index < len(self.items) and self.callback:
                    self.callback(self.items[self.selected_index])

    def update(self):
        # update hover state only if enabled
        if not self.enabled:
            return
        mx, my = pygame.mouse.get_pos()
        if self.rect.collidepoint(mx, my):
            rel_y = my - self.rect.y + self.offset_y
            idx = rel_y // self.line_h
            self.hover_index = idx if 0 <= idx < len(self.items) else None
        else:
            self.hover_index = None

    def draw(self, surface):
        # draw background
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=4)
        # clip to list area
        old_clip = surface.get_clip()
        surface.set_clip(self.rect)

        x, y0 = self.rect.x, self.rect.y
        text_right = self.rect.x + self.rect.width
        for i, text in enumerate(self.items):
            y = y0 + i * self.line_h - self.offset_y
            # hover highlight fill
            if self.enabled and self.hover_index == i:
                pygame.draw.rect(surface, self.sel_color,
                                 (x, y, self.rect.width, self.line_h), border_radius=4)
            # render text
            txt_surf = self.font.render(text, True, self.text_color)
            surface.blit(
                txt_surf,
                (x + 5, y + (self.line_h - txt_surf.get_height()) // 2)
            )
            # draw icon if present
            if i < len(self.icons) and self.icons[i]:
                icon_surf = pygame.transform.smoothscale(self.icons[i], self.icon_size)
                ix = text_right - self.icon_size[0] - self.icon_padding
                iy = y + (self.line_h - self.icon_size[1]) // 2
                surface.blit(icon_surf, (ix, iy))
            # draw selection border
            if i == self.selected_index:
                border_rect = pygame.Rect(x, y, self.rect.width, self.line_h)
                pygame.draw.rect(surface, self.sel_color, border_rect, 2, border_radius=4)

        surface.set_clip(old_clip)