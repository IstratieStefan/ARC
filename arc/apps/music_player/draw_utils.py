import pygame
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import math

def draw_page_dots(screen, rect, current_page, total_pages, accent, bg):
    if total_pages <= 1:
        return
    dot_r, spacing, padding = 4, 12, 6
    total_h = total_pages * spacing + padding*2 - 4
    total_w = dot_r*2 + padding*2
    x0 = rect.right - total_w - 8
    y0 = rect.y + (rect.height - total_h)//2
    for i in range(total_pages):
        y = y0 + padding + i*spacing
        color = accent if i == current_page else bg
        r = dot_r if i == current_page else dot_r-2
        pygame.draw.circle(screen, color, (x0 + total_w//2, y), r)
