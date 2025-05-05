import pygame
import config

class TopBar:
    def __init__(self):
        self.height = config.TOPBAR_HEIGHT
        self.icons  = []
        for path in config.TOPBAR_ICONS:
            try:
                img = pygame.image.load(path).convert_alpha()
                self.icons.append(pygame.transform.smoothscale(img,(16,16)))
            except:
                self.icons.append(pygame.Surface((16,16),pygame.SRCALPHA))

    def draw(self, surface):
        pygame.draw.rect(surface,config.TOPBAR_BG,(0,0,config.SCREEN_WIDTH,self.height))
        x=5
        for icon in self.icons:
            surface.blit(icon,(x,(self.height-icon.get_height())//2)); x+=icon.get_width()+5
        # timestamp
        txt = pygame.font.SysFont('Arial',14).render(str(pygame.time.get_ticks()//1000),True,config.TOPBAR_FG)
        surface.blit(txt,(config.SCREEN_WIDTH-txt.get_width()-5,(self.height-txt.get_height())//2))