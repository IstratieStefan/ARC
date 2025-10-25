import pygame
import os
import sys
import subprocess
import threading
import time
from config import config

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 320

# Simple color scheme
BG_COLOR = config.colors.background
CARD_BG = config.tab_bg
CARD_BORDER = (60, 65, 85)
BUTTON_COLOR = config.tab_bg
SELECTED_COLOR = config.accent_color
TEXT_COLOR = (255, 255, 255)
GRAY_TEXT = (180, 180, 180)
ERROR_COLOR = (255, 100, 100)
SUCCESS_COLOR = (100, 255, 150)
WARNING_COLOR = (255, 200, 100)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('BadUSB Script Loader')
clock = pygame.time.Clock()

# Fonts
try:
    FONT = pygame.font.Font(None, 20)
    TITLE_FONT = pygame.font.Font(None, 28)
    SMALL_FONT = pygame.font.Font(None, 16)
except:
    FONT = pygame.font.SysFont("Arial", 18)
    TITLE_FONT = pygame.font.SysFont("Arial", 24, bold=True)
    SMALL_FONT = pygame.font.SysFont("Arial", 14)

# Script directory
SCRIPT_DIR = os.path.expanduser(config.badusb_dir)
if not os.path.exists(SCRIPT_DIR):
    os.makedirs(SCRIPT_DIR)


def draw_rounded_rect(surface, color, rect, radius=8):
    """Draw rounded rectangle with fallback"""
    try:
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    except:
        pygame.draw.rect(surface, color, rect)


class ScriptItem:
    def __init__(self, filename, path):
        self.filename = filename
        self.path = path
        self.name = filename[:-3] if filename.endswith('.sh') else filename
        self.description = self.get_description()

    def get_description(self):
        """Extract description from script"""
        try:
            with open(self.path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[:10]
                for line in lines:
                    line = line.strip()
                    if line.startswith('# Description:'):
                        return line[14:].strip()
                    elif line.startswith('# DESC:'):
                        return line[7:].strip()
                    elif line.startswith('# ') and len(line) > 10 and 'bin/bash' not in line:
                        return line[2:].strip()
                return "No description"
        except:
            return "Error reading script"


class BadUSBLoader:
    def __init__(self):
        self.scripts = []
        self.selected_index = 0
        self.mode = "list"  # "list", "menu"
        self.menu_selected = 0
        self.status_message = "Ready"
        self.status_color = TEXT_COLOR
        self.status_timer = time.time()
        self.is_running = False
        self.current_script = ""

        # Menu options
        self.menu_options = ["Run Script", "New Script", "Delete Script", "Refresh", "Exit"]

        self.load_scripts()

    def load_scripts(self):
        """Load scripts"""
        self.scripts = []
        try:
            if os.path.exists(SCRIPT_DIR):
                for filename in sorted(os.listdir(SCRIPT_DIR)):
                    if filename.endswith('.sh'):
                        path = os.path.join(SCRIPT_DIR, filename)
                        self.scripts.append(ScriptItem(filename, path))

            if self.scripts and self.selected_index >= len(self.scripts):
                self.selected_index = 0

            self.set_status(f"Loaded {len(self.scripts)} scripts", SUCCESS_COLOR)
        except Exception as e:
            self.set_status(f"Error: {str(e)[:30]}", ERROR_COLOR)

    def set_status(self, message, color=None):
        """Set status message"""
        self.status_message = message
        self.status_color = color or TEXT_COLOR
        self.status_timer = time.time()

    def run_script(self):
        """Execute selected script"""
        if not self.scripts or self.is_running:
            return

        script = self.scripts[self.selected_index]
        self.is_running = True
        self.current_script = script.name
        self.set_status(f"Running {script.name}...", WARNING_COLOR)

        def execute():
            try:
                subprocess.run(['chmod', '+x', script.path], check=True)

                result = subprocess.run(
                    ['bash', script.path],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=os.path.dirname(script.path)
                )

                if result.returncode == 0:
                    self.set_status(f"Success: {script.name}", SUCCESS_COLOR)
                else:
                    error = result.stderr.strip()[:25] if result.stderr else "Unknown error"
                    self.set_status(f"Failed: {error}", ERROR_COLOR)

            except subprocess.TimeoutExpired:
                self.set_status(f"Timeout: {script.name}", ERROR_COLOR)
            except Exception as e:
                self.set_status(f"Error: {str(e)[:25]}", ERROR_COLOR)
            finally:
                self.is_running = False
                self.current_script = ""

        thread = threading.Thread(target=execute)
        thread.daemon = True
        thread.start()

    def create_new_script(self):
        """Create new script"""
        try:
            existing = [f for f in os.listdir(SCRIPT_DIR) if f.startswith('script_')]
            script_num = len(existing) + 1
            filename = f"script_{script_num:03d}.sh"
            filepath = os.path.join(SCRIPT_DIR, filename)

            template = f"""#!/bin/bash
# Description: BadUSB Script {script_num}
# Author: Your Name
# Date: 2025-07-22

echo "BadUSB script {script_num} executed at $(date)"

# Add your commands here
# Example: echo "Hello World" > /tmp/badusb_test.txt

echo "Script completed"
"""

            with open(filepath, 'w') as f:
                f.write(template)

            os.chmod(filepath, 0o755)
            self.load_scripts()

            # Select the new script
            for i, script in enumerate(self.scripts):
                if script.filename == filename:
                    self.selected_index = i
                    break

            self.set_status(f"Created {filename}", SUCCESS_COLOR)

        except Exception as e:
            self.set_status(f"Create failed: {str(e)[:25]}", ERROR_COLOR)

    def delete_script(self):
        """Delete selected script"""
        if not self.scripts:
            return

        script = self.scripts[self.selected_index]
        try:
            os.remove(script.path)
            self.set_status(f"Deleted {script.name}", SUCCESS_COLOR)
            self.load_scripts()
        except Exception as e:
            self.set_status(f"Delete failed: {str(e)[:25]}", ERROR_COLOR)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.mode == "menu":
                    self.mode = "list"
                else:
                    return False

            elif self.mode == "list":
                if event.key == pygame.K_UP and self.scripts:
                    self.selected_index = max(0, self.selected_index - 1)

                elif event.key == pygame.K_DOWN and self.scripts:
                    self.selected_index = min(len(self.scripts) - 1, self.selected_index + 1)

                elif event.key == pygame.K_RETURN:
                    if self.scripts:
                        self.mode = "menu"
                        self.menu_selected = 0
                    else:
                        self.create_new_script()

            elif self.mode == "menu":
                if event.key == pygame.K_UP:
                    self.menu_selected = max(0, self.menu_selected - 1)

                elif event.key == pygame.K_DOWN:
                    self.menu_selected = min(len(self.menu_options) - 1, self.menu_selected + 1)

                elif event.key == pygame.K_RETURN:
                    self.execute_menu_action()

        return True

    def execute_menu_action(self):
        """Execute selected menu action"""
        action = self.menu_options[self.menu_selected]

        if action == "Run Script" and not self.is_running:
            self.run_script()
            self.mode = "list"
        elif action == "New Script":
            self.create_new_script()
            self.mode = "list"
        elif action == "Delete Script":
            self.delete_script()
            self.mode = "list"
        elif action == "Refresh":
            self.load_scripts()
            self.mode = "list"
        elif action == "Exit":
            pygame.quit()
            sys.exit()

    def draw_header(self, surface):
        """Draw header"""
        # Title
        title = TITLE_FONT.render("BadUSB Script Loader", True, TEXT_COLOR)
        surface.blit(title, (15, 10))

        # Script count
        count_text = SMALL_FONT.render(f"{len(self.scripts)} scripts", True, GRAY_TEXT)
        surface.blit(count_text, (15, 35))

        # Running indicator
        if self.is_running:
            running_text = FONT.render(f"RUNNING: {self.current_script}", True, WARNING_COLOR)
            surface.blit(running_text, (15, 55))

    def draw_script_list(self, surface):
        """Draw script list with more padding"""
        start_y = 80
        item_height = 45  # Increased from 35 to 45
        padding_x = 20   # Increased horizontal padding
        padding_y = 8    # Increased vertical padding

        if not self.scripts:
            # No scripts
            no_scripts = FONT.render("No scripts found", True, TEXT_COLOR)
            surface.blit(no_scripts, (padding_x, start_y + 20))

            help_text = SMALL_FONT.render("Press ENTER to create a new script", True, GRAY_TEXT)
            surface.blit(help_text, (padding_x, start_y + 45))
            return

        # Draw scripts
        for i, script in enumerate(self.scripts):
            y_pos = start_y + i * item_height

            # Skip if off screen
            if y_pos > SCREEN_HEIGHT - 100:
                break

            # Background for selected item with more padding
            if i == self.selected_index:
                rect = pygame.Rect(10, y_pos - padding_y, SCREEN_WIDTH - 20, item_height - 5)
                draw_rounded_rect(surface, SELECTED_COLOR, rect)
                text_color = TEXT_COLOR
            else:
                text_color = GRAY_TEXT

            # Script name with more padding
            name_text = FONT.render(script.name[:30], True, text_color)
            surface.blit(name_text, (padding_x, y_pos))

            # Description with more padding and spacing
            desc_text = SMALL_FONT.render(script.description[:50], True, text_color)
            surface.blit(desc_text, (padding_x, y_pos + 22))  # Increased from 18 to 22

    def draw_menu(self, surface):
        """Draw action menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # Menu background
        menu_width = 200
        menu_height = len(self.menu_options) * 35 + 20
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2

        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        draw_rounded_rect(surface, CARD_BG, menu_rect)

        # Menu title
        if self.scripts:
            script_name = self.scripts[self.selected_index].name[:15]
            title = FONT.render(f"Actions: {script_name}", True, TEXT_COLOR)
        else:
            title = FONT.render("Actions", True, TEXT_COLOR)

        title_rect = title.get_rect(centerx=menu_rect.centerx, y=menu_y + 10)
        surface.blit(title, title_rect)

        # Menu options
        for i, option in enumerate(self.menu_options):
            y_pos = menu_y + 40 + i * 30

            # Skip unavailable options
            if option == "Run Script" and (not self.scripts or self.is_running):
                text_color = (100, 100, 100)
            elif option == "Delete Script" and not self.scripts:
                text_color = (100, 100, 100)
            else:
                text_color = TEXT_COLOR

            # Highlight selected option
            if i == self.menu_selected:
                option_rect = pygame.Rect(menu_x + 5, y_pos - 2, menu_width - 10, 25)
                draw_rounded_rect(surface, BUTTON_COLOR, option_rect)
                text_color = TEXT_COLOR

            option_text = FONT.render(option, True, text_color)
            option_rect = option_text.get_rect(centerx=menu_rect.centerx, y=y_pos)
            surface.blit(option_text, option_rect)

    def draw_footer(self, surface):
        """Draw footer with status and controls"""
        footer_y = SCREEN_HEIGHT - 60

        # Status
        if time.time() - self.status_timer > 5:
            self.status_message = "Ready"
            self.status_color = TEXT_COLOR

        status_text = FONT.render(self.status_message, True, self.status_color)
        surface.blit(status_text, (15, footer_y))

        # Controls
        if self.mode == "list":
            if self.scripts:
                controls = "UP/DOWN: Select | ENTER: Actions | ESC: Exit"
            else:
                controls = "ENTER: Create Script | ESC: Exit"
        else:
            controls = "UP/DOWN: Select | ENTER: Execute | ESC: Back"

        control_text = SMALL_FONT.render(controls, True, GRAY_TEXT)
        surface.blit(control_text, (15, footer_y + 25))

    def draw(self, surface):
        surface.fill(BG_COLOR)

        self.draw_header(surface)
        self.draw_script_list(surface)
        self.draw_footer(surface)

        if self.mode == "menu":
            self.draw_menu(surface)


def main():
    print(f"BadUSB Script Loader")
    print(f"Script directory: {SCRIPT_DIR}")

    loader = BadUSBLoader()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                if not loader.handle_event(event):
                    running = False

        loader.draw(screen)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()