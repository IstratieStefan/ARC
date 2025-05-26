import pygame
import sys
import math
from config import config

pygame.init()

WIDTH, HEIGHT = 480, 320
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Scientific Calculator")

# === COLORS ===
COLORS = {
    "background":      (28, 28, 28),        # background: dark neutral
    "text":            (220, 220, 220),     # text: light gray for contrast
    "display_bg":      (38, 38, 38),        # display area, slightly lighter than bg
    "button":          (220, 220, 220),     # main button, light gray
    "button_func":     (255, 190, 80),      # function buttons, warm accent (orange-yellow)
    "button_op":       (200, 200, 200),     # operators, neutral but stands out
    "button_eq":       (255, 140, 80),      # equals, accent orange
    "button_text":     (22, 22, 22),        # dark text for best contrast on light buttons
    "result_text":     (255, 140, 80),      # result text, match equals for clarity
    "accent":          (255, 140, 80),      # accent, matches equals/result
    "pressed":         (120, 180, 230),     # pressed, blueish highlight
}

FONT = pygame.font.SysFont('consolas', 26)
SMALL_FONT = pygame.font.SysFont('consolas', 17)
DISPLAY_FONT = pygame.font.SysFont('consolas', 30)

# === BUTTONS ===
BUTTONS = [
    ['7', '8', '9', '/', 'sin'],
    ['4', '5', '6', '*', 'cos'],
    ['1', '2', '3', '-', 'tan'],
    ['0', '.', '=', '+', '√'],
    ['C', '←', '^', '(', ')'],
    ['π', 'ln', 'log', '', ''],
]
ROWS, COLS = len(BUTTONS), max(len(row) for row in BUTTONS)

GAP = 5
TOP_BAR = 80
# Dynamically compute button width/height to always fit screen
BUTTON_W = (WIDTH - (COLS + 1) * GAP) // COLS
BUTTON_H = (HEIGHT - TOP_BAR - (ROWS + 1) * GAP) // ROWS

# For keyboard mapping
KEY_FUNCTIONS = {
    pygame.K_RETURN: '=', pygame.K_KP_ENTER: '=',
    pygame.K_BACKSPACE: '←', pygame.K_DELETE: 'C', pygame.K_c: 'C',
    pygame.K_LEFTPAREN: '(', pygame.K_RIGHTPAREN: ')',
    pygame.K_PERIOD: '.', pygame.K_COMMA: '.', pygame.K_SEMICOLON: '.',
    pygame.K_PLUS: '+', pygame.K_MINUS: '-', pygame.K_ASTERISK: '*', pygame.K_SLASH: '/',
    pygame.K_0: '0', pygame.K_1: '1', pygame.K_2: '2', pygame.K_3: '3', pygame.K_4: '4',
    pygame.K_5: '5', pygame.K_6: '6', pygame.K_7: '7', pygame.K_8: '8', pygame.K_9: '9',
    pygame.K_p: 'π', pygame.K_s: 'sin', pygame.K_t: 'tan', pygame.K_l: 'ln',
    pygame.K_g: 'log', pygame.K_r: '√', pygame.K_e: '^',
}

def safe_eval(expr):
    try:
        allowed_names = {k: getattr(math, k) for k in [
            "sin", "cos", "tan", "sqrt", "log", "pi", "e", "log10", "pow"
        ]}
        allowed_names['ln'] = math.log
        allowed_names['π'] = math.pi

        # Expression normalization
        expr = expr.replace('^', '**').replace('π', 'pi').replace('√', 'sqrt')
        expr = expr.replace('ln', 'log').replace('log', 'log10')
        # Remove trailing invalids
        while expr and expr[-1] in "+-*/^.":
            expr = expr[:-1]
        return str(eval(expr, {"__builtins__": None}, allowed_names))
    except Exception:
        return "Error"

def draw_display(current, result):
    pygame.draw.rect(screen, COLORS["display_bg"], (0, 0, WIDTH, TOP_BAR))
    disp_text = current if current else '0'
    if len(disp_text) > 22:
        disp_text = disp_text[-22:]
    disp = DISPLAY_FONT.render(disp_text, True, COLORS["text"])
    screen.blit(disp, (WIDTH - 18 - disp.get_width(), 18))
    if result:
        res = SMALL_FONT.render(result, True, COLORS["result_text"])
        screen.blit(res, (WIDTH - 15 - res.get_width(), TOP_BAR - 25))

def draw_buttons(pressed=None):
    for r, row in enumerate(BUTTONS):
        for c, label in enumerate(row):
            if not label: continue
            rect = pygame.Rect(
                GAP + c * (BUTTON_W + GAP),
                TOP_BAR + GAP + r * (BUTTON_H + GAP),
                BUTTON_W, BUTTON_H)
            if label in ['+', '-', '*', '/', '^']:
                color = COLORS["button_op"]
            elif label == '=':
                color = COLORS["button_eq"]
            elif label in ['C', '←']:
                color = COLORS["accent"]
            elif label in ['sin', 'cos', 'tan', 'ln', 'log', '√', 'π']:
                color = COLORS["button_func"]
            else:
                color = COLORS["button"]
            if pressed == (r, c):
                color = COLORS["pressed"]
            pygame.draw.rect(screen, color, rect, border_radius=8)
            txt = FONT.render(label, True, COLORS["button_text"])
            txt_rect = txt.get_rect(center=rect.center)
            screen.blit(txt, txt_rect)

def button_from_pos(mx, my):
    for r, row in enumerate(BUTTONS):
        for c, label in enumerate(row):
            if not label: continue
            rect = pygame.Rect(
                GAP + c * (BUTTON_W + GAP),
                TOP_BAR + GAP + r * (BUTTON_H + GAP),
                BUTTON_W, BUTTON_H)
            if rect.collidepoint(mx, my):
                return (r, c, label)
    return None

def button_from_label(lbl):
    for r, row in enumerate(BUTTONS):
        for c, label in enumerate(row):
            if label == lbl:
                return (r, c)
    return None

def append_input(current, label):
    # Don't allow two consecutive dots in a number
    if label == '.' and (not current or current[-1] == '.' or (len(current) > 1 and current[-2:] == '..')):
        return current
    # Don't allow multiple starting zeros (except '0.')
    if label == '0' and (not current or current == '0'):
        return current
    return current + label

def handle_button(label, current, result):
    if label in '0123456789.()+-*/^π':
        current = append_input(current, label)
        result = ''
    elif label in ['sin', 'cos', 'tan', 'ln', 'log', '√']:
        # Insert function with opening bracket
        if current and (current[-1].isdigit() or current[-1] == ')'):
            current += '*' + label + '('
        else:
            current += label + '('
        result = ''
    elif label == '=':
        result = safe_eval(current)
        current = result if result != "Error" else ''
    elif label == 'C':
        current = ''
        result = ''
    elif label == '←':
        current = current[:-1]
        result = ''
    return current, result

def main():
    current = ''
    result = ''
    pressed_button = None
    clock = pygame.time.Clock()

    while True:
        screen.fill(COLORS["background"])
        draw_display(current, result)
        draw_buttons(pressed_button)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                hit = button_from_pos(*event.pos)
                if hit:
                    r, c, label = hit
                    current, result = handle_button(label, current, result)
                    pressed_button = (r, c)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                pressed_button = None

            elif event.type == pygame.KEYDOWN:
                label = None
                if event.key in KEY_FUNCTIONS:
                    label = KEY_FUNCTIONS[event.key]
                elif event.unicode in '0123456789.()+-*/^':
                    label = event.unicode
                if label:
                    btn_pos = button_from_label(label)
                    current, result = handle_button(label, current, result)
                    pressed_button = btn_pos
            elif event.type == pygame.KEYUP:
                pressed_button = None

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
