import pygame
import requests
import math
import os
import sys
import geocoder
import threading
from queue import Queue

WIDTH, HEIGHT = 640, 480
TILE_SIZE = 256
TILE_FOLDER = "tiles"
MAX_WORKERS = 3  # How many concurrent tile downloads

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame OSM Map Async")

tile_cache = {}
tile_queue = Queue()
tile_cache_lock = threading.Lock()

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

def tile_path(z, x, y):
    return f"{TILE_FOLDER}/{z}_{x}_{y}.png"

def get_current_location():
    try:
        g = geocoder.ip('me')
        lat, lon = g.latlng
        print(f"Located by IP: {lat}, {lon}")
        return lat, lon
    except Exception as e:
        print("Could not geolocate, fallback to Brasov:", e)
        return 45.6456, 25.6072  # Brasov fallback

def blank_tile():
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    surf.fill((230, 230, 230))
    pygame.draw.line(surf, (180, 120, 120), (0, 0), (TILE_SIZE, TILE_SIZE), 3)
    pygame.draw.line(surf, (180, 120, 120), (TILE_SIZE, 0), (0, TILE_SIZE), 3)
    return surf

def loading_tile():
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    surf.fill((220, 220, 220))
    pygame.draw.circle(surf, (150, 180, 200), (TILE_SIZE // 2, TILE_SIZE // 2), 30, 5)
    return surf

def async_tile_worker():
    while True:
        z, x, y = tile_queue.get()
        path = tile_path(z, x, y)
        with tile_cache_lock:
            if (z, x, y) in tile_cache and tile_cache[(z, x, y)] is not None:
                tile_queue.task_done()
                continue
            tile_cache[(z, x, y)] = None  # mark as loading
        os.makedirs(TILE_FOLDER, exist_ok=True)
        if not os.path.exists(path):
            url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
            try:
                print(f"Downloading tile: {z}/{x}/{y}")
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    with open(path, "wb") as f:
                        f.write(r.content)
                    print(f"Tile saved: {path}")
                else:
                    print(f"Tile {z}/{x}/{y} HTTP error {r.status_code}")
                    with tile_cache_lock:
                        tile_cache[(z, x, y)] = blank_tile()
                    tile_queue.task_done()
                    continue
            except Exception as e:
                print(f"Exception while downloading tile {z}/{x}/{y}: {e}")
                with tile_cache_lock:
                    tile_cache[(z, x, y)] = blank_tile()
                tile_queue.task_done()
                continue
        try:
            img = pygame.image.load(path)
            with tile_cache_lock:
                tile_cache[(z, x, y)] = img
        except Exception as e:
            print(f"Error loading tile image {path}: {e}")
            with tile_cache_lock:
                tile_cache[(z, x, y)] = blank_tile()
        tile_queue.task_done()

# Start background workers
for _ in range(MAX_WORKERS):
    threading.Thread(target=async_tile_worker, daemon=True).start()

def get_tile(z, x, y):
    key = (z, x, y)
    with tile_cache_lock:
        if key in tile_cache and tile_cache[key]:
            return tile_cache[key]
        elif key in tile_cache and tile_cache[key] is None:
            return loading_tile()
    path = tile_path(z, x, y)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path)
            with tile_cache_lock:
                tile_cache[key] = img
            return img
        except Exception as e:
            print(f"Error loading cached tile: {e}")
            with tile_cache_lock:
                tile_cache[key] = blank_tile()
            return blank_tile()
    else:
        with tile_cache_lock:
            tile_cache[key] = None  # mark as loading
        tile_queue.put((z, x, y))
        return loading_tile()

def main():
    lat, lon = get_current_location()
    zoom = 16
    offset_x, offset_y = 0, 0
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_LEFT, pygame.K_a]:
                    offset_x -= 60
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    offset_x += 60
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    offset_y -= 60
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    offset_y += 60
                elif event.key in [pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS]:
                    if zoom < 19:
                        zoom += 1
                        offset_x //= 2
                        offset_y //= 2
                elif event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]:
                    if zoom > 1:
                        zoom -= 1
                        offset_x *= 2
                        offset_y *= 2

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4 and zoom < 19:  # wheel up
                    zoom += 1
                    offset_x //= 2
                    offset_y //= 2
                elif event.button == 5 and zoom > 1:  # wheel down
                    zoom -= 1
                    offset_x *= 2
                    offset_y *= 2

        center_tile_x, center_tile_y = deg2num(lat, lon, zoom)
        px = WIDTH // 2 - offset_x
        py = HEIGHT // 2 - offset_y

        screen.fill((40, 40, 40))
        # Draw visible 3x3 tiles grid
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                tx = center_tile_x + dx
                ty = center_tile_y + dy
                tile = get_tile(zoom, tx, ty)
                x = px + (dx * TILE_SIZE)
                y = py + (dy * TILE_SIZE)
                if tile:
                    screen.blit(tile, (x, y))
        # Draw center marker
        pygame.draw.circle(screen, (220, 60, 50), (WIDTH // 2, HEIGHT // 2), 8, 0)
        pygame.draw.circle(screen, (255, 255, 255), (WIDTH // 2, HEIGHT // 2), 8, 2)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
