import pygame
import random
import time
import math

# Initialize Pygame
pygame.init()

# --- General Settings ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Memory Card Matching Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 150, 255)
DARK_BLUE = (0, 100, 200)
GREEN = (50, 200, 50)
RED = (255, 50, 50)
COVER_COLOR = (44, 62, 80) # Card back color

# Fonts
FONT_XL = pygame.font.Font(None, 72)
FONT_LG = pygame.font.Font(None, 48)
FONT_MD = pygame.font.Font(None, 36)
FONT_SM = pygame.font.Font(None, 24)

# List of Card Characters (Letters)
# Use the alphabet A-Z. Max 32 unique needed for 8x8 board.
ALPHABET = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
CARD_ICONS = ALPHABET + ['1', '2', '3', '4', '5', '6'] # Use extra characters if necessary for 8x8 (32 pairs)

# --- Level & Difficulty Settings ---
# Total 50 levels, split into difficulty groups
LEVEL_SETTINGS = {
    # (cols, rows, time_limit_seconds_per_pair)
    1:  (4, 4, 10),  # Easy (16 cards, 8 pairs)
    11: (5, 4, 8),   # Medium (20 cards, 10 pairs)
    21: (6, 5, 6),   # Hard (30 cards, 15 pairs)
    31: (7, 6, 5),   # Very Hard (42 cards, 21 pairs)
    41: (8, 6, 4),   # Expert (48 cards, 24 pairs)
}

def get_level_config(level):
    """Determines the configuration (cols, rows, time) based on the current level."""
    level = max(1, min(level, 50))
    cols, rows, time_pair = LEVEL_SETTINGS[1]
    
    # Find the appropriate difficulty setting
    for start_level, settings in sorted(LEVEL_SETTINGS.items()):
        if level >= start_level:
            cols, rows, time_pair = settings
        else:
            break
            
    # Time reduction penalty after every 5 levels to increase difficulty
    time_penalty = math.floor((level - 1) / 5)
    total_pairs = (cols * rows) / 2
    
    # Calculate initial time limit and apply penalty
    initial_time = total_pairs * time_pair
    time_limit = initial_time - (time_penalty * 5)
    
    # Ensure a minimum time limit (e.g., 30 seconds)
    return cols, rows, max(30, time_limit)

# --- Card Class ---
class Card:
    def __init__(self, icon, x, y, width, height, id):
        self.icon = icon
        self.rect = pygame.Rect(x, y, width, height)
        self.is_flipped = False
        self.is_matched = False
        self.id = id # Unique ID for pair matching
        self.font = pygame.font.Font(None, int(min(width, height) * 0.6))
        
    def draw(self, screen):
        # Draw the back face (not flipped)
        if not self.is_flipped and not self.is_matched:
            pygame.draw.rect(screen, COVER_COLOR, self.rect, 0, 8)
            pygame.draw.rect(screen, BLACK, self.rect, 3, 8)
            # Display question mark or logo
            text = FONT_LG.render("?", True, WHITE)
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)
            
        # Draw the front face (flipped or matched)
        else:
            pygame.draw.rect(screen, GRAY if self.is_matched else WHITE, self.rect, 0, 8)
            pygame.draw.rect(screen, GREEN if self.is_matched else BLACK, self.rect, 3, 8)
            
            # Display the icon (letter)
            text_surface = self.font.render(self.icon, True, BLACK)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def handle_click(self, pos):
        if self.rect.collidepoint(pos) and not self.is_flipped and not self.is_matched:
            self.is_flipped = True
            return True
        return False

# --- Game Class ---
class MemoryGame:
    def __init__(self, cols, rows, time_limit, current_level=1):
        self.cols = cols
        self.rows = rows
        self.board_width = self.cols * 100
        self.board_height = self.rows * 100
        self.card_width = 80
        self.card_height = 80
        self.padding = 20
        self.board = []
        self.flipped_cards = []
        self.matched_pairs = 0
        self.total_pairs = (cols * rows) // 2
        self.game_state = "PLAYING" # PLAYING, WON, LOST
        self.current_level = current_level
        
        # Time settings
        self.start_time = time.time()
        self.time_limit = time_limit # Time limit in seconds
        
        self.setup_board()

    def setup_board(self):
        """Creates the game board, shuffles card pairs."""
        
        # Determine the number of unique icons needed
        num_unique_icons = self.total_pairs
        
        # Select the necessary icons (letters)
        if num_unique_icons > len(CARD_ICONS):
             # This should not happen with current settings (max 24 pairs, 32 icons available)
             selected_icons = CARD_ICONS 
        else:
             selected_icons = CARD_ICONS[:num_unique_icons]

        card_icons = selected_icons * 2
        random.shuffle(card_icons)
        
        # Calculate board center position
        total_card_space_width = self.cols * self.card_width + (self.cols - 1) * self.padding
        total_card_space_height = self.rows * self.card_height + (self.rows - 1) * self.padding
        
        start_x = (SCREEN_WIDTH - total_card_space_width) // 2
        start_y = (SCREEN_HEIGHT - total_card_space_height) // 2

        self.board = []
        card_id = 0
        for row in range(self.rows):
            for col in range(self.cols):
                x = start_x + col * (self.card_width + self.padding)
                y = start_y + row * (self.card_height + self.padding)
                icon = card_icons.pop()
                self.board.append(Card(icon, x, y, self.card_width, self.card_height, card_id // 2))
                card_id += 1
                
    def handle_click(self, pos):
        if self.game_state != "PLAYING" or len(self.flipped_cards) == 2:
            return

        for card in self.board:
            if card.handle_click(pos):
                self.flipped_cards.append(card)
                
                # After flipping the second card, check the match
                if len(self.flipped_cards) == 2:
                    pygame.time.set_timer(CHECK_MATCH_EVENT, 1000) # Wait 1 second to check
                    
    def check_match(self):
        if len(self.flipped_cards) == 2:
            card1, card2 = self.flipped_cards
            
            if card1.icon == card2.icon:
                # Match found
                card1.is_matched = True
                card2.is_matched = True
                self.matched_pairs += 1
                
                # Check for win condition
                if self.matched_pairs == self.total_pairs:
                    self.game_state = "WON"
            else:
                # No match
                card1.is_flipped = False
                card2.is_flipped = False
                
            self.flipped_cards = []
            
    def update(self):
        if self.game_state == "PLAYING":
            elapsed_time = time.time() - self.start_time
            if elapsed_time > self.time_limit:
                self.game_state = "LOST"

    def draw(self, screen):
        # Draw cards
        for card in self.board:
            card.draw(screen)

        # Display info
        time_left = max(0, self.time_limit - (time.time() - self.start_time))
        
        # Use simple floor for time display
        time_text = FONT_MD.render(f"Time Left: {math.floor(time_left)}s", True, BLACK if time_left > 10 else RED)
        screen.blit(time_text, (10, 10))
        
        level_text = FONT_MD.render(f"Level: {self.current_level}/50", True, BLACK)
        screen.blit(level_text, (SCREEN_WIDTH - level_text.get_width() - 10, 10))
        
        match_text = FONT_MD.render(f"Matched: {self.matched_pairs}/{self.total_pairs}", True, BLACK)
        screen.blit(match_text, (10, 50))

        # Display results
        if self.game_state == "WON":
            self.draw_message(screen, "CONGRATULATIONS! LEVEL COMPLETE!", GREEN)
        elif self.game_state == "LOST":
            self.draw_message(screen, "GAME OVER! TIME EXPIRED!", RED)

    def draw_message(self, screen, message, color):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        text = FONT_XL.render(message, True, color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(text, text_rect)
        
        # Next/Restart Button
        button_text = "Next Level" if self.game_state == "WON" and self.current_level < 50 else "Back to Menu"
        button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 300, 60)
        pygame.draw.rect(screen, BLUE, button_rect, 0, 10)
        pygame.draw.rect(screen, DARK_BLUE, button_rect, 3, 10)
        
        btn_label = FONT_MD.render(button_text, True, WHITE)
        btn_label_rect = btn_label.get_rect(center=button_rect.center)
        screen.blit(btn_label, btn_label_rect)
        self.message_button_rect = button_rect

# --- Menu Class (Start Interface) ---
class Menu:
    def __init__(self):
        self.state = "START" # START, LEVEL_SELECTION
        self.buttons = []
        self.selected_level = 1 # Starting level
        
    def draw_start_screen(self, screen):
        screen.fill(GRAY)
        
        # Title
        title = FONT_XL.render("MEMORY MATCH GAME", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)
        
        # Start Button
        self.buttons = []
        start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 250, 300, 70)
        pygame.draw.rect(screen, GREEN, start_button_rect, 0, 10)
        pygame.draw.rect(screen, BLACK, start_button_rect, 3, 10)
        start_label = FONT_LG.render("START GAME", True, WHITE)
        start_label_rect = start_label.get_rect(center=start_button_rect.center)
        screen.blit(start_label, start_label_rect)
        self.buttons.append(("START", start_button_rect))

        # Level Selection Button
        level_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 350, 300, 70)
        pygame.draw.rect(screen, BLUE, level_button_rect, 0, 10)
        pygame.draw.rect(screen, DARK_BLUE, level_button_rect, 3, 10)
        level_label = FONT_LG.render(f"Level: {self.selected_level}/50", True, WHITE)
        level_label_rect = level_label.get_rect(center=level_button_rect.center)
        screen.blit(level_label, level_label_rect)
        self.buttons.append(("LEVEL", level_button_rect))

    def draw_level_selection(self, screen):
        screen.fill(GRAY)
        
        title = FONT_XL.render("SELECT LEVEL (1-50)", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title, title_rect)
        
        # Display current level
        current_level_text = FONT_XL.render(str(self.selected_level), True, BLUE)
        current_level_rect = current_level_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
        screen.blit(current_level_text, current_level_rect)
        
        # Decrease level button
        minus_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 220, 100, 60)
        pygame.draw.rect(screen, RED, minus_rect, 0, 10)
        minus_label = FONT_XL.render("-", True, WHITE)
        minus_label_rect = minus_label.get_rect(center=minus_rect.center)
        screen.blit(minus_label, minus_label_rect)
        self.buttons.append(("MINUS", minus_rect))
        
        # Increase level button
        plus_rect = pygame.Rect(SCREEN_WIDTH // 2 + 100, 220, 100, 60)
        pygame.draw.rect(screen, GREEN, plus_rect, 0, 10)
        plus_label = FONT_XL.render("+", True, WHITE)
        plus_label_rect = plus_label.get_rect(center=plus_rect.center)
        screen.blit(plus_label, plus_label_rect)
        self.buttons.append(("PLUS", plus_rect))

        # Back/Confirm button
        back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 400, 200, 60)
        pygame.draw.rect(screen, DARK_BLUE, back_rect, 0, 10)
        back_label = FONT_MD.render("Confirm", True, WHITE)
        back_label_rect = back_label.get_rect(center=back_rect.center)
        screen.blit(back_label, back_label_rect)
        self.buttons.append(("BACK", back_rect))
        
        # Display difficulty info
        cols, rows, time_limit = get_level_config(self.selected_level)
        diff_text = FONT_MD.render(f"Size: {cols}x{rows} | Time: {int(time_limit)}s", True, BLACK)
        diff_rect = diff_text.get_rect(center=(SCREEN_WIDTH // 2, 330))
        screen.blit(diff_text, diff_rect)

    def handle_click(self, pos):
        if self.state == "START":
            for name, rect in self.buttons:
                if rect.collidepoint(pos):
                    if name == "START":
                        return "START_GAME", self.selected_level
                    elif name == "LEVEL":
                        self.state = "LEVEL_SELECTION"
                        self.buttons = []
                        return "MENU", None
        
        elif self.state == "LEVEL_SELECTION":
            for name, rect in self.buttons:
                if rect.collidepoint(pos):
                    if name == "MINUS":
                        self.selected_level = max(1, self.selected_level - 1)
                    elif name == "PLUS":
                        self.selected_level = min(50, self.selected_level + 1)
                    elif name == "BACK":
                        self.state = "START"
                        self.buttons = []
                        return "MENU", None
        return "MENU", None

    def draw(self, screen):
        self.buttons = [] # Clear old buttons before redrawing
        if self.state == "START":
            self.draw_start_screen(screen)
        elif self.state == "LEVEL_SELECTION":
            self.draw_level_selection(screen)

# --- Main Loop ---
CHECK_MATCH_EVENT = pygame.USEREVENT + 1

def main():
    game_state = "MENU" # MENU, PLAYING
    current_game = None
    current_level = 1
    
    menu = Menu()
    
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_state == "MENU":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    action, level = menu.handle_click(event.pos)
                    if action == "START_GAME":
                        current_level = level
                        cols, rows, time_limit = get_level_config(current_level)
                        current_game = MemoryGame(cols, rows, time_limit, current_level)
                        game_state = "PLAYING"
                        
            elif game_state == "PLAYING":
                if current_game.game_state == "PLAYING":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        current_game.handle_click(event.pos)
                    
                    if event.type == CHECK_MATCH_EVENT:
                        current_game.check_match()
                        pygame.time.set_timer(CHECK_MATCH_EVENT, 0) # Turn off timer
                        
                elif current_game.game_state in ["WON", "LOST"]:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if current_game.message_button_rect.collidepoint(event.pos):
                            if current_game.game_state == "WON" and current_game.current_level < 50:
                                # Advance to the next level
                                current_level = current_game.current_level + 1
                                cols, rows, time_limit = get_level_config(current_level)
                                current_game = MemoryGame(cols, rows, time_limit, current_level)
                            else:
                                # Back to Menu
                                game_state = "MENU"
                                menu.selected_level = current_level # Update level for menu
                                
        # --- Update and Draw ---
        SCREEN.fill(WHITE)
        
        if game_state == "MENU":
            menu.draw(SCREEN)
        
        elif game_state == "PLAYING":
            current_game.update()
            current_game.draw(SCREEN)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

while True:
    # To use the pygame library, you need to install it:
    # pip install pygame
    main()