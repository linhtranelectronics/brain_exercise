# color_focus.py
# Game: Color Focus - focus training (Space = MATCH, Enter = NOT MATCH)
# Requirement: pygame
# Run: python color_focus.py

import pygame
import random
import os

# --- Config ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
ROUND_TIME_MS = 2000  # 2 seconds
MAX_MISTAKES = 3
HIGHSCORE_FILE = "highscore.txt"

# Colors (name -> RGB)
COLOR_MAP = {
    "RED": (220, 50, 50),
    "GREEN": (50, 200, 70),
    "BLUE": (60, 120, 220),
    "YELLOW": (240, 220, 60),
    "ORANGE": (255, 140, 40),
    "PURPLE": (160, 80, 200),
}

COLOR_NAMES = list(COLOR_MAP.keys())

# --- Utilities ---
def load_highscore():
    try:
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "r") as f:
                s = f.read().strip()
                return int(s) if s.isdigit() else 0
    except Exception:
        pass
    return 0

def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))
    except Exception:
        pass



# --- Game Functions ---
def new_round():
    # Return (actual_color_name, shown_text_name)
    actual = random.choice(COLOR_NAMES)

    # 50% match, 50% mismatch
    if random.random() < 0.5:
        shown = actual
    else:
        shown = random.choice([c for c in COLOR_NAMES if c != actual])
    return actual, shown

def draw_centered_text(text, font, y, color=(255,255,255)):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(SCREEN_WIDTH//2, y))
    screen.blit(surf, rect)

# --- Main Game Loop ---
def start_game_3():
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen

    # --- Pygame init ---
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Color Focus - Focus Training")
    clock = pygame.time.Clock()

    # Fonts
    TITLE_FONT = pygame.font.SysFont(None, 52)
    BIG_FONT = pygame.font.SysFont(None, 64)
    MED_FONT = pygame.font.SysFont(None, 36)
    SMALL_FONT = pygame.font.SysFont(None, 28)

    running = True
    game_state = "MENU"  # MENU, PLAYING, GAMEOVER
    score = 0
    mistakes = 0
    highscore = load_highscore()

    actual_color, shown_text = new_round()
    round_start = 0
    answered_this_round = False
    answered_correct = False

    while running:
        dt = clock.tick(FPS)
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                # MENU
                if game_state == "MENU":
                    if event.key == pygame.K_SPACE:
                        game_state = "PLAYING"
                        score = 0
                        mistakes = 0
                        actual_color, shown_text = new_round()
                        round_start = pygame.time.get_ticks()
                        answered_this_round = False
                        answered_correct = False

                # PLAYING
                elif game_state == "PLAYING":
                    if not answered_this_round:
                        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            is_match = (actual_color == shown_text)

                            if (is_match and event.key == pygame.K_SPACE) or (not is_match and event.key == pygame.K_RETURN):
                                score += 1
                                answered_correct = True
                            else:
                                mistakes += 1
                                answered_correct = False

                            answered_this_round = True

                # GAME OVER
                elif game_state == "GAMEOVER":
                    if event.key == pygame.K_SPACE:
                        game_state = "PLAYING"
                        score = 0
                        mistakes = 0
                        actual_color, shown_text = new_round()
                        round_start = pygame.time.get_ticks()
                        answered_this_round = False
                        answered_correct = False

        # Drawing
        screen.fill((25, 25, 25))

        # MENU SCREEN
        if game_state == "MENU":
            draw_centered_text("COLOR FOCUS", TITLE_FONT, SCREEN_HEIGHT//2 - 120)
            draw_centered_text("Focus training game (Space = MATCH, Enter = NOT MATCH)", MED_FONT, SCREEN_HEIGHT//2 - 50)
            draw_centered_text("Each round shows for 2 seconds. Max 3 mistakes.", SMALL_FONT, SCREEN_HEIGHT//2)
            draw_centered_text("Press SPACE to start", MED_FONT, SCREEN_HEIGHT//2 + 80)
            draw_centered_text(f"High Score: {highscore}", SMALL_FONT, SCREEN_HEIGHT//2 + 150)

        # GAMEPLAY
        elif game_state == "PLAYING":
            elapsed = now - round_start

            # Draw color box
            box_w = 400
            box_h = 250
            box_rect = pygame.Rect((SCREEN_WIDTH - box_w)//2, 100, box_w, box_h)
            pygame.draw.rect(screen, COLOR_MAP[actual_color], box_rect, border_radius=12)

            # Draw text
            draw_centered_text(shown_text, BIG_FONT, box_rect.bottom + 70, color=(255,255,255))

            # HUD
            time_left_ms = max(0, ROUND_TIME_MS - elapsed)
            time_left_s = time_left_ms / 1000.0
            draw_centered_text(
                f"Score: {score}    Mistakes: {mistakes}/{MAX_MISTAKES}    Time: {time_left_s:.2f}s",
                SMALL_FONT, 40
            )

            instr = "SPACE = MATCH     ENTER = NOT MATCH"
            surf_instr = SMALL_FONT.render(instr, True, (200,200,200))
            instr_rect = surf_instr.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 30))
            screen.blit(surf_instr, instr_rect)

            # Feedback
            if answered_this_round:
                fb_text = "CORRECT! +1" if answered_correct else "WRONG!"
                fb_color = (80, 200, 80) if answered_correct else (220, 80, 80)
                draw_centered_text(fb_text, MED_FONT, box_rect.centery, fb_color)

            # Check end of round
            if elapsed >= ROUND_TIME_MS:
                if not answered_this_round:
                    mistakes += 1

                if mistakes >= MAX_MISTAKES:
                    game_state = "GAMEOVER"
                    if score > highscore:
                        highscore = score
                        save_highscore(highscore)
                else:
                    actual_color, shown_text = new_round()
                    round_start = pygame.time.get_ticks()
                    answered_this_round = False
                    answered_correct = False

        # GAME OVER SCREEN
        elif game_state == "GAMEOVER":
            draw_centered_text("GAME OVER", TITLE_FONT, SCREEN_HEIGHT//2 - 80)
            draw_centered_text(f"Your Score: {score}", BIG_FONT, SCREEN_HEIGHT//2 - 10)
            draw_centered_text(f"High Score: {highscore}", MED_FONT, SCREEN_HEIGHT//2 + 50)
            draw_centered_text("Press SPACE to play again", MED_FONT, SCREEN_HEIGHT//2 + 120)

        pygame.display.flip()

    pygame.quit()
    return
