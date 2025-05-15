import os
import pygame
import config

# Attempt to import Xlib for X11/XWayland captures
try:
    from Xlib import display, X
except ImportError:
    display = None

class AppCarouselMenu:
    def __init__(self, apps, launch_callback, screen_size):
        """
        apps: list of dicts, optionally with 'window_id' for live previews
        launch_callback: function to call with exec cmd
        screen_size: (width, height)
        """
        self.apps = apps
        self.launch = launch_callback
        self.sw, self.sh = screen_size
        self.selected = 0
        self.active = False

        # preload static icons
        self.static_icons = []
        for a in apps:
            img = pygame.image.load(a.get('icon', '')).convert_alpha()
            self.static_icons.append(img)

        # Determine if X11 or XWayland server is available via DISPLAY
        self.use_x = False
        if display and os.getenv('DISPLAY'):
            try:
                # Try to connect to X server (real X11 or XWayland)
                self.dpy = display.Display()
                self.use_x = True
            except Exception:
                self.dpy = None
        else:
            self.dpy = None

    def open(self):
        self.active = True
        self.selected = 0

    def close(self):
        self.active = False

    def handle_event(self, ev):
        if ev.type != pygame.KEYDOWN:
            return
        if ev.key == pygame.K_LEFT:
            self.selected = (self.selected - 1) % len(self.apps)
        elif ev.key == pygame.K_RIGHT:
            self.selected = (self.selected + 1) % len(self.apps)
        elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            cmd = self.apps[self.selected].get('exec', '')
            if cmd:
                self.launch(cmd)
            self.close()
        elif ev.key in (pygame.K_TAB, pygame.K_ESCAPE):
            self.close()

    def draw(self, surface):
        # dark overlay
        overlay = pygame.Surface((self.sw, self.sh)); overlay.set_alpha(180); overlay.fill((0,0,0))
        surface.blit(overlay, (0,0))

        # attempt live preview if X connection and window_id provided
        preview_surf = None
        info = self.apps[self.selected]
        win_id = info.get('window_id')
        if self.use_x and win_id:
            preview_surf = self._capture_x(win_id)
        # fallback to static icon
        if preview_surf is None:
            preview_surf = self.static_icons[self.selected]

        # scale preview to 80%
        side = int(min(self.sw, self.sh) * 0.8)
        preview = pygame.transform.smoothscale(preview_surf, (side, side))
        x = (self.sw - side)//2; y = (self.sh - side)//2 - 20
        surface.blit(preview, (x,y))

        # draw app name
        name = info.get('name','')
        font = pygame.font.SysFont(config.FONT_NAME, 28)
        txt = font.render(name, True, config.COLORS['text_light'])
        tx = (self.sw - txt.get_width())//2; ty = y + side + 10
        surface.blit(txt, (tx,ty))

        # position indicator
        pos = f"{self.selected+1}/{len(self.apps)}"
        pf = pygame.font.SysFont(config.FONT_NAME, 20)
        pi = pf.render(pos, True, config.COLORS['text_light'])
        px = (self.sw - pi.get_width())//2; py = ty + font.get_height() + 5
        surface.blit(pi, (px,py))

        # arrows
        af = pygame.font.SysFont(config.FONT_NAME, 40)
        left = af.render("<", True, config.COLORS['accent'])
        right = af.render(">", True, config.COLORS['accent'])
        surface.blit(left, (20, (self.sh-left.get_height())//2))
        surface.blit(right, (self.sw-20-right.get_width(), (self.sh-right.get_height())//2))

    def _capture_x(self, window_id):
        """
        Capture a screenshot of an X11 or XWayland window by ID. Returns a pygame.Surface or None.
        """
        try:
            win = self.dpy.create_resource_object('window', window_id)
            geom = win.get_geometry()
            raw = win.get_image(0, 0, geom.width, geom.height, X.ZPixmap, 0xffffffff)
            data = raw.data  # bytes in native order (typically BGRX)
            # create surface; format 'BGRX' matches little-endian 32-bit
            surf = pygame.image.frombuffer(data, (geom.width, geom.height), 'BGRX')
            return surf
        except Exception:
            return None
