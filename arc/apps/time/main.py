import pygame
import sys
import time
from config import config

WIDTH, HEIGHT = config.screen.width, config.screen.height
TAB_HEIGHT = 50
BG = (30, 32, 38)
TAB_BG = (50, 50, 50)
TAB_ACTIVE = (204, 99, 36)
WHITE = (250, 250, 250)
ACCENT = (204, 99, 36)
BTN_BG = (90, 90, 105)
BTN_HOVER = (140, 140, 170)
BTN_TXT = (240, 240, 240)

pygame.init()
# Try nicer fonts; fallbacks for cross-platform support
def get_font(name, size, bold=False):
    try:
        return pygame.font.SysFont(name, size, bold=bold)
    except Exception:
        return pygame.font.SysFont("arial", size, bold=bold)

FONT = get_font("Segoe UI", 48, True) or get_font("DejaVu Sans", 48, True)
SMALL = get_font("Segoe UI", 28) or get_font("DejaVu Sans", 28)
TINY = get_font("Segoe UI", 18) or get_font("DejaVu Sans", 18)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Stopwatch / Timer / Pomodoro")
clock = pygame.time.Clock()
TABS = ["Stopwatch", "Timer", "Pomodoro"]

def draw_tabs(active):
    for i, tab in enumerate(TABS):
        rect = pygame.Rect(i * WIDTH//3, 0, WIDTH//3, TAB_HEIGHT)
        color = TAB_ACTIVE if i == active else TAB_BG
        pygame.draw.rect(screen, color, rect, border_radius=14)
        txt = SMALL.render(tab, True, WHITE)
        screen.blit(txt, txt.get_rect(center=rect.center))

def draw_btn(label, rect, hovered=False, pressed=False, padding=18):
    color = BTN_HOVER if hovered else (TAB_ACTIVE if pressed else BTN_BG)
    pygame.draw.rect(screen, color, rect, border_radius=16)
    txt = SMALL.render(label, True, BTN_TXT)
    padded_rect = rect.inflate(-2*padding, -2*padding)
    text_rect = txt.get_rect(center=padded_rect.center)
    screen.blit(txt, text_rect)

def format_time(seconds, show_hours=True):
    if show_hours:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02}:{m:02}:{s:02}"
    else:
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m:02}:{s:02}"

def layout_buttons_centered(num_buttons, btn_w, btn_h, btn_gap, y, outer_pad):
    total_width = num_buttons * btn_w + (num_buttons - 1) * btn_gap
    x_start = (WIDTH - total_width) // 2
    return [
        pygame.Rect(x_start + i * (btn_w + btn_gap), y, btn_w, btn_h)
        for i in range(num_buttons)
    ]

def main():
    active_tab = 0
    running = [False, False, False]
    start_time = [0, 0, 0]
    elapsed = [0, 0, 0]
    laps = []
    timer_set = 5*60  # default 5 min
    timer_input = ""
    pomodoro_state = "Work"
    pomodoro_durations = {"Work": 25*60, "Break": 5*60}
    pomodoro_left = pomodoro_durations["Work"]
    pomodoro_cycles = 0

    # Button layout params
    btn_y = 200
    btn_h = 52
    btn_w_long = 130
    btn_w_short = 100
    btn_gap = 32      # More space between buttons
    outer_pad = 32    # Space around button group

    mouse_pos = (0, 0)

    while True:
        screen.fill(BG)
        draw_tabs(active_tab)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_TAB:
                    active_tab = (active_tab + 1) % 3
                if active_tab == 1:
                    if event.unicode.isdigit():
                        timer_input += event.unicode
                    elif event.key == pygame.K_BACKSPACE:
                        timer_input = timer_input[:-1]
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if timer_input:
                            timer_set = int(timer_input)
                            timer_input = ""
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Tab switching by click
                if my < TAB_HEIGHT:
                    tab_clicked = mx // (WIDTH//3)
                    if tab_clicked != active_tab:
                        active_tab = tab_clicked
                # Stopwatch buttons
                if active_tab == 0:
                    btns = ["Start" if not running[0] else "Pause", "Reset", "Lap"]
                    btn_rects = layout_buttons_centered(len(btns), btn_w_long, btn_h, btn_gap, btn_y, outer_pad)
                    for i, r in enumerate(btn_rects):
                        if r.collidepoint(mx, my):
                            if i == 0:  # Start/Pause
                                if not running[0]:
                                    start_time[0] = time.time() - elapsed[0]
                                    running[0] = True
                                else:
                                    elapsed[0] = time.time() - start_time[0]
                                    running[0] = False
                            elif i == 1:  # Reset
                                running[0] = False
                                elapsed[0] = 0
                                start_time[0] = 0
                                laps.clear()
                            elif i == 2:  # Lap
                                laps.append(format_time(elapsed[0], show_hours=True))
                # Timer buttons
                if active_tab == 1:
                    btns = ["Start" if not running[1] else "Pause", "Reset", "Set"]
                    btn_rects = layout_buttons_centered(len(btns), btn_w_long, btn_h, btn_gap, btn_y, outer_pad)
                    for i, r in enumerate(btn_rects):
                        if r.collidepoint(mx, my):
                            if i == 0:  # Start/Pause
                                if not running[1]:
                                    start_time[1] = time.time() - elapsed[1]
                                    running[1] = True
                                else:
                                    elapsed[1] = time.time() - start_time[1]
                                    running[1] = False
                            elif i == 1:  # Reset
                                running[1] = False
                                elapsed[1] = 0
                                start_time[1] = 0
                            elif i == 2:  # Set
                                if timer_input:
                                    timer_set = int(timer_input)
                                    timer_input = ""
                # Pomodoro buttons
                if active_tab == 2:
                    btns = ["Start" if not running[2] else "Pause", "Reset", "Next"]
                    btn_rects = layout_buttons_centered(len(btns), btn_w_short, btn_h, btn_gap, btn_y, outer_pad)
                    for i, r in enumerate(btn_rects):
                        if r.collidepoint(mx, my):
                            if i == 0:  # Start/Pause
                                if not running[2]:
                                    running[2] = True
                                else:
                                    running[2] = False
                            elif i == 1:  # Reset
                                running[2] = False
                                pomodoro_state = "Work"
                                pomodoro_left = pomodoro_durations[pomodoro_state]
                            elif i == 2:  # Next
                                # Switch state
                                if pomodoro_state == "Work":
                                    pomodoro_state = "Break"
                                    pomodoro_left = pomodoro_durations["Break"]
                                    running[2] = False
                                    pomodoro_cycles += 1
                                else:
                                    pomodoro_state = "Work"
                                    pomodoro_left = pomodoro_durations["Work"]
                                    running[2] = False

        # --- STOPWATCH TAB ---
        if active_tab == 0:
            if running[0]:
                elapsed[0] = time.time() - start_time[0]
            main_time = format_time(elapsed[0], show_hours=True)
            t_render = FONT.render(main_time, True, ACCENT)
            screen.blit(t_render, t_render.get_rect(center=(WIDTH//2, 110)))
            btns = ["Start" if not running[0] else "Pause", "Reset", "Lap"]
            btn_rects = layout_buttons_centered(len(btns), btn_w_long, btn_h, btn_gap, btn_y, outer_pad)
            for i, r in enumerate(btn_rects):
                hovered = r.collidepoint(mouse_pos)
                draw_btn(btns[i], r, hovered=hovered)
            # Laps
            y = btn_y + btn_h + 16
            for i, lap in enumerate(laps[-3:][::-1]):
                ltxt = TINY.render(f"Lap {len(laps)-i}: {lap}", True, WHITE)
                screen.blit(ltxt, (outer_pad, y))
                y += 22

        # --- TIMER TAB ---
        elif active_tab == 1:
            if running[1]:
                elapsed[1] = time.time() - start_time[1]
                remaining = max(0, timer_set - elapsed[1])
                if remaining <= 0:
                    running[1] = False
                    elapsed[1] = timer_set
            else:
                remaining = max(0, timer_set - elapsed[1]) if elapsed[1] > 0 else timer_set
            main_time = format_time(remaining, show_hours=True)
            t_render = FONT.render(main_time, True, ACCENT)
            screen.blit(t_render, t_render.get_rect(center=(WIDTH//2, 110)))
            inp_render = TINY.render("Set (sec): " + timer_input, True, WHITE)
            screen.blit(inp_render, (outer_pad, 170))
            btns = ["Start" if not running[1] else "Pause", "Reset", "Set"]
            btn_rects = layout_buttons_centered(len(btns), btn_w_long, btn_h, btn_gap, btn_y, outer_pad)
            for i, r in enumerate(btn_rects):
                hovered = r.collidepoint(mouse_pos)
                draw_btn(btns[i], r, hovered=hovered)

        # --- POMODORO TAB ---
        elif active_tab == 2:
            t_render = FONT.render(format_time(pomodoro_left, show_hours=False), True, ACCENT)
            screen.blit(t_render, t_render.get_rect(center=(WIDTH//2, 110)))
            state_txt = TINY.render(f"{pomodoro_state} | Cycles: {pomodoro_cycles}", True, WHITE)
            screen.blit(state_txt, (outer_pad, 170))
            btns = ["Start" if not running[2] else "Pause", "Reset", "Next"]
            btn_rects = layout_buttons_centered(len(btns), btn_w_short, btn_h, btn_gap, btn_y, outer_pad)
            for i, r in enumerate(btn_rects):
                hovered = r.collidepoint(mouse_pos)
                draw_btn(btns[i], r, hovered=hovered)

        # Update Pomodoro timer
        if running[2]:
            pomodoro_left -= clock.get_time() / 1000
            if pomodoro_left <= 0:
                if pomodoro_state == "Work":
                    pomodoro_state = "Break"
                    pomodoro_left = pomodoro_durations["Break"]
                    pomodoro_cycles += 1
                else:
                    pomodoro_state = "Work"
                    pomodoro_left = pomodoro_durations["Work"]

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
