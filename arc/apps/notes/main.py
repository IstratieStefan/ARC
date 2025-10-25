import pygame
import sys
import os
from arc.core.config import config

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

LEFT_PAD = 10
TOP_PAD = 10
LINE_HEIGHT = 24
RIGHT_PAD = 10

def wrap_line(text, font, max_width):
    """Wrap a single line of text to fit in max_width (returns list of substrings)"""
    words = text.split(' ')
    lines = []
    current = ""
    for word in words:
        test = current + (" " if current else "") + word
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            # If a word is too long, split it by characters
            while font.size(word)[0] > max_width:
                # Find how many characters fit
                for i in range(1, len(word)+1):
                    if font.size(word[:i])[0] > max_width:
                        break
                lines.append(word[:i-1])
                word = word[i-1:]
            current = word
    if current:
        lines.append(current)
    return lines

def build_visual_lines(lines, font, area_width):
    """
    Returns a list of (logical_row, logical_col_start, string) for each visible visual line.
    """
    visual_lines = []
    for row, line in enumerate(lines):
        wraps = wrap_line(line, font, area_width)
        col_start = 0
        for wrap in wraps:
            visual_lines.append((row, col_start, wrap))
            col_start += len(wrap)
    return visual_lines

def find_cursor_visual_pos(lines, font, area_width, cursor_row, cursor_col):
    """
    Find (visual_idx, cursor_x, cursor_y) for cursor drawing.
    """
    visual_lines = []
    cursor_visual_idx = 0
    x_offset = 0
    y_offset = 0
    found = False

    for row, line in enumerate(lines):
        wraps = wrap_line(line, font, area_width)
        col_start = 0
        for wrap in wraps:
            start = col_start
            end = col_start + len(wrap)
            if not found and row == cursor_row and start <= cursor_col <= end:
                cursor_visual_idx = len(visual_lines)
                x_offset = font.size(wrap[:cursor_col - start])[0]
                found = True
            visual_lines.append((row, start, wrap))
            col_start = end
    if not found:
        # End of document (cursor after last character)
        cursor_visual_idx = len(visual_lines) - 1
        x_offset = font.size(visual_lines[-1][2])[0]
    y_offset = cursor_visual_idx * LINE_HEIGHT
    return cursor_visual_idx, x_offset, y_offset, visual_lines

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
        area_width = width - LEFT_PAD - RIGHT_PAD
        max_visual_lines = (height - TOP_PAD) // LINE_HEIGHT

        # Get all visual lines and cursor position
        cursor_visual_idx, cursor_x, cursor_y, visual_lines = find_cursor_visual_pos(
            lines, FONT, area_width, cursor_row, cursor_col
        )

        # Clamp scroll for visual lines
        scroll = max(0, min(scroll, max(0, len(visual_lines) - max_visual_lines)))
        visible = visual_lines[scroll:scroll+max_visual_lines]

        # Draw visible lines
        for i, (row, col_start, wrap) in enumerate(visible):
            text = FONT.render(wrap, True, FG)
            screen.blit(text, (LEFT_PAD, TOP_PAD + i * LINE_HEIGHT))

        # Draw cursor (blinking)
        blink = (blink + 1) % 60
        if blink < 40:
            if scroll <= cursor_visual_idx < scroll + max_visual_lines:
                cursor_y_screen = TOP_PAD + (cursor_visual_idx - scroll) * LINE_HEIGHT
                pygame.draw.rect(
                    screen, CURSOR_COLOR,
                    (LEFT_PAD + cursor_x, cursor_y_screen, 2, FONT.get_height())
                )

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
                    # Move up a visual line, recompute logical line/col
                    cursor_visual_idx, _, _, visual_lines = find_cursor_visual_pos(
                        lines, FONT, area_width, cursor_row, cursor_col
                    )
                    if cursor_visual_idx > 0:
                        prev_row, prev_col_start, prev_wrap = visual_lines[cursor_visual_idx - 1]
                        cursor_row = prev_row
                        cursor_col = min(prev_col_start + len(prev_wrap),
                                         prev_col_start + (cursor_col - visual_lines[cursor_visual_idx][1]))
                        if cursor_visual_idx - 1 < scroll:
                            scroll = max(0, scroll - SCROLL_STEP)
                elif event.key == pygame.K_DOWN:
                    cursor_visual_idx, _, _, visual_lines = find_cursor_visual_pos(
                        lines, FONT, area_width, cursor_row, cursor_col
                    )
                    if cursor_visual_idx < len(visual_lines) - 1:
                        next_row, next_col_start, next_wrap = visual_lines[cursor_visual_idx + 1]
                        cursor_row = next_row
                        cursor_col = min(next_col_start + len(next_wrap),
                                         next_col_start + (cursor_col - visual_lines[cursor_visual_idx][1]))
                        if cursor_visual_idx + 1 >= scroll + max_visual_lines:
                            scroll += SCROLL_STEP
                elif event.key == pygame.K_PAGEUP:
                    scroll = max(0, scroll - max_visual_lines)
                elif event.key == pygame.K_PAGEDOWN:
                    scroll = min(max(0, len(visual_lines) - max_visual_lines), scroll + max_visual_lines)
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

        # Clamp logical cursor position
        if cursor_row < 0: cursor_row = 0
        if cursor_row >= len(lines): cursor_row = len(lines) - 1
        if cursor_col < 0: cursor_col = 0
        if cursor_col > len(lines[cursor_row]): cursor_col = len(lines[cursor_row])
        # Clamp scroll
        scroll = max(0, min(scroll, max(0, len(visual_lines) - max_visual_lines)))

        pygame.display.flip()
        pygame.time.Clock().tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
