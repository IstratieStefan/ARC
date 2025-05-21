import pygame
import socket
import qrcode
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PIL import Image
import io
import config

WIDTH, HEIGHT = 480, 320
ACCENT_COLOR = config.ACCENT_COLOR
BG_COLOR = config.COLORS['background']
TEXT_COLOR = config.COLORS['text']

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable; just used to get local IP
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def make_qr_code(data, size=160):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    qr_surface = pygame.image.load(buf, 'qr.png')
    return qr_surface

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("IP Address & QR Code")

    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 22)

    ip_addr = get_ip_address()
    qr_surface = make_qr_code(ip_addr, size=160)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    pygame.quit()



        screen.fill(BG_COLOR)

        # Render the IP address
        text = font.render("IP Address:", True, TEXT_COLOR)
        ip_text = font.render(ip_addr, True, ACCENT_COLOR)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 20))
        screen.blit(ip_text, (WIDTH // 2 - ip_text.get_width() // 2, 60))

        qr_x = WIDTH // 2 - qr_surface.get_width() // 2
        qr_y = 100
        screen.blit(qr_surface, (qr_x, qr_y))

        info_text = small_font.render("Scan this QR with your app to connect!", True, (180, 180, 180))
        screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, HEIGHT - 40))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
