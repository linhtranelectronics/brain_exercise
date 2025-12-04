import pygame
import random
import sys
import math

# Khởi tạo Pygame
pygame.init()

# --- Configuration ---
SCREEN_WIDTH = 900                     
SCREEN_HEIGHT = 670                    
CAPTION = "Lane Master: Focus Drive"    
FPS = 60

# --- Colors (RGB) ---
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREY = (150, 150, 150)
COLOR_YELLOW = (255, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 200, 0)
COLOR_PURPLE = (150, 0, 200)

# --- Game Stats ---
LANE_WIDTH = SCREEN_WIDTH // 3          
PLAYER_LANE = 1                         
PLAYER_SPEED = 6                        
GAME_SPEED = 6                          
MAX_HEALTH = 3

# --- Collectibles Config ---
COLLECTIBLE_SHAPES = ["CIRCLE", "SQUARE", "TRIANGLE"]
COLLECTIBLE_COLORS = {
    "RED": COLOR_RED,
    "BLUE": COLOR_BLUE,
    "GREEN": COLOR_GREEN,
    "YELLOW": COLOR_YELLOW
}
SHAPE_SIZE = 30 
SPAWN_INTERVAL = 1000 
TARGET_CHANGE_INTERVAL = 10000 

# Set up screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(CAPTION)
clock = pygame.time.Clock()

font_large = pygame.font.Font(None, 80) 
font_medium = pygame.font.Font(None, 40)
font_small = pygame.font.Font(None, 28)

# --- Game State Management ---
class GameState:
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    FOCUS_TIPS = 4

# --- Player Car Class (ĐÃ SỬA: Bỏ logic di chuyển trong update) ---
class PlayerCar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = 50
        self.color = COLOR_GREEN
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        points = [
            (self.size // 4, 0), (self.size * 3 // 4, 0),
            (self.size, self.size), (0, self.size)
        ]
        pygame.draw.polygon(self.image, self.color, points)
        
        self.current_lane = PLAYER_LANE
        self.rect = self.image.get_rect()
        self.set_lane_position()
        self.rect.bottom = SCREEN_HEIGHT - 70
        self.health = MAX_HEALTH
        self.invulnerable_time = 0

    def set_lane_position(self):
        # Tính toán vị trí X dựa trên làn đường
        center_x = (self.current_lane * LANE_WIDTH) + (LANE_WIDTH // 2)
        self.rect.centerx = center_x
        
    def move_lane(self, direction):
        """Di chuyển xe sang làn trái (-1) hoặc làn phải (+1) nếu hợp lệ."""
        new_lane = self.current_lane + direction
        if 0 <= new_lane <= 2:
            self.current_lane = new_lane
            self.set_lane_position()
        
    def update(self): # KHÔNG CẦN NHẬN 'keys' NỮA
        # Chỉ xử lý trạng thái bất tử và hiển thị
        if self.invulnerable_time > 0:
            self.invulnerable_time -= clock.get_time()
            if self.invulnerable_time % 200 < 100:
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)
            
    def take_hit(self):
        if self.invulnerable_time <= 0:
            self.health -= 1
            self.invulnerable_time = 1500
            return True
        return False

# --- RoadObject Classes (Logic Unchanged) ---
class RoadObject(pygame.sprite.Sprite):
    def __init__(self, lane, size, color):
        super().__init__()
        self.size = size
        self.speed = GAME_SPEED
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        center_x = (lane * LANE_WIDTH) + (LANE_WIDTH // 2)
        self.rect.centerx = center_x
        self.rect.bottom = -50 

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class OtherCar(RoadObject):
    def __init__(self, lane):
        size = 70
        color = random.choice([COLOR_RED, COLOR_BLUE, COLOR_GREY])
        super().__init__(lane, size, color)
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, color, self.image.get_rect(), border_radius=5)
        pygame.draw.rect(self.image, COLOR_WHITE, (size//4, size//4, size//2, size//3))

class Collectible(RoadObject):
    def __init__(self, lane):
        size = SHAPE_SIZE
        self.shape = random.choice(COLLECTIBLE_SHAPES)
        self.color_name, self.color_rgb = random.choice(list(COLLECTIBLE_COLORS.items()))
        super().__init__(lane, size, self.color_rgb)
        self.draw_shape()

    def draw_shape(self):
        self.image.fill((0, 0, 0, 0))
        center = (self.size // 2, self.size // 2)
        
        if self.shape == "CIRCLE":
            pygame.draw.circle(self.image, self.color_rgb, center, self.size // 2)
        elif self.shape == "SQUARE":
            pygame.draw.rect(self.image, self.color_rgb, (0, 0, self.size, self.size))
        elif self.shape == "TRIANGLE":
            points = [
                (self.size // 2, 0), 
                (0, self.size), 
                (self.size, self.size)
            ]
            pygame.draw.polygon(self.image, self.color_rgb, points)
            
    @property
    def identifier(self):
        return f"{self.color_name}_{self.shape}"

# --- Helper Functions (DRAWING) ---

road_line_pos = 0
def draw_road(screen):
    global road_line_pos, GAME_SPEED
    
    screen.fill((50, 50, 50))
    road_line_pos = (road_line_pos + GAME_SPEED) % 50 
    
    num_dashes = SCREEN_HEIGHT // 50 + 2
    for i in range(num_dashes):
        y = (i * 50 + road_line_pos) - 50 
        pygame.draw.rect(screen, COLOR_WHITE, (LANE_WIDTH - 5, y, 10, 30))
        pygame.draw.rect(screen, COLOR_WHITE, (LANE_WIDTH * 2 - 5, y, 10, 30))
        pygame.draw.rect(screen, COLOR_YELLOW, (SCREEN_WIDTH // 2 - 10, y, 5, 30))
        pygame.draw.rect(screen, COLOR_YELLOW, (SCREEN_WIDTH // 2 + 5, y, 5, 30))


def create_random_object(player_rect):
    lane = random.randint(0, 2)
    if random.random() < 0.3:
        return OtherCar(lane)
    else:
        return Collectible(lane)

def draw_hud(screen, health, score, target):
    # Health
    health_text = font_medium.render("HEALTH:", True, COLOR_WHITE)
    screen.blit(health_text, (10, 10))
    for i in range(MAX_HEALTH):
        color = COLOR_RED if i < health else COLOR_GREY
        pygame.draw.circle(screen, color, (150 + i * 30, 25), 10)

    # Score
    score_text = font_large.render(f"{score}", True, COLOR_WHITE)
    screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, 35)))
    
    # Target (Focus Objective)
    target_label = font_medium.render("COLLECT TARGET:", True, COLOR_YELLOW)
    screen.blit(target_label, (10, 60))
    target_text = font_medium.render(target.replace("_", " "), True, COLOR_YELLOW)
    screen.blit(target_text, (10, 100))

def draw_menu_screen(screen):
    screen.fill(COLOR_BLACK)
    
    title_text = font_large.render("LANE MASTER", True, COLOR_YELLOW)
    subtitle_text = font_medium.render("FOCUS DRIVE", True, COLOR_WHITE)
    
    screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200)))
    screen.blit(subtitle_text, subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 140)))

    # Button positions
    button_start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 50, 360, 70)
    button_tips_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 50, 360, 70)
    
    # Draw buttons
    pygame.draw.rect(screen, COLOR_GREEN, button_start_rect, border_radius=10)
    pygame.draw.rect(screen, COLOR_PURPLE, button_tips_rect, border_radius=10)

    # Button text
    text_start = font_medium.render("START GAME", True, COLOR_WHITE)
    text_tips = font_medium.render("FOCUS DRIVING TIPS", True, COLOR_WHITE)
    
    screen.blit(text_start, text_start.get_rect(center=button_start_rect.center))
    screen.blit(text_tips, text_tips.get_rect(center=button_tips_rect.center))
    
    return button_start_rect, button_tips_rect

# Draw Focus Tips Screen with small buttons in the corners
def draw_focus_driving_tips(screen):
    screen.fill((50, 50, 100))
    
    title = font_large.render("FOCUS DRIVING TIPS", True, COLOR_YELLOW)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 80)))
    
    tips = [
        ("Scanning Field", "Always scan 3 zones: Target (top/sides), Obstacles (middle), and Next Lane (bottom)."),
        ("Predictive Thinking", "Anticipate which lane will have an obstacle in the next 2 seconds. Don't react late."),
        ("Selective Processing", "Force your brain to ignore 'wrong' collectibles and focus only on the required item."),
        ("Timely Reaction", "Practice making quick, calculated lane change decisions."),
    ]
    
    start_y = 180
    row_gap = 130
    
    for i, (title_tip, content_tip) in enumerate(tips):
        y_pos = start_y + i * row_gap
        
        # Tip Title
        title_surf = font_medium.render(f"{i+1}. {title_tip}", True, COLOR_WHITE)
        screen.blit(title_surf, (70, y_pos))
        
        # Tip Content
        content_surf = font_small.render(content_tip, True, (200, 200, 255))
        screen.blit(content_surf, (90, y_pos + 40))

    # --- SMALL BUTTONS IN CORNERS ---
    
    # 1. BACK TO MENU (Top Left)
    button_back_rect = pygame.Rect(10, 10, 180, 50) 
    pygame.draw.rect(screen, (100, 100, 100), button_back_rect, border_radius=10)
    text_back = font_small.render("BACK TO MENU", True, COLOR_WHITE) 
    screen.blit(text_back, text_back.get_rect(center=button_back_rect.center))
    
    # 2. EXIT GAME (Top Right)
    button_exit_rect = pygame.Rect(SCREEN_WIDTH - 190, 10, 180, 50) 
    pygame.draw.rect(screen, COLOR_RED, button_exit_rect, border_radius=10)
    text_exit = font_small.render("EXIT GAME", True, COLOR_WHITE) 
    screen.blit(text_exit, text_exit.get_rect(center=button_exit_rect.center))
    
    return button_back_rect, button_exit_rect

# Draw Pause Screen with Main Menu button in the corner
def draw_pause_screen(screen):
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180)) 
    screen.blit(s, (0, 0))

    text_paused = font_large.render("PAUSED", True, COLOR_WHITE)
    screen.blit(text_paused, text_paused.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)))

    # 1. RESUME (Center)
    button_resume_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 60)
    pygame.draw.rect(screen, COLOR_GREEN, button_resume_rect, border_radius=10)
    text_resume = font_medium.render("RESUME (ESC)", True, COLOR_WHITE)
    screen.blit(text_resume, text_resume.get_rect(center=button_resume_rect.center))
    
    # 2. MAIN MENU (Top Left Corner)
    button_menu_rect = pygame.Rect(10, 10, 180, 50)
    pygame.draw.rect(screen, COLOR_RED, button_menu_rect, border_radius=10)
    text_menu = font_small.render("MAIN MENU", True, COLOR_WHITE) 
    screen.blit(text_menu, text_menu.get_rect(center=button_menu_rect.center))
    
    return button_resume_rect, button_menu_rect

# Draw Game Over Screen (Unchanged)
def draw_game_over_screen(screen, score):
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180)) 
    screen.blit(s, (0, 0))

    text_main = font_large.render("GAME OVER", True, COLOR_RED)
    screen.blit(text_main, text_main.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)))

    text_score = font_medium.render(f"FINAL SCORE: {score}", True, COLOR_YELLOW)
    screen.blit(text_score, text_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)))

    button_menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 50, 240, 50)
    pygame.draw.rect(screen, COLOR_BLUE, button_menu_rect, border_radius=10)
    text_menu = font_medium.render("MAIN MENU", True, COLOR_WHITE)
    screen.blit(text_menu, text_menu.get_rect(center=button_menu_rect.center))
    
    return button_menu_rect


# --- Game Loop (ĐÃ SỬA LỖI NHẢY LÀN) ---
def game_loop():
    game_state = GameState.MENU
    running = True
    score = 0
    current_target = "RED_CIRCLE" 
    last_spawn_time = pygame.time.get_ticks()
    last_target_change = pygame.time.get_ticks()
    
    def reset_game():
        nonlocal player, all_sprites, road_objects, score, current_target, last_spawn_time, last_target_change, GAME_SPEED
        
        player = PlayerCar()
        all_sprites = pygame.sprite.Group()
        road_objects = pygame.sprite.Group() 
        all_sprites.add(player)
        score = 0
        current_target = f"{random.choice(list(COLLECTIBLE_COLORS.keys()))}_{random.choice(COLLECTIBLE_SHAPES)}"
        current_time = pygame.time.get_ticks()
        last_spawn_time = current_time
        last_target_change = current_time
        GAME_SPEED = 6

    player, all_sprites, road_objects = PlayerCar(), pygame.sprite.Group(), pygame.sprite.Group()

    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                # --- XỬ LÝ CHUYỂN LÀN Ở ĐÂY (KEYDOWN) ---
                if game_state == GameState.PLAYING:
                    if event.key == pygame.K_a:
                        player.move_lane(-1) # Di chuyển sang trái
                    elif event.key == pygame.K_d:
                        player.move_lane(1) # Di chuyển sang phải
                # ----------------------------------------
                
                if event.key == pygame.K_ESCAPE:
                    if game_state == GameState.PLAYING:
                        game_state = GameState.PAUSED
                    elif game_state == GameState.PAUSED:
                        game_state = GameState.PLAYING
                        
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                
                if game_state == GameState.MENU:
                    start_rect, tips_rect = draw_menu_screen(screen)
                    if start_rect.collidepoint(mouse_pos):
                        reset_game()
                        game_state = GameState.PLAYING
                    elif tips_rect.collidepoint(mouse_pos):
                        game_state = GameState.FOCUS_TIPS
                        
                elif game_state == GameState.FOCUS_TIPS:
                    back_rect, exit_rect = draw_focus_driving_tips(screen) 
                    if back_rect.collidepoint(mouse_pos):
                        game_state = GameState.MENU
                    elif exit_rect.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()
                        
                elif game_state == GameState.PAUSED:
                    resume_rect, menu_rect = draw_pause_screen(screen)
                    if resume_rect.collidepoint(mouse_pos):
                        game_state = GameState.PLAYING
                    elif menu_rect.collidepoint(mouse_pos):
                        game_state = GameState.MENU
                        
                elif game_state == GameState.GAME_OVER:
                    menu_rect = draw_game_over_screen(screen, score)
                    if menu_rect.collidepoint(mouse_pos):
                        game_state = GameState.MENU

        # --- Logic Game ---
        if game_state == GameState.PLAYING:
            GAME_SPEED = 6 + (current_time // 10000) * 0.5 
            
            # Cập nhật trạng thái bất tử (chuyển động đã được xử lý ở event.KEYDOWN)
            player.update() 
            
            if current_time - last_target_change > TARGET_CHANGE_INTERVAL:
                new_target = current_target
                while new_target == current_target:
                    new_target = f"{random.choice(list(COLLECTIBLE_COLORS.keys()))}_{random.choice(COLLECTIBLE_SHAPES)}"
                current_target = new_target
                last_target_change = current_time

            adjusted_spawn_interval = SPAWN_INTERVAL - (GAME_SPEED - 6) * 100
            adjusted_spawn_interval = max(300, adjusted_spawn_interval)
            
            if current_time - last_spawn_time > adjusted_spawn_interval:
                new_object = create_random_object(player.rect)
                all_sprites.add(new_object)
                road_objects.add(new_object)
                last_spawn_time = current_time
                
            for obj in road_objects:
                obj.speed = GAME_SPEED
            road_objects.update()

            hits = pygame.sprite.spritecollide(player, road_objects, True)
            for obj in hits:
                if isinstance(obj, OtherCar):
                    if player.take_hit():
                        score = max(0, score - 50)
                        if player.health <= 0:
                            game_state = GameState.GAME_OVER
                            break
                elif isinstance(obj, Collectible):
                    if obj.identifier == current_target:
                        score += 20
                    else:
                        score -= 5
                        if player.take_hit():
                            if player.health <= 0:
                                game_state = GameState.GAME_OVER
                                break

        # --- Drawing ---
        if game_state in [GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER]:
            draw_road(screen)
            all_sprites.draw(screen)
            draw_hud(screen, player.health, score, current_target)

            if game_state == GameState.PAUSED:
                draw_pause_screen(screen)
            elif game_state == GameState.GAME_OVER:
                draw_game_over_screen(screen, score)

        elif game_state == GameState.MENU:
            draw_menu_screen(screen)
        
        elif game_state == GameState.FOCUS_TIPS:
            draw_focus_driving_tips(screen)


        pygame.display.flip()
        clock.tick(FPS)

while True:
    game_loop()