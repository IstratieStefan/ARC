import pygame
from arc.core.config import config
import sys
import requests
import json
import threading

GEMINI_API_KEY = config.api.gemini_key
# Use gemini-1.5-flash for free tier (works with Google AI Studio keys)
GEMINI_ENDPOINT = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}'

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 320
BG_COLOR = config.colors.background
USER_COLOR = config.colors.tab_bg
BOT_COLOR = config.colors.text
INPUT_BG = config.colors.tab_bg
INPUT_BORDER = config.colors.text
INPUT_ACTIVE_BORDER = config.accent_color
INPUT_FG = config.colors.text
ANSWER_BG = config.colors.tab_bg
BORDER_RADIUS = 8

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('AI Chatbot')
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("Arial", 14)
INPUT_FONT = pygame.font.SysFont("Arial", 16)
TITLE_FONT = pygame.font.SysFont("Arial", 18, bold=True)


class TextBox:
    def __init__(self, rect, placeholder="Type your question...", max_lines=2):
        self.rect = pygame.Rect(rect)
        self.placeholder = placeholder
        self.text = ""
        self.active = True
        self.cursor_pos = 0
        self.cursor_visible = True
        self.cursor_timer = 0
        self.max_lines = max_lines
        self.scroll_offset = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)

        if self.active and event.type == pygame.TEXTINPUT:
            self.text = self.text[:self.cursor_pos] + event.text + self.text[self.cursor_pos:]
            self.cursor_pos += len(event.text)

    def update(self, dt):
        if self.active:
            self.cursor_timer += dt
            if self.cursor_timer >= 500:  # 500ms blink
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0

    def get_wrapped_lines_with_positions(self, text, font, max_width):
        """Get wrapped lines and character positions for proper cursor placement"""
        if not text:
            return [""], [0]

        words = text.split(' ')
        lines = []
        char_positions = []  # Start position of each line in the original text
        current_line = ""
        char_count = 0

        for word_idx, word in enumerate(words):
            test_line = current_line + (" " if current_line else "") + word

            if font.size(test_line)[0] <= max_width or not current_line:
                current_line = test_line
            else:
                # Current line is full, start new line
                lines.append(current_line)
                char_positions.append(char_count)
                char_count += len(current_line) + (1 if word_idx > 0 else 0)  # +1 for space
                current_line = word

        if current_line:
            lines.append(current_line)
            char_positions.append(char_count)

        return lines if lines else [""], char_positions

    def get_wrapped_lines(self, text, font, max_width):
        """Simple wrapper for compatibility"""
        lines, _ = self.get_wrapped_lines_with_positions(text, font, max_width)
        return lines

    def find_cursor_position(self, lines, char_positions, cursor_pos):
        """Find which line and position the cursor should be on"""
        if not lines or cursor_pos == 0:
            return 0, 0

        # Find which line the cursor belongs to
        for line_idx in range(len(lines) - 1, -1, -1):
            line_start = char_positions[line_idx]
            if cursor_pos >= line_start:
                # Cursor is on this line
                pos_in_line = cursor_pos - line_start
                # Handle spaces between words
                if line_idx > 0 and pos_in_line > 0:
                    pos_in_line = min(pos_in_line, len(lines[line_idx]))
                return line_idx, pos_in_line

        return 0, 0

    def draw(self, surface):
        # Draw background
        border_color = INPUT_ACTIVE_BORDER if self.active else INPUT_BORDER
        pygame.draw.rect(surface, INPUT_BG, self.rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=BORDER_RADIUS)

        # Calculate text area
        text_area = pygame.Rect(self.rect.x + 8, self.rect.y + 8,
                                self.rect.width - 16, self.rect.height - 16)

        # Get text to display
        if self.text:
            display_text = self.text
            text_color = INPUT_FG

            # Get wrapped lines with positions
            lines, char_positions = self.get_wrapped_lines_with_positions(
                display_text, INPUT_FONT, text_area.width
            )
        else:
            # Show placeholder
            display_text = self.placeholder
            text_color = (120, 120, 120)
            lines = self.get_wrapped_lines(display_text, INPUT_FONT, text_area.width)

        # Draw text lines
        line_height = INPUT_FONT.get_height() + 2
        for i, line in enumerate(lines):
            if i >= self.max_lines:
                break
            y_pos = text_area.y + i * line_height
            text_surface = INPUT_FONT.render(line, True, text_color)
            surface.blit(text_surface, (text_area.x, y_pos))

        # Draw cursor if active and we have text
        if self.active and self.cursor_visible and self.text:
            cursor_line, cursor_pos_in_line = self.find_cursor_position(
                lines, char_positions, self.cursor_pos
            )

            if cursor_line < len(lines) and cursor_line < self.max_lines:
                # Calculate cursor x position
                line_text = lines[cursor_line]
                text_before_cursor = line_text[:cursor_pos_in_line]
                cursor_x = text_area.x + INPUT_FONT.size(text_before_cursor)[0]
                cursor_y = text_area.y + cursor_line * line_height

                pygame.draw.line(surface, INPUT_FG,
                                 (cursor_x, cursor_y),
                                 (cursor_x, cursor_y + line_height), 1)


def draw_rounded_rect(surf, color, rect, radius):
    pygame.draw.rect(surf, color, rect, border_radius=radius)


def gemini_api(message_text):
    """Call Gemini API with proper formatting for free tier"""
    if not GEMINI_API_KEY or GEMINI_API_KEY in ['YOUR_GEMINI_API_KEY', 'your api key', '']:
        return "⚠️ Please set your Google AI Studio API key in config/arc.yaml\n\nSteps:\n1. Get a free API key from https://aistudio.google.com/app/apikey\n2. Open config/arc.yaml\n3. Find 'gemini_key' and replace 'your api key' with your actual key\n4. Save and restart the chatbot"

    headers = {
        'Content-Type': 'application/json',
    }

    # Proper payload format for Gemini 1.5 Flash (free tier)
    payload = {
        "contents": [{
            "parts": [{
                "text": message_text
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 1024,
        }
    }

    try:
        print(f"Sending request to: {GEMINI_ENDPOINT}")
        print(f"Payload: {json.dumps(payload, indent=2)}")

        response = requests.post(GEMINI_ENDPOINT,
                                 headers=headers,
                                 data=json.dumps(payload),
                                 timeout=30)

        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text[:500]}...")

        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                candidate = data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    return candidate['content']['parts'][0]['text']
                else:
                    return f"Unexpected response structure: {str(candidate)[:200]}"
            else:
                return f"No candidates in response: {str(data)[:200]}"
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith(
                'application/json') else response.text
            return f"API Error ({response.status_code}): {str(error_data)[:200]}"

    except requests.exceptions.Timeout:
        return "Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "Connection error. Check your internet connection."
    except json.JSONDecodeError as e:
        return f"JSON decode error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def render_multiline(text, font, color, width):
    lines = []
    words = text.split(' ')
    line = ''
    for word in words:
        test = line + word + ' '
        if font.size(test)[0] > width and line:
            lines.append(line.strip())
            line = word + ' '
        else:
            line = test
    if line:
        lines.append(line.strip())
    return [font.render(l, True, color) for l in lines]


def main():
    # Check if API key is configured
    if not GEMINI_API_KEY or GEMINI_API_KEY in ['YOUR_GEMINI_API_KEY', 'your api key', '']:
        answer_text = "⚠️ API Key Not Configured\n\nTo use the AI Chatbot:\n\n1. Get a free API key from:\n   https://aistudio.google.com/app/apikey\n\n2. Open config/arc.yaml\n\n3. Find the 'api:' section and replace 'your api key' with your Google AI Studio key\n\n4. Save and restart the chatbot"
    else:
        answer_text = "✨ Hello! I'm your AI assistant powered by Gemini 1.5 Flash.\n\nAsk me anything in the text box below - I can help with questions, writing, coding, math, and more!\n\nPress ENTER or click Send to submit your question."
    
    is_loading = False
    need_redraw = True
    scroll_offset = 0

    # UI Layout - Question textbox now at bottom
    margin = 10
    button_height = 30
    textbox_height = 50

    # Answer area at top
    answer_rect = pygame.Rect(
        margin,
        margin + 25,  # Space for title
        SCREEN_WIDTH - 2 * margin,
        SCREEN_HEIGHT - (margin + 25 + textbox_height + button_height + 20)
    )

    # Question textbox at bottom
    textbox = TextBox(
        (margin, answer_rect.bottom + 10, SCREEN_WIDTH - 2 * margin, textbox_height),
        "Ask me anything..."
    )

    # Send button
    send_button = pygame.Rect(
        SCREEN_WIDTH - 80 - margin,
        textbox.rect.bottom + 5,
        70, button_height
    )

    # Clear button
    clear_button = pygame.Rect(
        SCREEN_WIDTH - 160 - margin,
        textbox.rect.bottom + 5,
        70, button_height
    )

    def send_message():
        nonlocal answer_text, is_loading, need_redraw

        question = textbox.text.strip()
        if not question or is_loading:
            return

        is_loading = True
        answer_text = "Thinking..."
        need_redraw = True

        def get_answer():
            nonlocal answer_text, is_loading, need_redraw
            print(f"Sending question: {question}")
            response = gemini_api(question)
            print(f"Got response: {response[:100]}...")
            answer_text = response
            is_loading = False
            need_redraw = True

        thread = threading.Thread(target=get_answer)
        thread.daemon = True
        thread.start()

    while True:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_q and (event.mod & pygame.KMOD_CTRL):
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_RETURN and not is_loading:
                    send_message()
                elif event.key == pygame.K_UP:
                    scroll_offset = min(scroll_offset + 20, 0)
                    need_redraw = True
                elif event.key == pygame.K_DOWN:
                    scroll_offset -= 20
                    need_redraw = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if send_button.collidepoint(event.pos) and not is_loading:
                    send_message()
                elif clear_button.collidepoint(event.pos):
                    textbox.text = ""
                    textbox.cursor_pos = 0
                    # Reset to welcome message (check API key status)
                    if not GEMINI_API_KEY or GEMINI_API_KEY in ['YOUR_GEMINI_API_KEY', 'your api key', '']:
                        answer_text = "⚠️ API Key Not Configured\n\nTo use the AI Chatbot:\n\n1. Get a free API key from:\n   https://aistudio.google.com/app/apikey\n\n2. Open config/arc.yaml\n\n3. Find the 'api:' section and replace 'your api key' with your Google AI Studio key\n\n4. Save and restart the chatbot"
                    else:
                        answer_text = "✨ Hello! I'm your AI assistant powered by Gemini 1.5 Flash.\n\nAsk me anything in the text box below - I can help with questions, writing, coding, math, and more!\n\nPress ENTER or click Send to submit your question."
                    scroll_offset = 0
                    need_redraw = True
                elif answer_rect.collidepoint(event.pos):
                    if event.button == 4:  # Scroll up
                        scroll_offset = min(scroll_offset + 20, 0)
                        need_redraw = True
                    elif event.button == 5:  # Scroll down
                        scroll_offset -= 20
                        need_redraw = True

            textbox.handle_event(event)
            need_redraw = True

        textbox.update(dt)

        if need_redraw:
            screen.fill(BG_COLOR)

            # Draw title
            title = TITLE_FONT.render("AI Assistant", True, (255, 255, 255))
            screen.blit(title, (margin, margin))

            # Draw answer area
            pygame.draw.rect(screen, ANSWER_BG, answer_rect, border_radius=BORDER_RADIUS)
            pygame.draw.rect(screen, config.colors.tab_active, answer_rect, 2, border_radius=BORDER_RADIUS)

            # Draw answer text
            if answer_text:
                text_area = pygame.Rect(answer_rect.x + 10, answer_rect.y + 10,
                                        answer_rect.width - 20, answer_rect.height - 20)

                lines = render_multiline(answer_text, FONT, (255, 255, 255), text_area.width)
                line_height = FONT.get_height() + 3

                y_pos = text_area.y + scroll_offset
                for line_surface in lines:
                    if y_pos > text_area.bottom:
                        break
                    if y_pos + line_height > text_area.y:
                        screen.blit(line_surface, (text_area.x, y_pos))
                    y_pos += line_height

            # Draw question textbox
            textbox.draw(screen)

            # Draw buttons
            # Send button
            send_color = config.accent_color if not is_loading else (100, 100, 100)
            pygame.draw.rect(screen, send_color, send_button, border_radius=5)
            send_text = FONT.render("Send", True, (255, 255, 255))
            screen.blit(send_text, (send_button.centerx - send_text.get_width() // 2,
                                    send_button.centery - send_text.get_height() // 2))

            # Clear button
            pygame.draw.rect(screen, (80, 80, 80), clear_button, border_radius=5)
            clear_text = FONT.render("Clear", True, (255, 255, 255))
            screen.blit(clear_text, (clear_button.centerx - clear_text.get_width() // 2,
                                     clear_button.centery - clear_text.get_height() // 2))

            # Draw loading indicator
            if is_loading:
                loading_text = FONT.render("AI is thinking...", True, config.colors.text)
                screen.blit(loading_text, (margin + 10, textbox.rect.y - 35))

            pygame.display.flip()
            need_redraw = False


if __name__ == "__main__":
    main()