import pygame
import random
import sys

# --- Initialization ---
pygame.init()

# --- Game Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
CAPTION = "Arithmetic Dash: The Calculation Chain"

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 100, 255)

# --- Game Setup ---
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(CAPTION)
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 100)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)

# --- Sound Setup (Game Over Music ONLY) ---
try:
    GAME_OVER_MUSIC_FILE = 'gameover.mp3' # Ensure this file exists
    SOUNDS_LOADED = True
    pygame.mixer.init()
except pygame.error:
    print("Warning: Failed to initialize audio mixer. Game will run without Game Over music.")
    SOUNDS_LOADED = False

# --- Utility Functions ---

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)

def game_over_screen(score):
    if SOUNDS_LOADED:
        try:
            pygame.mixer.music.load("Downloads/gameover.mp3")
            pygame.mixer.music.play(-1) # Play music in a loop
        except pygame.error:
            print("Downloads/gameover.mp3")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if SOUNDS_LOADED:
                        pygame.mixer.music.stop()
                    return True # Restart game
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        screen.fill(BLACK)
        draw_text(screen, "TIME'S UP!", font_large, RED, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        draw_text(screen, f"Score: {score}", font_medium, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        draw_text(screen, "Press [SPACE] to Restart", font_small, YELLOW, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)
        draw_text(screen, "Press [ESC] to Quit", font_small, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4 + 40)
        
        pygame.display.flip()
        clock.tick(15)

# --- Game Logic Functions ---
def generate_equation(score):
    # Increase complexity based on score
    if score < 10:
        a = random.randrange(1, 9)
        b = random.randrange(1, 9)
        op = random.choice(['+'])
    elif score < 25:
        a = random.randrange(5, 15)
        b = random.randrange(1, 10)
        op = random.choice(['+', '-'])
    else:
        # Higher range and includes simple multiplication
        a = random.randrange(5, 20)
        b = random.randrange(1, 15)
        op = random.choice(['+', '-', '*'])

    if op == '+':
        result = a + b
    elif op == '-':
        # Ensure result is non-negative and keep it simple
        if a < b: a, b = b, a 
        result = a - b
    elif op == '*':
        # Keep multiplication small for quick mental math
        a = random.randrange(1, 6)
        b = random.randrange(1, 6)
        result = a * b
    
    # We only accept single digit answers (0-9)
    if result < 0 or result > 9:
        return generate_equation(score) # Regenerate if result is outside 0-9
        
    equation_str = f"{a} {op} {b}"
    return equation_str, result

# --- Main Game Loop ---
def main_game():
    if SOUNDS_LOADED:
        pygame.mixer.music.stop()

    score = 0
    
    # Timer variables
    MAX_TIME_MS = 2000 # 2 seconds base time limit
    time_left_ms = MAX_TIME_MS
    start_time = pygame.time.get_ticks()
    
    # Equation state
    equation_str, correct_answer = generate_equation(score)
    input_received = False
    
    game_running = True
    while game_running:
        current_time = pygame.time.get_ticks()
        
        # Calculate time left
        elapsed_time = current_time - start_time
        time_left_ms = MAX_TIME_MS - elapsed_time
        
        # 1. Input/Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key)
                
                if key_name.isdigit():
                    # Player answered with a digit key
                    player_answer = int(key_name)
                    
                    if player_answer == correct_answer:
                        # Correct Answer!
                        score += 1
                        input_received = True
                    else:
                        # Incorrect Answer!
                        game_running = False
                        break

        # 2. Update Game State
        
        # Check for Time Over
        if time_left_ms <= 0:
            game_running = False
            break

        # Check for successful input
        if input_received:
            # Generate new equation
            equation_str, correct_answer = generate_equation(score)
            
            # Reset and reduce timer for next round (increase difficulty)
            MAX_TIME_MS = max(500, MAX_TIME_MS - 50) # Minimum time limit of 0.5 seconds
            start_time = pygame.time.get_ticks()
            input_received = False
        
        # 3. Draw/Render
        screen.fill(BLACK)
        
        # Draw Score
        draw_text(screen, f"Score: {score}", font_medium, WHITE, SCREEN_WIDTH / 2, 50)
        
        # Draw Equation
        draw_text(screen, equation_str + " = ?", font_large, YELLOW, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50)
        
        # Draw Instruction
        draw_text(screen, "Type the single-digit answer (0-9) fast!", font_small, GREEN, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)

        # Draw Timer Bar (Visual focus on the shrinking bar)
        BAR_WIDTH = SCREEN_WIDTH * 0.8
        BAR_HEIGHT = 20
        
        time_ratio = max(0, time_left_ms / MAX_TIME_MS)
        current_bar_width = BAR_WIDTH * time_ratio
        
        # Determine color based on time left (Green -> Yellow -> Red)
        if time_ratio > 0.6:
            bar_color = BLUE
        elif time_ratio > 0.3:
            bar_color = YELLOW
        else:
            bar_color = RED
            
        # Background bar
        bg_rect = pygame.Rect((SCREEN_WIDTH - BAR_WIDTH) / 2, SCREEN_HEIGHT - 100, BAR_WIDTH, BAR_HEIGHT)
        pygame.draw.rect(screen, WHITE, bg_rect, 2) # Outline

        # Foreground time bar
        fg_rect = pygame.Rect((SCREEN_WIDTH - BAR_WIDTH) / 2, SCREEN_HEIGHT - 100, current_bar_width, BAR_HEIGHT)
        pygame.draw.rect(screen, bar_color, fg_rect)
        
        # Update display
        pygame.display.flip()
        
        # Control game speed
        clock.tick(60)

    # Game Over logic (Timer ran out or incorrect answer)
    return game_over_screen(score)

while True:
    main_game()