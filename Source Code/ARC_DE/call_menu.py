import pygame
import sys
import config

# Screen configuration
WIDTH = config.SCREEN_WIDTH
HEIGHT = config.SCREEN_HEIGHT
FPS = 30

# Colors
dark_bg = config.COLORS['background']
white   = config.COLORS['text']
green   = (0, 180, 0)
red     = (180, 0, 0)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Incoming Call")
clock = pygame.time.Clock()

# Load fonts
name_font = pygame.font.SysFont(None, 56)
num_font  = pygame.font.SysFont(None, 40)
btn_font  = pygame.font.SysFont(None, 36)

# Define button rectangles
btn_w, btn_h = 160, 60
accept_rect = pygame.Rect( (WIDTH//4 - btn_w//2, HEIGHT - btn_h - 20), (btn_w, btn_h) )
reject_rect = pygame.Rect( (3*WIDTH//4 - btn_w//2, HEIGHT - btn_h - 20), (btn_w, btn_h) )

# Sample incoming data
def get_incoming():
    # TO DO: Replace with actual SIM800L serial communication
    return "Marcel", "+40 736 893 378"

# Draw the incoming call menu
def draw_incoming(name, number):
    screen.fill(dark_bg)

    # Draw name
    name_surf = name_font.render(name, True, white)
    name_rect = name_surf.get_rect(center=(WIDTH//2, HEIGHT//5))
    screen.blit(name_surf, name_rect)

    # Draw number
    num_surf = num_font.render(number, True, white)
    num_rect = num_surf.get_rect(center=(WIDTH//2, HEIGHT//5 + 40))
    screen.blit(num_surf, num_rect)

    # Draw Accept button
    pygame.draw.rect(screen, green, accept_rect, border_radius=8)
    acc_txt = btn_font.render("Accept", True, white)
    acc_rect = acc_txt.get_rect(center=accept_rect.center)
    screen.blit(acc_txt, acc_rect)

    # Draw Reject button
    pygame.draw.rect(screen, red, reject_rect, border_radius=8)
    rej_txt = btn_font.render("Reject", True, white)
    rej_rect = rej_txt.get_rect(center=reject_rect.center)
    screen.blit(rej_txt, rej_rect)

    pygame.display.flip()

# Main loop
def main():
    name, number = get_incoming()
    draw_incoming(name, number)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if accept_rect.collidepoint(event.pos):
                    print("Call accepted")
                    return
                if reject_rect.collidepoint(event.pos):
                    print("Call rejected")
                    return

        clock.tick(FPS)

if __name__ == "__main__":
    main()
