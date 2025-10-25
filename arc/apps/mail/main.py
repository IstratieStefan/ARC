import pygame
import sys
import math
from arc.core import config
from arc.core.ui_elements import Button, WarningMessage, TabManager, SearchBox

class EmailApp:
    """
    Simple email client with read and compose views.
    Folders: Inbox, Sent, Drafts
    Views: list, read, compose
    """
    ITEMS_PER_PAGE = 8

    def __init__(self):
        pygame.font.init()
        # folders
        self.folders = ["Inbox", "Sent", "Drafts"]
        self.folder_tabs = TabManager(self.folders)

        # mock messages
        self.messages = {f: [] for f in self.folders}
        # populate inbox and sent with sample
        self.messages["Inbox"] = [
            {"sender": "alice@example.com", "subject": "Meeting Tomorrow", "body": "Hi there,\nDon't forget our 10am meeting."},
            {"sender": "bob@example.com", "subject": "Lunch?", "body": "Are you free for lunch today?"},
        ]
        self.messages["Sent"] = [
            {"sender": "me@example.com", "subject": "Re: Project", "body": "I've pushed the latest updates."}
        ]

        # state
        self.view = "list"  # list | read | compose
        self.selected_idx = 0
        self.scroll = 0

        # read view back button
        self.btn_back = Button("Back", (20, 20, 100, 40), self._go_list)
        # compose button in list
        self.btn_compose = Button("Compose", (config.SCREEN_WIDTH - 140, 20, 120, 40), self._go_compose)

        # compose inputs
        w = config.SCREEN_WIDTH - 100
        self.input_to = SearchBox((50, 100, w, 40), placeholder="To: ")
        self.input_subject = SearchBox((50, 160, w, 40), placeholder="Subject: ")
        # body: simple multi-line area, capture keys
        self.body_lines = [""]
        self.body_rect = pygame.Rect(50, 220, w, 240)
        self.body_active = False

        # send/cancel buttons
        self.btn_send = Button("Send", (50, 480, 120, 40), self._send_email)
        self.btn_cancel = Button("Cancel", (200, 480, 120, 40), self._go_list)

        self.warning = WarningMessage("")

    def _go_list(self):
        self.view = "list"
        self.selected_idx = self.scroll

    def _go_compose(self):
        self.view = "compose"
        self.input_to.text = ""
        self.input_subject.text = ""
        self.body_lines = [""]
        self.selected_idx = 0

    def _send_email(self):
        # mock send: add to Sent
        to = self.input_to.text.strip()
        subj = self.input_subject.text.strip()
        body = "\n".join(self.body_lines).strip()
        if to and subj:
            self.messages["Sent"].insert(0, {"sender": to, "subject": subj, "body": body})
            self.warning.text = "Email sent"
            self.warning.show()
            self._go_list()
        else:
            self.warning.text = "To and Subject required"
            self.warning.show()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if self.view == "list":
            self.folder_tabs.handle_event(event)
            self.btn_compose.handle_event(event)
            # scroll and nav
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RIGHT, pygame.K_LEFT):
                    idx = self.folder_tabs.active
                    idx = (idx + (1 if event.key==pygame.K_RIGHT else -1)) % len(self.folders)
                    self.folder_tabs.active = idx; self.selected_idx = self.scroll = 0; return
                if event.key in (pygame.K_DOWN, pygame.K_UP):
                    msgs = self._current_list()
                    step = 1 if event.key==pygame.K_DOWN else -1
                    self.selected_idx = max(0, min(len(msgs)-1, self.selected_idx+step))
                    if self.selected_idx < self.scroll: self.scroll = self.selected_idx
                    elif self.selected_idx >= self.scroll + self.ITEMS_PER_PAGE:
                        self.scroll = self.selected_idx - self.ITEMS_PER_PAGE + 1
                    return
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.view = "read"; return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: self.scroll = max(0, self.scroll-1)
                elif event.button ==5:
                    self.scroll = min(len(self._current_list())-self.ITEMS_PER_PAGE, self.scroll+1)
            # select via mouse
            for i, msg in enumerate(self._current_list()):
                rect = pygame.Rect(50, 100 + (i-self.scroll)*50, config.SCREEN_WIDTH-100, 40)
                if rect.collidepoint(pygame.mouse.get_pos()):
                    self.selected_idx = i

        elif self.view == "read":
            self.btn_back.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
                self._go_list(); return

        elif self.view == "compose":
            self.input_to.handle_event(event)
            self.input_subject.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                # activate body on click
                self.body_active = self.body_rect.collidepoint(event.pos)
            if event.type == pygame.KEYDOWN and self.body_active:
                if event.key == pygame.K_BACKSPACE:
                    if self.body_lines[-1]:
                        self.body_lines[-1] = self.body_lines[-1][:-1]
                    elif len(self.body_lines)>1:
                        self.body_lines.pop()
                elif event.key == pygame.K_RETURN:
                    self.body_lines.append("")
                else:
                    self.body_lines[-1] += event.unicode
            self.btn_send.handle_event(event); self.btn_cancel.handle_event(event)

    def update(self):
        self.warning.update();

    def draw(self, screen):
        screen.fill(config.COLORS['background'])
        if self.view == "list":
            self.folder_tabs.draw(screen)
            font=pygame.font.SysFont(config.FONT_NAME,36)
            txt=font.render(self.folders[self.folder_tabs.active],True,config.COLORS['text'])
            screen.blit(txt,txt.get_rect(center=(config.SCREEN_WIDTH//2,60)))
            self.btn_compose.draw(screen)
            # list
            msgs=self._current_list()
            for i in range(self.scroll, min(self.scroll+self.ITEMS_PER_PAGE,len(msgs))):
                msg=msgs[i]; y=100+(i-self.scroll)*50; rect=pygame.Rect(50,y,config.SCREEN_WIDTH-100,40)
                pygame.draw.rect(screen,config.COLORS['button'],rect,border_radius=5)
                if i==self.selected_idx:
                    pygame.draw.rect(screen,config.COLORS['accent'],rect.inflate(4,4),width=3,border_radius=7)
                fnt=pygame.font.SysFont(config.FONT_NAME,24)
                screen.blit(fnt.render(msg['subject'],True,config.COLORS['text_light']),(rect.x+10,rect.y+5))
                screen.blit(fnt.render(msg['sender'],True,config.COLORS['text']),(rect.x+10,rect.y+25))
        elif self.view=="read":
            self.btn_back.draw(screen)
            msg=self._current_list()[self.selected_idx]
            fnt=pygame.font.SysFont(config.FONT_NAME,28)
            screen.blit(fnt.render(msg['subject'],True,config.COLORS['text']),(50,120))
            screen.blit(fnt.render("From: "+msg['sender'],True,config.COLORS['text_light']),(50,160))
            bf=pygame.font.SysFont(config.FONT_NAME,20)
            for idx,line in enumerate(msg['body'].split("\n")):
                screen.blit(bf.render(line,True,config.COLORS['text']),(50,200+idx*24))
        else:  # compose
            fnt=pygame.font.SysFont(config.FONT_NAME,36)
            screen.blit(fnt.render("Compose",True,config.COLORS['text']),(50,60))
            self.input_to.draw(screen); self.input_subject.draw(screen)
            # body area
            pygame.draw.rect(screen,config.COLORS['input_bg'],self.body_rect)
            pygame.draw.rect(screen,config.COLORS['input_border'],self.body_rect,2)
            bf=pygame.font.SysFont(config.FONT_NAME,20)
            for idx,line in enumerate(self.body_lines):
                screen.blit(bf.render(line,True,config.COLORS['text']),(self.body_rect.x+5,self.body_rect.y+5+idx*24))
            self.btn_send.draw(screen); self.btn_cancel.draw(screen)
        self.warning.draw(screen)

    def _current_list(self):
        return self.messages[self.folders[self.folder_tabs.active]]

    def run(self):
        pygame.init(); screen=pygame.display.set_mode((config.SCREEN_WIDTH,config.SCREEN_HEIGHT)); pygame.display.set_caption("Email Client")
        clock=pygame.time.Clock()
        while True:
            for e in pygame.event.get(): self.handle_event(e)
            self.update(); self.draw(screen); pygame.display.flip(); clock.tick(config.FPS)

if __name__=='__main__':
    app=EmailApp(); app.run()