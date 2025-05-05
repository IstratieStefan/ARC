import pygame
import config
from ui_elements import Button, WarningMessage, TabManager, MessageBox, SearchBox

pygame.init()
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Initialize UI
tab_manager = TabManager(['Home', 'Settings', 'About', 'Extra', 'More'])
warning = WarningMessage("This is a warning!")

# Setup message box callbacks
def on_yes():
    print("User selected YES")
def on_no():
    print("User selected NO")
message_box = MessageBox("Are you sure?", on_yes, on_no)

search_box = SearchBox((150, 200, 200, 40), placeholder="Search...", callback=lambda t: print(f"Search: {t}"))

# Create buttons for each page
buttons = {
    0: [
        Button('Warn', (150, 80, 100, 40), warning.show),
        Button('Ask',  (150, 140, 100, 40), message_box.show),
    ],
    1: [
        Button('Option 1', (150, 100, 120, 40), lambda: print('Option 1 selected')),
        Button('Option 2', (150, 160, 120, 40), lambda: print('Option 2 selected'))
    ],
    2: [],
    3: [],
    4: []
}

running = True
while running:
    dt = clock.tick(config.FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # message box has priority
        if message_box.visible:
            message_box.handle_event(event)
        else:
            tab_manager.handle_event(event)
            for btn in buttons[tab_manager.get_active_index()]:
                btn.handle_event(event)

    warning.update()

    # Draw
    screen.fill(config.COLORS['background'])
    tab_manager.draw(screen)
    for btn in buttons[tab_manager.get_active_index()]:
        btn.draw(screen)
    warning.draw(screen)
    search_box.draw(screen)
    message_box.draw(screen)

    pygame.display.flip()

pygame.quit()
