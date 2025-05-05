import pygame

pygame.init()

# Screen setup
screen = pygame.display.set_mode((480, 320))
pygame.display.set_caption("Menu UI")
clock = pygame.time.Clock()

# Colors
BG = (15, 15, 15)
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
ACCENT = (5, 148, 250)

# Fonts
title_font = pygame.font.Font("assets/fonts/Inter/Inter_24pt-SemiBold.ttf", 24)
items_font = pygame.font.Font("assets/fonts/Inter/Inter_18pt-Regular.ttf", 18)

# Load icons
bluetooth_icon = pygame.image.load("assets/bluetooth_menu/bluetooth.png").convert_alpha()
bluetooth_icon = pygame.transform.scale(bluetooth_icon, (18, 18))

def draw_bluetooth_menu(screen, floating_menu_box):
    pygame.draw.rect(screen, WHITE, floating_menu_box, border_radius=15)
    title = title_font.render("Bluetooth", True, (0, 0, 0))
    screen.blit(title, (floating_menu_box.x + 10, floating_menu_box.y + 8))
    pygame.draw.line(screen, BG, (0, 85), (480, 85), 1)

    bluetooth_devices = ["Speaker", "Headphones", "Keyboard"]

    for i, name in enumerate(bluetooth_devices):
        y = floating_menu_box.y + 45 + i * 30
        pygame.draw.rect(screen, WHITE, (floating_menu_box.x + 5, y, floating_menu_box.width - 10, 25), border_radius=6)
        text = items_font.render(name, True, BG)
        screen.blit(text, (floating_menu_box.x + 10, y + 5))
        icon_rect = bluetooth_icon.get_rect()
        icon_rect.center = (floating_menu_box.right - 20, y + 12)
        screen.blit(bluetooth_icon, icon_rect)


