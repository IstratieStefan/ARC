import pygame
import sys
import os
from config import config

# --- For file dialog ---
import tkinter as tk
from tkinter import filedialog

def pick_file():
    root = tk.Tk()
    root.withdraw()
    filetypes = [
        ('Text files', '*.txt *.md *.log'),
        ('All files', '*.*')
    ]
    filename = filedialog.asksaveasfilename(
        title="Choose notes file",
        initialfile="notes.txt",
        defaultextension=".txt",
        filetypes=filetypes
    )
    root.destroy()
    return filename

def load_notes(filename):
    if filename and os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read().splitlines()
    else:
        return [""]

def save_notes(filename, lines):
    if filename:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

WIDTH, HEIGHT = 480, 320
BG = config.colors.background
FG = config.colors.text
CURSOR_COLOR = config.accent_color
SCROLL_STEP = 1

pygame.init()
FONT = pygame.font.SysFont("consolas", 20)

def main():
    filename = pick_file()
    if not filename:
        print("No file selected. Exiting.")
        sys.exit()

    lines = load_notes(filename)
    cursor_row, cursor_col = len(lines) - 1, len(lines[-1])
    scroll = 0
    running = True
    blink = 0
    width, height = WIDTH, HEIGHT
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)

    while running:
        screen.fill(BG)
        max_lines = height // 24
        visible_lines = lines[scroll:scroll+max_lines]

        # Draw lines
        for i, line in enumerate(visible_lines):
            text = FONT.render(line, True, FG)
            screen.blit(text, (10, 10 + i * 24))

        # Draw cursor (blinking)
        blink = (blink + 1) % 60
        if blink < 40:
            if scroll <= cursor_row < scroll + max_lines:
                row = cursor_row - scroll
                left = FONT.size(lines[cursor_row][:cursor_col])[0]
                pygame.draw.rect(screen, CURSOR_COLOR, (10 + left, 10 + row * 24, 2, 22))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_notes(filename, lines)
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_notes(filename, lines)
                    running = False
                elif event.key == pygame.K_RETURN:
                    before = lines[cursor_row][:cursor_col]
                    after = lines[cursor_row][cursor_col:]
                    lines[cursor_row] = before
                    lines.insert(cursor_row + 1, after)
                    cursor_row += 1
                    cursor_col = 0
                elif event.key == pygame.K_BACKSPACE:
                    if cursor_col > 0:
                        lines[cursor_row] = lines[cursor_row][:cursor_col-1] + lines[cursor_row][cursor_col:]
                        cursor_col -= 1
                    elif cursor_row > 0:
                        cursor_col = len(lines[cursor_row - 1])
                        lines[cursor_row - 1] += lines[cursor_row]
                        del lines[cursor_row]
                        cursor_row -= 1
                elif event.key == pygame.K_LEFT:
                    if cursor_col > 0:
                        cursor_col -= 1
                    elif cursor_row > 0:
                        cursor_row -= 1
                        cursor_col = len(lines[cursor_row])
                elif event.key == pygame.K_RIGHT:
                    if cursor_col < len(lines[cursor_row]):
                        cursor_col += 1
                    elif cursor_row < len(lines) - 1:
                        cursor_row += 1
                        cursor_col = 0
                elif event.key == pygame.K_UP:
                    if cursor_row > 0:
                        cursor_row -= 1
                        cursor_col = min(cursor_col, len(lines[cursor_row]))
                        if cursor_row < scroll:
                            scroll = max(0, scroll - SCROLL_STEP)
                elif event.key == pygame.K_DOWN:
                    if cursor_row < len(lines) - 1:
                        cursor_row += 1
                        cursor_col = min(cursor_col, len(lines[cursor_row]))
                        if cursor_row >= scroll + max_lines:
                            scroll += SCROLL_STEP
                elif event.key == pygame.K_PAGEUP:
                    scroll = max(0, scroll - max_lines)
                    cursor_row = max(0, cursor_row - max_lines)
                    cursor_col = min(cursor_col, len(lines[cursor_row]))
                elif event.key == pygame.K_PAGEDOWN:
                    scroll = min(max(0, len(lines) - max_lines), scroll + max_lines)
                    cursor_row = min(len(lines) - 1, cursor_row + max_lines)
                    cursor_col = min(cursor_col, len(lines[cursor_row]))
                elif event.key == pygame.K_HOME:
                    cursor_col = 0
                elif event.key == pygame.K_END:
                    cursor_col = len(lines[cursor_row])
                else:
                    if event.unicode and event.key != pygame.K_TAB:
                        lines[cursor_row] = lines[cursor_row][:cursor_col] + event.unicode + lines[cursor_row][cursor_col:]
                        cursor_col += len(event.unicode)
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.size
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        # Clamp scroll and cursor
        if cursor_row < 0: cursor_row = 0
        if cursor_row >= len(lines): cursor_row = len(lines) - 1
        if cursor_col < 0: cursor_col = 0
        if cursor_col > len(lines[cursor_row]): cursor_col = len(lines[cursor_row])
        scroll = max(0, min(scroll, max(0, len(lines) - max_lines)))

        pygame.display.flip()
        pygame.time.Clock().tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
