import pygame
import random

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

# --- Game Globals ---
screen = None
clock = None
font_large = None
font_medium = None
font_small = None

# --- Sound Setup ---
SOUNDS_LOADED = False
try:
    pygame.mixer.init()
    SOUNDS_LOADED = True
except pygame.error:
    print("Warning: Audio init failed.")

# --- Utility ---
def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, rect)

# --- GAME START SCREEN (NEW) ---
def start_instruction_screen():
    """Hiển thị màn hình hướng dẫn (Start Screen) trước khi vào game."""
    global screen, clock, font_large, font_medium, font_small

    show_screen = True

    while show_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False

        screen.fill(BLACK)

        draw_text(screen, "ARITHMETIC DASH", font_large, YELLOW, SCREEN_WIDTH / 2, 100)
        draw_text(screen, "How to Play:", font_medium, WHITE, SCREEN_WIDTH / 2, 200)
        draw_text(screen, "- You will see a math equation.", font_small, WHITE, SCREEN_WIDTH / 2, 260)
        draw_text(screen, "- Type the correct answer (0-9) quickly!", font_small, WHITE, SCREEN_WIDTH / 2, 300)
        draw_text(screen, "- You have limited time for each question.", font_small, WHITE, SCREEN_WIDTH / 2, 340)

        draw_text(screen, "Press SPACE to start", font_small, GREEN, SCREEN_WIDTH / 2, 450)
        draw_text(screen, "Press ESC to exit", font_small, RED, SCREEN_WIDTH / 2, 490)

        pygame.display.flip()
        clock.tick(30)

    return False

# --- GAME OVER SCREEN ---
def game_over_screen(score):
    global screen, clock, font_large, font_medium, font_small, SOUNDS_LOADED
    
    if SOUNDS_LOADED:
        try:
            pygame.mixer.music.load("Downloads/gameover.mp3")
            pygame.mixer.music.play(-1)
        except:
            pass

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if SOUNDS_LOADED: pygame.mixer.music.stop()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if SOUNDS_LOADED: pygame.mixer.music.stop()
                    return True
                if event.key == pygame.K_ESCAPE:
                    if SOUNDS_LOADED: pygame.mixer.music.stop()
                    return False

        screen.fill(BLACK)
        draw_text(screen, "TIME'S UP!", font_large, RED, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        draw_text(screen, f"Score: {score}", font_medium, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        draw_text(screen, "Press SPACE to Restart", font_small, YELLOW, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3/4)
        draw_text(screen, "Press ESC to Exit", font_small, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3/4 + 40)

        pygame.display.flip()
        clock.tick(20)
    
    return False

# --- Equation Generator ---
def generate_equation(score):
    if score < 10:
        a = random.randrange(1, 9)
        b = random.randrange(1, 9)
        op = '+'
    elif score < 25:
        a = random.randrange(5, 15)
        b = random.randrange(1, 10)
        op = random.choice(['+', '-'])
    else:
        a = random.randrange(1, 6)
        b = random.randrange(1, 6)
        op = random.choice(['+', '-', '*'])

    if op == '+': result = a + b
    elif op == '-':
        if a < b: a, b = b, a
        result = a - b
    else:  # multiply
        result = a * b

    if result < 0 or result > 9:
        return generate_equation(score)

    return f"{a} {op} {b}", result

# --- MAIN GAME LOOP ---
def main_game():
    global screen, clock

    score = 0
    MAX_TIME_MS = 2000
    start_time = pygame.time.get_ticks()

    equation_str, correct_answer = generate_equation(score)
    input_received = False
    game_running = True

    while game_running:
        current = pygame.time.get_ticks()
        time_left = MAX_TIME_MS - (current - start_time)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
                break

            if event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key).isdigit():
                    if int(pygame.key.name(event.key)) == correct_answer:
                        score += 1
                        input_received = True
                    else:
                        game_running = False
                        break

        if not game_running:
            break

        if time_left <= 0:
            break

        if input_received:
            equation_str, correct_answer = generate_equation(score)
            MAX_TIME_MS = max(500, MAX_TIME_MS - 50)
            start_time = pygame.time.get_ticks()
            input_received = False

        # DRAW
        screen.fill(BLACK)
        draw_text(screen, f"Score: {score}", font_medium, WHITE, SCREEN_WIDTH/2, 50)
        draw_text(screen, equation_str + " = ?", font_large, YELLOW, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        # Timer Bar
        BAR_WIDTH = SCREEN_WIDTH * 0.8
        BAR_HEIGHT = 20
        ratio = max(0, time_left / MAX_TIME_MS)
        color = BLUE if ratio > 0.6 else YELLOW if ratio > 0.3 else RED

        pygame.draw.rect(screen, WHITE,
            pygame.Rect((SCREEN_WIDTH - BAR_WIDTH)/2, SCREEN_HEIGHT - 120, BAR_WIDTH, BAR_HEIGHT), 2)
        pygame.draw.rect(screen, color,
            pygame.Rect((SCREEN_WIDTH - BAR_WIDTH)/2, SCREEN_HEIGHT - 120, BAR_WIDTH * ratio, BAR_HEIGHT))

        pygame.display.flip()
        clock.tick(60)

    if time_left <= 0:
        return game_over_screen(score)

    return False

# --- PUBLIC ENTRY POINT ---
def start_game_1():
    pygame.init()
    pygame.font.init()

    global screen, clock, font_large, font_medium, font_small
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption(CAPTION)

    clock = pygame.time.Clock()
    font_large = pygame.font.Font(None, 80)
    font_medium = pygame.font.Font(None, 50)
    font_small = pygame.font.Font(None, 32)

    # --- NEW: Start Screen ---
    if not start_instruction_screen():
        pygame.quit()
        return

    # --- Game Loop ---
    running = True
    while running:
        restart = main_game()
        if not restart:
            running = False

    pygame.quit()
    return
