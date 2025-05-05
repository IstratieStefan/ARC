import pygame

pygame.init()

# Colors
BG = (15, 15, 15)
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
ACCENT = (5, 148, 250)

title_font = pygame.font.Font("assets/fonts/Inter/Inter_24pt-SemiBold.ttf", 24)
items_font = pygame.font.Font("assets/fonts/Inter/Inter_18pt-Regular.ttf", 18)
lock_icon = pygame.image.load("assets/wifi_menu/lock.png")

def draw_wifi_menu(screen, floating_menu_box):
    pygame.draw.rect(screen, (255, 255, 255), floating_menu_box, border_radius=15)
    title = title_font.render("Wifi", True, (0, 0, 0))
    screen.blit(title, (floating_menu_box.x + 10, floating_menu_box.y + 8))
    pygame.draw.line(screen, BG, (0, 85), (480, 85), 1)
    wifi_networks = ["Network1", "Network2", "Network3"]

    for i, ssid in enumerate(wifi_networks):
        y = floating_menu_box.y + 45 + i * 30
        pygame.draw.rect(screen, WHITE, (floating_menu_box.x + 5, y, floating_menu_box.width - 10, 25), border_radius=6)
        text = items_font.render(ssid, True, BG)
        screen.blit(text, (floating_menu_box.x + 10, y + 5))
        resized_icon = pygame.transform.scale(lock_icon, (20, 20))
        icon_rect = resized_icon.get_rect()
        icon_rect.center = (floating_menu_box.right - 20, y + 12)
        screen.blit(resized_icon, icon_rect)

