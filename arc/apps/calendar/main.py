import pygame
import sys
import os
import calendar
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from arc.core import config
from arc.core.ui_elements import *

# --- Config helpers ---
def c(name, default=(240,240,240)):
    return getattr(config.colors, name, default)

def fnt(size=None):
    return pygame.font.SysFont(getattr(config.font, "name", "Arial"), size or getattr(config.font, "size", 18))

def s(name, default=480):
    return getattr(config.screen, name, default)

def fps():
    return getattr(config, "fps", 30)

def accent():
    return getattr(config, "accent_color", c("accent", (100,100,240)))

# --- Main Calendar Class ---
class CalendarApp:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = s("width", 480), s("height", 320)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption('Calendar App')
        self.clock = pygame.time.Clock()
        self.FPS = fps()
        # Fonts
        self.title_font = fnt(24)
        self.weekday_font = fnt(18)
        self.day_font = fnt(16)
        self.arrow_font = fnt(28)
        # Colors
        self.BACKGROUND = c("background", (34,40,48))
        self.TEXT = c("text", (220,220,220))
        self.ACCENT = accent()
        # Layout
        self.HEADER_HEIGHT = 40
        self.WEEKDAY_HEIGHT = 20
        self.CAL_TOP = self.HEADER_HEIGHT + self.WEEKDAY_HEIGHT
        self.CELL_WIDTH = self.WIDTH / 7
        self.CELL_HEIGHT = (self.HEIGHT - self.CAL_TOP) / 6
        self.LEFT_ARROW_RECT = pygame.Rect(10, 10, 24, 24)
        self.RIGHT_ARROW_RECT = pygame.Rect(self.WIDTH - 34, 10, 24, 24)
        # Calendar state
        now = datetime.now()
        self.year = now.year
        self.month = now.month

    def draw(self):
        self.screen.fill(self.BACKGROUND)
        now = datetime.now()
        today = (now.day, now.month, now.year)
        # Title
        title_surf = self.title_font.render(f"{calendar.month_name[self.month]} {self.year}", True, self.TEXT)
        title_rect = title_surf.get_rect(center=(self.WIDTH // 2, self.HEADER_HEIGHT // 2))
        self.screen.blit(title_surf, title_rect)
        # Arrows
        left_surf = self.arrow_font.render('<', True, self.TEXT)
        right_surf = self.arrow_font.render('>', True, self.TEXT)
        self.screen.blit(left_surf, self.LEFT_ARROW_RECT.topleft)
        self.screen.blit(right_surf, self.RIGHT_ARROW_RECT.topleft)
        # Weekdays
        for idx, day_name in enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']):
            x = idx * self.CELL_WIDTH + self.CELL_WIDTH / 2
            y = self.HEADER_HEIGHT + self.WEEKDAY_HEIGHT / 2
            day_surf = self.weekday_font.render(day_name, True, self.TEXT)
            day_rect = day_surf.get_rect(center=(x, y))
            self.screen.blit(day_surf, day_rect)
        # Days
        month_matrix = calendar.monthcalendar(self.year, self.month)
        for row_idx, week in enumerate(month_matrix):
            for col_idx, day in enumerate(week):
                if day == 0: continue
                x = col_idx * self.CELL_WIDTH + self.CELL_WIDTH / 2
                y = self.CAL_TOP + row_idx * self.CELL_HEIGHT + self.CELL_HEIGHT / 2
                is_today = (day, self.month, self.year) == today
                if is_today:
                    radius = int(min(self.CELL_WIDTH, self.CELL_HEIGHT) / 2 - 4)
                    pygame.draw.circle(self.screen, self.ACCENT, (int(x), int(y)), radius)
                    day_text = self.day_font.render(str(day), True, self.BACKGROUND)
                else:
                    day_text = self.day_font.render(str(day), True, self.TEXT)
                day_rect = day_text.get_rect(center=(x, y))
                self.screen.blit(day_text, day_rect)
        pygame.display.flip()

    def prev_month(self):
        if self.month == 1:
            self.month, self.year = 12, self.year - 1
        else:
            self.month -= 1

    def next_month(self):
        if self.month == 12:
            self.month, self.year = 1, self.year + 1
        else:
            self.month += 1

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.prev_month()
                    elif event.key == pygame.K_RIGHT:
                        self.next_month()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.LEFT_ARROW_RECT.collidepoint(event.pos):
                        self.prev_month()
                    elif self.RIGHT_ARROW_RECT.collidepoint(event.pos):
                        self.next_month()
            self.draw()
            self.clock.tick(30)
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    CalendarApp().run()
