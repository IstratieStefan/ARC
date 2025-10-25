import pygame
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from arc.core.ui_elements import ScrollableList

class MainMenu:
    OPTIONS = ["Songs", "Albums", "Artists", "Now Playing"]

    def __init__(self, fonts, colors, screen):
        self.screen = screen
        self.font_item = fonts[1]
        self.C_TEXT, self.C_ACCENT = colors[2], colors[3]

        # Determine list area: full width, starting 30% down
        w, h = screen.get_size()
        line_h = 40
        list_height = len(self.OPTIONS) * line_h
        list_y = 5
        rect = (5, list_y, w - 10, list_height)

        # Instantiate ScrollableList without a callback
        self.list = ScrollableList(
            items=self.OPTIONS,
            rect=rect,
            font=self.font_item,
            line_height=line_h,
            text_color=self.C_TEXT,
            bg_color=(255, 255, 255),
            sel_color=self.C_ACCENT
        )

    def handle_event(self, ev):
        """
        Forward event to the scrollable list and
        return the selected option on Enter.
        """
        self.list.handle_event(ev)
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
            idx = self.list.selected_index
            return self.OPTIONS[idx]
        return None

    def update(self):
        """Update hover state."""
        self.list.update()

    def draw(self):
        """Draw the menu on screen."""
        self.screen.fill((255, 255, 255))
        self.list.draw(self.screen)
