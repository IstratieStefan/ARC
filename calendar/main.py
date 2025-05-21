import pygame
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import calendar
import config
from datetime import datetime

pygame.init()

WIDTH, HEIGHT = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
FPS = config.FPS
FONT_NAME = None

# Colors
BACKGROUND = config.COLORS['background']
TEXT = config.COLORS['text']
ACCENT = config.ACCENT_COLOR
GRAY = (200, 200, 200)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Calendar App')
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.Font(FONT_NAME, 24)
weekday_font = pygame.font.Font(FONT_NAME, 18)
day_font = pygame.font.Font(FONT_NAME, 16)
arrow_font = pygame.font.Font(FONT_NAME, 28)

# Calendar state
now = datetime.now()
year = now.year
month = now.month

# Layout
HEADER_HEIGHT = 40
WEEKDAY_HEIGHT = 20
CAL_TOP = HEADER_HEIGHT + WEEKDAY_HEIGHT
CELL_WIDTH = WIDTH / 7
CELL_HEIGHT = (HEIGHT - CAL_TOP) / 6

# Arrow areas for mouse
LEFT_ARROW_RECT = pygame.Rect(10, 10, 20, 20)
RIGHT_ARROW_RECT = pygame.Rect(WIDTH - 30, 10, 20, 20)


def draw():
    screen.fill(BACKGROUND)

    # Get current date
    now = datetime.now()
    today_day = now.day
    today_month = now.month
    today_year = now.year

    # Draw month/year title
    title_surf = title_font.render(f"{calendar.month_name[month]} {year}", True, TEXT)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, HEADER_HEIGHT // 2))
    screen.blit(title_surf, title_rect)

    # Draw navigation arrows
    left_surf = arrow_font.render('<', True, TEXT)
    right_surf = arrow_font.render('>', True, TEXT)
    screen.blit(left_surf, LEFT_ARROW_RECT.topleft)
    screen.blit(right_surf, RIGHT_ARROW_RECT.topleft)

    # Draw weekday headers
    for idx, day_name in enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']):
        x = idx * CELL_WIDTH + CELL_WIDTH / 2
        y = HEADER_HEIGHT + WEEKDAY_HEIGHT / 2
        day_surf = weekday_font.render(day_name, True, TEXT)
        day_rect = day_surf.get_rect(center=(x, y))
        screen.blit(day_surf, day_rect)

    # Draw days
    month_matrix = calendar.monthcalendar(year, month)
    for row_idx, week in enumerate(month_matrix):
        for col_idx, day in enumerate(week):
            if day != 0:
                x = col_idx * CELL_WIDTH + CELL_WIDTH / 2
                y = CAL_TOP + row_idx * CELL_HEIGHT + CELL_HEIGHT / 2

                # Highlight today's date
                if day == today_day and month == today_month and year == today_year:
                    radius = int(min(CELL_WIDTH, CELL_HEIGHT) / 2 - 4)
                    pygame.draw.circle(screen, ACCENT, (int(x), int(y)), radius)
                    day_text = day_font.render(str(day), True, BACKGROUND)
                else:
                    day_text = day_font.render(str(day), True, TEXT)

                day_rect = day_text.get_rect(center=(x, y))
                screen.blit(day_text, day_rect)

    pygame.display.flip()


def prev_month():
    global month, year
    if month == 1:
        month = 12
        year -= 1
    else:
        month -= 1


def next_month():
    global month, year
    if month == 12:
        month = 1
        year += 1
    else:
        month += 1


def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    prev_month()
                elif event.key == pygame.K_RIGHT:
                    next_month()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if LEFT_ARROW_RECT.collidepoint(event.pos):
                    prev_month()
                elif RIGHT_ARROW_RECT.collidepoint(event.pos):
                    next_month()

        draw()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
