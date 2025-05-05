import pygame

class TopBar:
    def __init__(self):
        self.icon_size = 24
        self.spacing = 10
        self.icons = {
            "apps": pygame.Rect(self.spacing + 0 * (self.icon_size + self.spacing), 5, self.icon_size, self.icon_size),
            "desktop": pygame.Rect(self.spacing + 1 * (self.icon_size + self.spacing), 5, self.icon_size, self.icon_size),
            "settings": pygame.Rect(self.spacing + 2 * (self.icon_size + self.spacing), 5, self.icon_size, self.icon_size),
            "cellular": pygame.Rect(470 - 3 * (self.icon_size + self.spacing), 5, self.icon_size, self.icon_size),
            "bluetooth": pygame.Rect(470 - 2 * (self.icon_size + self.spacing), 5, self.icon_size, self.icon_size),
            "wifi": pygame.Rect(470 - 1 * (self.icon_size + self.spacing), 5, self.icon_size, self.icon_size),
        }

        self.images = {
            name: pygame.transform.smoothscale(
                pygame.image.load(f"assets/topbar/{name}.png").convert_alpha(),
                (24, 24)
            )
            for name in self.icons
        }

    def draw(self, surface):
        for name, rect in self.icons.items():
            surface.blit(self.images[name], rect)

    def handle_click(self, pos):
        for name, rect in self.icons.items():
            if rect.collidepoint(pos):
                return name
        return None
