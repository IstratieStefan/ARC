import pygame
import sys
import math
import config
from ui_elements import Button, WarningMessage, TabManager

class RFMenu:
    ITEMS_PER_TAB = 3

    def __init__(self):
        # state
        self.page = 0  # 0=channel select, 1=2.4GHz, 2=Sub-1GHz
        self.selected_idx = 0

        # sizes/layout
        self.btn_w, self.btn_h = 400, 60
        self.spacing = 10
        self.top_offset = 60
        cx = config.SCREEN_WIDTH // 2 - self.btn_w // 2
        cy = config.SCREEN_HEIGHT // 2 - self.btn_h

        # Page 0
        self.types_0 = ["2.4 GHz", "Sub-1 GHz"]
        self.btns_0 = [
            Button(self.types_0[i],
                   (cx, cy + i*(self.btn_h + self.spacing), self.btn_w, self.btn_h),
                   lambda idx=i: self.set_page(idx+1))
            for i in range(2)
        ]

        # Page 1: 2.4 GHz
        self.types_24 = [
            "Continuous Wave (CW)", "Frequency Hopping (FHSS)",
            "Direct Sequence Spread Spectrum (DSSS)", "Orthogonal FDM (OFDM)"
        ]
        self.btns_1 = [Button(t, (0,0,self.btn_w,self.btn_h), lambda t=t: self.on_select(t))
                       for t in self.types_24]
        count1 = math.ceil(len(self.types_24) / self.ITEMS_PER_TAB)
        self.tabmgr_1 = TabManager([f"" for _ in range(count1)])

        # Page 2: Sub-1 GHz
        self.types_sub1 = ["Narrowband", "LoRa", "FSK", "Sigfox"]
        self.btns_2 = [Button(t, (0,0,self.btn_w,self.btn_h), lambda t=t: self.on_select(t))
                       for t in self.types_sub1]
        count2 = math.ceil(len(self.types_sub1) / self.ITEMS_PER_TAB)
        self.tabmgr_2 = TabManager([f"" for _ in range(count2)])

        self.warning = WarningMessage("")

    def set_page(self, idx):
        self.page = idx
        self.selected_idx = 0
        # reset subpage manager
        if idx == 1:
            self.tabmgr_1.active = 0
        elif idx == 2:
            self.tabmgr_2.active = 0

    def on_select(self, selection):
        self.warning.text = f"Selected: {selection}"
        self.warning.show()

    def handle_event(self, event):
        # quit
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # page 1 & 2: allow clicking on TabManager indicators
        if self.page == 1:
            self.tabmgr_1.handle_event(event)
        elif self.page == 2:
            self.tabmgr_2.handle_event(event)

        # keyboard navigation
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.page != 0:
                self.set_page(0)
                return

            # up/down moves within current page block
            if event.key in (pygame.K_DOWN, pygame.K_UP):
                btns = self._current_buttons_list()
                max_idx = len(btns) - 1
                step = 1 if event.key == pygame.K_DOWN else -1
                self.selected_idx = (self.selected_idx + step) % (max_idx + 1)
                # if on subpage, change page indicator if moving outside current tab
                if self.page == 1:
                    self.tabmgr_1.active = self.selected_idx // self.ITEMS_PER_TAB
                elif self.page == 2:
                    self.tabmgr_2.active = self.selected_idx // self.ITEMS_PER_TAB
                return

            # Enter to select
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._current_buttons_list()[self.selected_idx].callback()
                return

        # mouse buttons on items
        for i, btn in enumerate(self._current_buttons_list()):
            btn.handle_event(event)
            if btn.hovered:
                self.selected_idx = i

    def update(self):
        self.warning.update()

    def draw(self, surface):
        surface.fill(config.COLORS['background'])
        # title
        height = 60
        if self.page == 0:
            title = "Select RF type"
            height = 60
        else:
            title = "Select Operation"
            height = 35
        font = pygame.font.SysFont(config.FONT_NAME, 40)
        txt = font.render(title, True, config.COLORS['text'])
        surface.blit(txt, txt.get_rect(center=(config.SCREEN_WIDTH//2, height)))

        if self.page == 0:
            # draw two main buttons
            for idx, btn in enumerate(self.btns_0):
                btn.rect.x = config.SCREEN_WIDTH//2 - self.btn_w//2
                btn.rect.y = config.SCREEN_HEIGHT//2 - self.btn_h + idx*(self.btn_h+self.spacing)
                pygame.draw.rect(surface, config.COLORS['button'], btn.rect, border_radius=config.RADIUS["app_button"])
                lbl = pygame.font.SysFont(config.FONT_NAME, 30).render(btn.text, True, config.COLORS['text_light'])
                surface.blit(lbl, lbl.get_rect(center=btn.rect.center))
                if idx == self.selected_idx:
                    pygame.draw.rect(surface, config.COLORS['accent'], btn.rect.inflate(6,6), width=4,
                                     border_radius=config.RADIUS["app_button"])
        else:
            # page 1 or 2: paged lists
            if self.page == 1:
                btns_all, tabmgr = self.btns_1, self.tabmgr_1
            else:
                btns_all, tabmgr = self.btns_2, self.tabmgr_2
            # determine current tab
            active_tab = tabmgr.active
            start = active_tab * self.ITEMS_PER_TAB
            end = start + self.ITEMS_PER_TAB
            for idx, btn in enumerate(btns_all[start:end]):
                btn.rect.x = config.SCREEN_WIDTH//2 - self.btn_w//2
                btn.rect.y = self.top_offset + idx*(self.btn_h+self.spacing)
                pygame.draw.rect(surface, config.COLORS['button'], btn.rect, border_radius=config.RADIUS["app_button"])
                lbl = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE+6).render(btn.text, True, config.COLORS['text_light'])
                surface.blit(lbl, lbl.get_rect(center=btn.rect.center))
                global_idx = start + idx
                if global_idx == self.selected_idx:
                    pygame.draw.rect(surface, config.COLORS['accent'], btn.rect.inflate(6,6), width=4,
                                     border_radius=config.RADIUS["app_button"]+4)
            # draw subpage indicator
            tabmgr.draw(surface)

        self.warning.draw(surface)

    def _current_buttons_list(self):
        if self.page == 0:
            return self.btns_0
        elif self.page == 1:
            return self.btns_1
        return self.btns_2


def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("RF Tools Menu")
    clock = pygame.time.Clock()

    menu = RFMenu()
    while True:
        for event in pygame.event.get():
            menu.handle_event(event)
        menu.update()
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(config.FPS)

if __name__ == '__main__':
    main()