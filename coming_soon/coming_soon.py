import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 480, 320
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Coming Soon')

# Set up font and render text
font = pygame.font.Font(None, 74)  # Default font, size 74
text_surface = font.render('Coming Soon', True, (255, 255, 255))  # White text
text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# Main loop
def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the background
        screen.fill((0, 0, 0))  # Black background

        # Blit the text
        screen.blit(text_surface, text_rect)

        # Update the display
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()