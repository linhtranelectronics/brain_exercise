import pygame
import random
# Không cần import sys nữa vì chúng ta không gọi sys.exit()



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
# Khởi tạo các biến global cần thiết
# Khởi tạo màn hình, clock, và fonts chỉ một lần khi hàm start_game_1 được gọi
screen = None 
clock = None
font_large = None
font_medium = None
font_small = None

# --- Sound Setup (Game Over Music ONLY) ---
SOUNDS_LOADED = False
try:
    pygame.mixer.init()
    SOUNDS_LOADED = True
except pygame.error:
    print("Warning: Failed to initialize audio mixer. Game will run without Game Over music.")

# --- Utility Functions ---

def draw_text(surface, text, font, color, x, y):
    """Vẽ chữ lên màn hình."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)

def game_over_screen(score):
    """Màn hình Game Over. Trả về True nếu muốn Restart, False nếu muốn Quit."""
    global screen, clock, font_large, font_medium, font_small, SOUNDS_LOADED
    
    if SOUNDS_LOADED:
        try:
            # Lưu ý: Cần đảm bảo file 'Downloads/gameover.mp3' tồn tại
            pygame.mixer.music.load("Downloads/gameover.mp3") 
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"Error loading music: {e}")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Đóng cửa sổ game và trả về False để thoát vòng lặp chính
                if SOUNDS_LOADED: pygame.mixer.music.stop()
                return False 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Restart game
                    if SOUNDS_LOADED: pygame.mixer.music.stop()
                    return True 
                if event.key == pygame.K_ESCAPE:
                    # Thoát game và trả về False
                    if SOUNDS_LOADED: pygame.mixer.music.stop()
                    return False
        
        screen.fill(BLACK)
        draw_text(screen, "TIME'S UP!", font_large, RED, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        draw_text(screen, f"Score: {score}", font_medium, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        draw_text(screen, "Press [SPACE] to Restart", font_small, YELLOW, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)
        draw_text(screen, "Press [ESC] or [X] to Return to Main App", font_small, WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4 + 40)
        
        pygame.display.flip()
        clock.tick(15)
        
    return False # Trường hợp vòng lặp bị thoát bất ngờ

# --- Game Logic Functions ---
def generate_equation(score):
    """Tạo ra một phương trình mới."""
    # Giữ nguyên logic phức tạp của bạn
    if score < 10:
        a = random.randrange(1, 9)
        b = random.randrange(1, 9)
        op = random.choice(['+'])
    elif score < 25:
        a = random.randrange(5, 15)
        b = random.randrange(1, 10)
        op = random.choice(['+', '-'])
    else:
        a = random.randrange(5, 20)
        b = random.randrange(1, 15)
        op = random.choice(['+', '-', '*'])

    if op == '+':
        result = a + b
    elif op == '-':
        if a < b: a, b = b, a 
        result = a - b
    elif op == '*':
        a = random.randrange(1, 6)
        b = random.randrange(1, 6)
        result = a * b
    
    if result < 0 or result > 9:
        return generate_equation(score)
        
    equation_str = f"{a} {op} {b}"
    return equation_str, result

# --- Main Game Loop ---
def main_game():
    """Chạy vòng lặp chính của trò chơi."""
    global screen, clock, SOUNDS_LOADED
    
    if SOUNDS_LOADED:
        pygame.mixer.music.stop()

    score = 0
    MAX_TIME_MS = 2000
    time_left_ms = MAX_TIME_MS
    start_time = pygame.time.get_ticks()
    
    equation_str, correct_answer = generate_equation(score)
    input_received = False
    
    game_running = True
    while game_running:
        current_time = pygame.time.get_ticks()
        
        elapsed_time = current_time - start_time
        time_left_ms = MAX_TIME_MS - elapsed_time
        
        # 1. Input/Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Dừng vòng lặp game và trả về False, không thoát ứng dụng
                game_running = False 
                break 
            
            if event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key)
                
                if key_name.isdigit():
                    player_answer = int(key_name)
                    
                    if player_answer == correct_answer:
                        score += 1
                        input_received = True
                    else:
                        game_running = False
                        break
        
        # 2. Update Game State
        if not game_running: # Xử lý thoát game ngay lập tức
             break
             
        # Check for Time Over
        if time_left_ms <= 0:
            game_running = False
            break

        # Check for successful input
        if input_received:
            equation_str, correct_answer = generate_equation(score)
            MAX_TIME_MS = max(500, MAX_TIME_MS - 50)
            start_time = pygame.time.get_ticks()
            input_received = False
        
        # 3. Draw/Render
        screen.fill(BLACK)
        
        draw_text(screen, f"Score: {score}", font_medium, WHITE, SCREEN_WIDTH / 2, 50)
        draw_text(screen, equation_str + " = ?", font_large, YELLOW, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50)
        draw_text(screen, "Type the single-digit answer (0-9) fast!", font_small, GREEN, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)

        # Draw Timer Bar
        BAR_WIDTH = SCREEN_WIDTH * 0.8
        BAR_HEIGHT = 20
        time_ratio = max(0, time_left_ms / MAX_TIME_MS)
        current_bar_width = BAR_WIDTH * time_ratio
        
        if time_ratio > 0.6:
            bar_color = BLUE
        elif time_ratio > 0.3:
            bar_color = YELLOW
        else:
            bar_color = RED
            
        bg_rect = pygame.Rect((SCREEN_WIDTH - BAR_WIDTH) / 2, SCREEN_HEIGHT - 100, BAR_WIDTH, BAR_HEIGHT)
        pygame.draw.rect(screen, WHITE, bg_rect, 2)
        fg_rect = pygame.Rect((SCREEN_WIDTH - BAR_WIDTH) / 2, SCREEN_HEIGHT - 100, current_bar_width, BAR_HEIGHT)
        pygame.draw.rect(screen, bar_color, fg_rect)
        
        pygame.display.flip()
        clock.tick(60)

    # Game Over logic
    if not game_running and time_left_ms <= 0:
        return game_over_screen(score)
    # Nếu thoát bằng cách nhấn X (pygame.QUIT) hoặc ESC, game_running là False và ta thoát luôn
    return False

def start_game_1():
    pygame.init()
    pygame.font.init()

    global font_large, font_medium, font_small, clock, screen
    font_large = pygame.font.Font(None, 74)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)
    # Khởi tạo các biến Pygame khi hàm được gọi
    if screen is None:
        screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption(CAPTION)
        clock = pygame.time.Clock()
        font_large = pygame.font.Font(None, 100)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)
        
    running = True
    while running:
        should_restart = main_game()
        if not should_restart:
            running = False

    # Dọn dẹp Pygame trước khi trả lại quyền điều khiển
    pygame.quit()
    # Không gọi sys.exit() ở đây!
    return

# Bỏ vòng lặp while True: main_game() ở cuối file để nó không tự chạy khi import