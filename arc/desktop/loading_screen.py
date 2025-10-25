import pygame
import time

def show_loading_screen(screen, message="Loading...", duration=1.0):
    # Fill the screen with a background color
    screen.fill((30, 30, 30))

    # Use a default font
    font = pygame.font.Font(None, 48)
    text = font.render(message, True, (220, 220, 220))
    rect = text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
    screen.blit(text, rect)

    pygame.display.flip()
    # Optional: process events to keep window responsive
    start = time.time()
    while time.time() - start < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        time.sleep(0.01)
