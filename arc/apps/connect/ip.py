import pygame
import socket
import qrcode
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from PIL import Image
import io
from arc.core.config import config   # <-- YAML loader
import threading
import uvicorn
import time

WIDTH, HEIGHT = config.screen.width, config.screen.height
ACCENT_COLOR = tuple(config.accent_color)
BG_COLOR = tuple(config.colors.background)
TEXT_COLOR = tuple(config.colors.text)

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
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

def start_server():
    """Start the FastAPI server in a separate thread"""
    config = uvicorn.Config(
        "arc.apps.connect.server:app",
        host="0.0.0.0",
        port=5001,
        workers=1,
        limit_concurrency=50,
        timeout_keep_alive=30,
        log_level="warning"
    )
    server = uvicorn.Server(config)
    server.run()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("ARC Connect")

    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)
    tiny_font = pygame.font.SysFont(None, 18)

    ip_addr = get_ip_address()
    dashboard_url = f"http://{ip_addr}:5001/"
    qr_surface = make_qr_code(dashboard_url, size=180)

    # Start the web server in a background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Give server a moment to start
    time.sleep(1)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                pygame.quit()

        screen.fill(BG_COLOR)

        # Title
        title_text = font.render("ARC Connect", True, (255, 255, 255))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 10))

        # Status indicator
        status_text = tiny_font.render("Server Running", True, (0, 255, 0))
        status_dot = pygame.Surface((8, 8))
        status_dot.fill((0, 255, 0))
        screen.blit(status_dot, (WIDTH // 2 - 45, 48))
        screen.blit(status_text, (WIDTH // 2 - 30, 45))

        # QR Code
        qr_x = WIDTH // 2 - qr_surface.get_width() // 2
        qr_y = 70
        screen.blit(qr_surface, (qr_x, qr_y))

        # Dashboard URL
        url_text = small_font.render(dashboard_url, True, ACCENT_COLOR)
        screen.blit(url_text, (WIDTH // 2 - url_text.get_width() // 2, qr_y + qr_surface.get_height() + 10))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
