import pygame
import random
import sys
import math



# --- Cấu hình chung ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
CAPTION = "Tank Dodge - Advanced Survival" # Đã sửa
FPS = 60

# --- Màu sắc (RGB) ---
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (200, 0, 0)
COLOR_PLAYER_TANK = (0, 100, 0)
COLOR_BULLET_NORMAL = (255, 0, 0)       # Normal Bullet (Red)
COLOR_BULLET_FAST = (0, 0, 200)         # Fast Bullet (Dark Blue)
COLOR_BULLET_SPIRAL = (255, 165, 0)     # Spiral Bullet (Orange)
COLOR_WARNING = (255, 200, 0)           # Orange-Yellow for Triangle Warning
COLOR_CACTUS = (0, 150, 0)
COLOR_ROCK = (100, 100, 100)
COLOR_BULLET_SMART = (0, 255, 255)      # Smart Bullet (Cyan)
COLOR_BULLET_SPLIT = (255, 0, 255)      # Split Bullet (Magenta)

# --- Fonts ---
FONT_LARGE = None
FONT_MEDIUM = None
FONT_SMALL = None

# --- Trạng thái trò chơi ---
class GameState:
    MENU = 1
    INSTRUCTIONS = 2
    SURVIVAL_SELECT = 3
    SURVIVAL_PLAYING = 4
    GAME_OVER = 5
    PAUSED = 6 # Trạng thái Tạm dừng mới

# --- Cấu hình Map ---
MAPS = [
    {
        "name": "Desert Oasis",
        "color": (240, 230, 140), # Khaki
        "obstacle_color": COLOR_CACTUS,
        "base_bullet_speed": 4,
        "max_bullet_speed": 8,
        "max_enemies": 3,
        "spawn_rate": 120, # frames
        "bullet_types": ["normal", "fast"],
        "decorations": [
            {"type": "cactus", "pos": (50, 50), "size": (20, 40)},
            {"type": "rock", "pos": (700, 500), "size": (30, 30)},
        ],
        "obstacles": [
            pygame.Rect(100, 100, 50, 200),
            pygame.Rect(650, 300, 50, 200),
        ]
    },
    {
        "name": "Frozen Tundra",
        "color": (173, 216, 230), # LightBlue
        "obstacle_color": COLOR_ROCK,
        "base_bullet_speed": 5,
        "max_bullet_speed": 10,
        "max_enemies": 4,
        "spawn_rate": 100,
        "bullet_types": ["fast", "spiral"],
        "decorations": [
            {"type": "rock", "pos": (150, 400), "size": (40, 40)},
            {"type": "rock", "pos": (500, 100), "size": (30, 30)},
        ],
        "obstacles": [
            pygame.Rect(250, 200, 300, 50),
            pygame.Rect(250, 350, 300, 50),
        ]
    },
    {
        "name": "Jungle Maze",
        "color": (34, 139, 34), # Forest Green
        "obstacle_color": COLOR_CACTUS,
        "base_bullet_speed": 6,
        "max_bullet_speed": 12,
        "max_enemies": 5,
        "spawn_rate": 80,
        "bullet_types": ["spiral", "smart"],
        "decorations": [
            {"type": "cactus", "pos": (600, 150), "size": (20, 50)},
            {"type": "cactus", "pos": (100, 500), "size": (30, 60)},
        ],
        "obstacles": [
            pygame.Rect(50, 50, 50, 500),
            pygame.Rect(700, 50, 50, 500),
            pygame.Rect(50, 50, 700, 50),
            pygame.Rect(50, 500, 700, 50),
        ]
    },
]

# --- Điểm cao (Survival Mode) ---
SURVIVAL_HIGH_SCORES = {} # key: map_index, value: high_score_time

# --- Lớp Sprite và Hàm chung ---

# Định nghĩa màn hìn
screen = None
pygame.display.set_caption(CAPTION)
clock = None

class Tank(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        self.size = 20
        self.color = color
        self.image = pygame.Surface([self.size, self.size])
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.lives = 3 # Mạng sống mới
        self.hit_cooldown = 0
        self.max_hit_cooldown = FPS * 2 # 2 giây

    def update(self, obstacles):
        # Tăng tốc khi nhấn Shift
        keys = pygame.key.get_pressed()
        current_speed = self.speed * 1.5 if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else self.speed
        
        # Xử lý di chuyển
        new_x = self.rect.x
        new_y = self.rect.y
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            new_x -= current_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_x += current_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            new_y -= current_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            new_y += current_speed

        # Cập nhật cooldown
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        # Kiểm tra va chạm với biên màn hình
        if new_x < 0: new_x = 0
        if new_x > SCREEN_WIDTH - self.size: new_x = SCREEN_WIDTH - self.size
        if new_y < 0: new_y = 0
        if new_y > SCREEN_HEIGHT - self.size: new_y = SCREEN_HEIGHT - self.size

        # Kiểm tra va chạm với chướng ngại vật (trục X)
        temp_rect_x = self.rect.copy()
        temp_rect_x.x = new_x
        if not temp_rect_x.collidelist(obstacles) != -1:
            self.rect.x = new_x

        # Kiểm tra va chạm với chướng ngại vật (trục Y)
        temp_rect_y = self.rect.copy()
        temp_rect_y.y = new_y
        if not temp_rect_y.collidelist(obstacles) != -1:
            self.rect.y = new_y
            
        # Hiệu ứng nhấp nháy khi bị trúng đạn
        if self.hit_cooldown > 0 and self.hit_cooldown % 10 < 5:
            self.image.fill(COLOR_RED)
        else:
            self.image.fill(self.color)

    def take_hit(self):
        if self.hit_cooldown == 0:
            self.lives -= 1
            self.hit_cooldown = self.max_hit_cooldown
            return True
        return False

class Enemy(pygame.sprite.Sprite):
    def __init__(self, color, size, x, y, bullet_type):
        super().__init__()
        self.size = size
        self.color = color
        self.image = pygame.Surface([self.size, self.size])
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2
        self.direction = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)]) # Hướng ngẫu nhiên
        self.change_dir_timer = random.randint(30, 120) # Thay đổi hướng sau 0.5-2 giây
        self.bullet_type = bullet_type
        self.shoot_cooldown = random.randint(FPS * 1, FPS * 3) # Bắn sau 1-3 giây

    def update(self, player_pos, obstacles):
        # 1. Di chuyển (thay đổi hướng ngẫu nhiên)
        self.change_dir_timer -= 1
        if self.change_dir_timer <= 0:
            self.direction = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
            self.change_dir_timer = random.randint(60, 180)

        new_x = self.rect.x + self.direction[0] * self.speed
        new_y = self.rect.y + self.direction[1] * self.speed

        # Kiểm tra va chạm với biên màn hình và chướng ngại vật
        if new_x < 0 or new_x > SCREEN_WIDTH - self.size:
            self.direction = (-self.direction[0], self.direction[1])
            new_x = self.rect.x + self.direction[0] * self.speed
        if new_y < 0 or new_y > SCREEN_HEIGHT - self.size:
            self.direction = (self.direction[0], -self.direction[1])
            new_y = self.rect.y + self.direction[1] * self.speed

        # Kiểm tra va chạm với chướng ngại vật (trục X)
        temp_rect_x = self.rect.copy()
        temp_rect_x.x = new_x
        if temp_rect_x.collidelist(obstacles) != -1:
             self.direction = (-self.direction[0], self.direction[1])
             new_x = self.rect.x + self.direction[0] * self.speed
        
        # Kiểm tra va chạm với chướng ngại vật (trục Y)
        temp_rect_y = self.rect.copy()
        temp_rect_y.y = new_y
        if temp_rect_y.collidelist(obstacles) != -1:
             self.direction = (self.direction[0], -self.direction[1])
             new_y = self.rect.y + self.direction[1] * self.speed

        self.rect.x = new_x
        self.rect.y = new_y


    def shoot(self, player_pos, all_sprites, bullets_group, map_config, elapsed_time):
        self.shoot_cooldown -= 1
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = random.randint(FPS * 1, FPS * 3) # Reset cooldown

            # Tính toán tốc độ đạn dựa trên thời gian sống sót
            bullet_speed = map_config["base_bullet_speed"] + min(elapsed_time / 30, map_config["max_bullet_speed"] - map_config["base_bullet_speed"])

            if self.bullet_type == "spiral":
                # Bắn 4 viên theo 4 hướng
                for angle in range(0, 360, 90):
                    new_bullet = Bullet(self.rect.center, angle, bullet_speed, COLOR_BULLET_SPIRAL, "spiral")
                    all_sprites.add(new_bullet)
                    bullets_group.add(new_bullet)

            elif self.bullet_type == "smart":
                # Smart Bullet: Tự động khóa mục tiêu
                new_bullet = Bullet(self.rect.center, 0, bullet_speed * 0.8, COLOR_BULLET_SMART, "smart", target=player_pos)
                all_sprites.add(new_bullet)
                bullets_group.add(new_bullet)

            elif self.bullet_type == "fast":
                # Fast Bullet: Tốc độ cao hơn, bay thẳng về người chơi
                dx = player_pos[0] - self.rect.centerx
                dy = player_pos[1] - self.rect.centery
                angle = math.degrees(math.atan2(-dy, dx))
                
                new_bullet = Bullet(self.rect.center, angle, bullet_speed * 1.5, COLOR_BULLET_FAST, "fast")
                all_sprites.add(new_bullet)
                bullets_group.add(new_bullet)
                
            else: # "normal"
                # Normal Bullet: Bay thẳng về người chơi
                dx = player_pos[0] - self.rect.centerx
                dy = player_pos[1] - self.rect.centery
                angle = math.degrees(math.atan2(-dy, dx))
                
                new_bullet = Bullet(self.rect.center, angle, bullet_speed, COLOR_BULLET_NORMAL, "normal")
                all_sprites.add(new_bullet)
                bullets_group.add(new_bullet)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, angle, speed, color, type, target=None):
        super().__init__()
        self.size = 6
        self.image = pygame.Surface([self.size, self.size])
        self.image.fill(color)
        self.rect = self.image.get_rect(center=start_pos)
        self.speed = speed
        self.angle = angle
        self.type = type
        self.target = target
        
        # Tính toán hướng di chuyển dựa trên góc
        self.vx = self.speed * math.cos(math.radians(angle))
        self.vy = -self.speed * math.sin(math.radians(angle))

        self.smart_turn_rate = 0.05
        self.smart_update_timer = 0
        self.smart_update_interval = 10 # Cập nhật hướng 6 lần mỗi giây

    def update(self, player_pos):
        # 1. Smart Bullet logic (nếu có)
        if self.type == "smart" and self.target:
            self.smart_update_timer += 1
            if self.smart_update_timer >= self.smart_update_interval:
                self.smart_update_timer = 0

                # Tính góc hướng về mục tiêu
                dx = player_pos[0] - self.rect.centerx
                dy = player_pos[1] - self.rect.centery
                target_angle = math.degrees(math.atan2(-dy, dx))

                # Làm mịn góc quay
                diff_angle = (target_angle - self.angle + 180) % 360 - 180
                self.angle = (self.angle + diff_angle * self.smart_turn_rate) % 360

                # Cập nhật vận tốc
                self.vx = self.speed * math.cos(math.radians(self.angle))
                self.vy = -self.speed * math.sin(math.radians(self.angle))


        # 2. Di chuyển
        self.rect.x += self.vx
        self.rect.y += self.vy

        # 3. Loại bỏ đạn ra khỏi màn hình
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

class Decoration(pygame.sprite.Sprite):
    def __init__(self, type, pos, size, map_config):
        super().__init__()
        self.type = type
        self.size = size
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect(topleft=pos)
        
        if type == "cactus":
            self.image.fill(COLOR_CACTUS)
            # Vẽ hình dạng đơn giản
            pygame.draw.polygon(self.image, (0, 100, 0), [(size[0]//2, 0), (0, size[1]), (size[0], size[1])])
        elif type == "rock":
            self.image.fill(map_config["obstacle_color"])
            # Vẽ hình dạng đơn giản
            pygame.draw.circle(self.image, COLOR_ROCK, (size[0]//2, size[1]//2), size[0]//2)
            
        self.image.set_colorkey(COLOR_BLACK) # Đặt màu nền trong suốt

# --- Hàm vẽ UI ---

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def draw_info(surface, time, map_index, map_name, lives, game_mode):
    # Thời gian
    draw_text(surface, f"Time: {time}s", FONT_MEDIUM, COLOR_BLACK, SCREEN_WIDTH - 100, 20)
    # Map
    draw_text(surface, f"Map: {map_name} ({map_index + 1}/{len(MAPS)})", FONT_SMALL, COLOR_BLACK, SCREEN_WIDTH // 2, 20)
    # Mạng sống
    draw_text(surface, f"Lives: {lives}", FONT_MEDIUM, COLOR_BLACK, 80, 20)

def draw_decorations(surface, map_config):
    for deco in map_config["decorations"]:
        if deco["type"] == "cactus":
            # Vẽ xương rồng đơn giản
            pygame.draw.rect(surface, (0, 150, 0), (deco["pos"][0] + deco["size"][0]//4, deco["pos"][1], deco["size"][0]//2, deco["size"][1]))
            pygame.draw.rect(surface, (0, 150, 0), (deco["pos"][0], deco["pos"][1] + deco["size"][1]//4, deco["size"][0], deco["size"][1]//4))
        elif deco["type"] == "rock":
            # Vẽ đá đơn giản
            pygame.draw.circle(surface, COLOR_ROCK, (deco["pos"][0], deco["pos"][1]), deco["size"][0]//2)

def draw_menu_screen(surface):
    surface.fill(COLOR_WHITE)
    draw_text(surface, CAPTION, FONT_LARGE, (0, 0, 150), SCREEN_WIDTH // 2, 100)
    
    # Lựa chọn
    options = [
        ("1. Survival Mode (Sinh tồn)", GameState.SURVIVAL_SELECT),
        ("2. Instructions (Hướng dẫn)", GameState.INSTRUCTIONS),
        ("3. Quit (Thoát)", None)
    ]
    
    for i, (text, _) in enumerate(options):
        color = COLOR_BLACK
        # Hiệu ứng hover giả định (chỉ vẽ, không cần logic)
        if i == 0: color = (0, 150, 0) 
        
        draw_text(surface, text, FONT_MEDIUM, color, SCREEN_WIDTH // 2, 250 + i * 50)

    draw_text(surface, "Press key 1, 2, or 3", FONT_SMALL, (100, 100, 100), SCREEN_WIDTH // 2, 500)

def draw_instructions_screen(surface):
    surface.fill((200, 200, 200))
    draw_text(surface, "Hướng Dẫn", FONT_LARGE, COLOR_BLACK, SCREEN_WIDTH // 2, 80)
    
    instructions = [
        "Mục tiêu: Sinh tồn càng lâu càng tốt.",
        "Di chuyển: Sử dụng các phím mũi tên hoặc WASD.",
        "Chạy nhanh: Giữ SHIFT để tăng tốc độ.",
        "Mạng sống: Bạn có 3 mạng. Va chạm với đạn sẽ mất 1 mạng.",
        "Chướng ngại vật: Các khối màu đặc. Không thể đi qua.",
        "Đạn: Đạn thường (đỏ), Nhanh (xanh đậm), Xoắn ốc (cam), Thông minh (Cyan).",
        "Tốc độ đạn tăng dần theo thời gian.",
        "Nhấn ESC để quay lại Menu.",
    ]
    
    for i, text in enumerate(instructions):
        draw_text(surface, text, FONT_MEDIUM, COLOR_BLACK, SCREEN_WIDTH // 2, 180 + i * 40)

def draw_survival_select_screen(surface, high_scores):
    surface.fill((200, 220, 255))
    draw_text(surface, "Chọn Map Sinh Tồn", FONT_LARGE, (0, 0, 150), SCREEN_WIDTH // 2, 80)

    for i, map_config in enumerate(MAPS):
        map_name = map_config["name"]
        high_score = high_scores.get(i, 0)
        
        text = f"{i+1}. {map_name} (High Score: {high_score}s)"
        color = COLOR_BLACK
        if i == 0: color = (0, 150, 0)
        
        draw_text(surface, text, FONT_MEDIUM, color, SCREEN_WIDTH // 2, 200 + i * 70)
    
    draw_text(surface, "Nhấn phím số (1-3) để chọn Map. ESC để quay lại Menu.", FONT_SMALL, (100, 100, 100), SCREEN_WIDTH // 2, 550)

def draw_game_over_screen(surface, score, mode, map_index, is_new_highscore, high_scores):
    # Tạo lớp phủ mờ
    overlay = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180)) # Đen, độ mờ 70%
    surface.blit(overlay, (0, 0))

    draw_text(surface, "GAME OVER", FONT_LARGE, COLOR_RED, SCREEN_WIDTH // 2, 100)
    
    # Hiển thị điểm số
    score_text = f"Thời gian sống sót: {score} giây"
    draw_text(surface, score_text, FONT_MEDIUM, COLOR_WHITE, SCREEN_WIDTH // 2, 200)

    # Cập nhật High Score
    map_name = MAPS[map_index]["name"]
    high_score_text = f"High Score Map {map_name}: {high_scores.get(map_index, 0)}s"
    draw_text(surface, high_score_text, FONT_SMALL, COLOR_WHITE, SCREEN_WIDTH // 2, 250)

    if is_new_highscore:
        draw_text(surface, "KỶ LỤC MỚI!", FONT_MEDIUM, COLOR_WARNING, SCREEN_WIDTH // 2, 300)
    
    draw_text(surface, "Nhấn ENTER để tiếp tục...", FONT_MEDIUM, (255, 255, 0), SCREEN_WIDTH // 2, 450)

def draw_pause_screen(surface):
    # Tạo lớp phủ mờ
    overlay = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150)) # Đen, độ mờ 60%
    surface.blit(overlay, (0, 0))
    
    draw_text(surface, "PAUSED (Tạm Dừng)", FONT_LARGE, COLOR_WHITE, SCREEN_WIDTH // 2, 200)
    draw_text(surface, "Nhấn P để tiếp tục", FONT_MEDIUM, (170, 170, 170), SCREEN_WIDTH // 2, 300)

# --- Hàm xử lý Input ---

def handle_input(game_state, current_map_index):
    global game_mode
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, game_state, current_map_index
        
        if event.type == pygame.KEYDOWN:
            if game_state == GameState.MENU:
                if event.key == pygame.K_1:
                    game_state = GameState.SURVIVAL_SELECT
                elif event.key == pygame.K_2:
                    game_state = GameState.INSTRUCTIONS
                elif event.key == pygame.K_3 or event.key == pygame.K_q:
                    return False, game_state, current_map_index
            
            elif game_state == GameState.INSTRUCTIONS:
                if event.key == pygame.K_ESCAPE:
                    game_state = GameState.MENU
            
            elif game_state == GameState.SURVIVAL_SELECT:
                if event.key == pygame.K_1 and 0 < len(MAPS):
                    current_map_index = 0
                    game_state = GameState.SURVIVAL_PLAYING
                elif event.key == pygame.K_2 and 1 < len(MAPS):
                    current_map_index = 1
                    game_state = GameState.SURVIVAL_PLAYING
                elif event.key == pygame.K_3 and 2 < len(MAPS):
                    current_map_index = 2
                    game_state = GameState.SURVIVAL_PLAYING
                elif event.key == pygame.K_ESCAPE:
                    game_state = GameState.MENU

            elif game_state == GameState.SURVIVAL_PLAYING:
                if event.key == pygame.K_p: # Tạm dừng game
                    game_state = GameState.PAUSED
            
            elif game_state == GameState.PAUSED:
                if event.key == pygame.K_p: # Tiếp tục game
                    game_state = GameState.SURVIVAL_PLAYING

            elif game_state == GameState.GAME_OVER:
                if event.key == pygame.K_RETURN:
                    # Chuyển về menu sau khi kết thúc
                    game_state = GameState.MENU

    return True, game_state, current_map_index

# --- Hàm khởi tạo Game Mode ---

def init_survival_mode(all_sprites, enemies, bullets, player, map_index):
    # Xóa các sprites cũ
    all_sprites.empty()
    enemies.empty()
    bullets.empty()
    
    # Khởi tạo người chơi và thêm vào nhóm
    player.__init__(COLOR_PLAYER_TANK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    all_sprites.add(player)
    
    # Reset thời gian, số lần đếm
    return 0, 0, 0, 0, False # total_time_survived, enemy_spawn_timer, current_enemies, is_new_highscore

# --- Hàm chính của trò chơi (Đã đổi tên) ---

def start_game_3():
    """
    Hàm khởi chạy chính của Trò Chơi Tank Dodge Survival.
    Được đổi tên từ 'main' thành 'start_game_3' theo yêu cầu.
    """
    global SURVIVAL_HIGH_SCORES
    global screen, pygame, clock
    global FONT_LARGE, FONT_MEDIUM, FONT_SMALL
    # Khởi tạo Pygame
    pygame.init()
    # --- Fonts ---
    FONT_LARGE = pygame.font.Font(None, 74)
    FONT_MEDIUM = pygame.font.Font(None, 36)
    FONT_SMALL = pygame.font.Font(None, 24)
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption(CAPTION)
    clock = pygame.time.Clock()
    # --- Khởi tạo Biến Game ---
    running = True
    game_state = GameState.MENU
    game_mode = "Survival"
    
    current_map_index = 0
    
    # Biến trạng thái Survival Mode
    total_time_survived = 0
    enemy_spawn_timer = 0
    current_enemies = 0
    is_new_highscore = False
    
    # Biến Game Over
    last_game_score = 0
    last_game_map_index = 0
    
    # --- Nhóm Sprites ---
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    player = Tank(COLOR_PLAYER_TANK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    all_sprites.add(player) # Thêm player vào all_sprites ngay cả khi ở Menu

    # --- Game Loop ---
    while running:
        # Xử lý đầu vào
        running, game_state, current_map_index = handle_input(game_state, current_map_index)
        
        # --- Cập nhật logic (Chỉ khi đang chơi) ---
        if game_state == GameState.SURVIVAL_PLAYING:
            current_map = MAPS[current_map_index]
            
            # 1. Cập nhật thời gian
            total_time_survived += 1 / FPS # Tăng thời gian sống sót (tính bằng giây)

            # 2. Sinh Enemy
            enemy_spawn_timer += 1
            if enemy_spawn_timer >= current_map["spawn_rate"] and current_enemies < current_map["max_enemies"]:
                # Chọn vị trí ngẫu nhiên ngoài màn hình hoặc gần biên
                x = random.choice([random.randint(0, SCREEN_WIDTH), random.choice([-50, SCREEN_WIDTH + 50])])
                y = random.choice([random.randint(0, SCREEN_HEIGHT), random.choice([-50, SCREEN_HEIGHT + 50])])
                if -50 < x < SCREEN_WIDTH + 50 and -50 < y < SCREEN_HEIGHT + 50:
                    x = random.choice([0, SCREEN_WIDTH])
                    y = random.choice([0, SCREEN_HEIGHT])
                    
                # Chọn loại đạn ngẫu nhiên từ map
                bullet_type = random.choice(current_map["bullet_types"])
                
                new_enemy = Enemy((0, 0, 0), 30, x, y, bullet_type) # Màu đen
                all_sprites.add(new_enemy)
                enemies.add(new_enemy)
                current_enemies += 1
                enemy_spawn_timer = 0
            
            # 3. Cập nhật Sprites
            player.update(current_map["obstacles"])
            
            for enemy in enemies:
                enemy.update(player.rect.center, current_map["obstacles"])
                enemy.shoot(player.rect.center, all_sprites, bullets, current_map, total_time_survived)
            
            bullets.update(player.rect.center)
            
            # 4. Kiểm tra va chạm (Đạn vs Người chơi)
            if player.hit_cooldown == 0:
                hit_bullets = pygame.sprite.spritecollide(player, bullets, True)
                if hit_bullets:
                    if player.take_hit():
                        # Người chơi bị trúng đạn
                        if player.lives <= 0:
                            # GAME OVER
                            game_state = GameState.GAME_OVER
                            last_game_score = int(total_time_survived)
                            last_game_map_index = current_map_index
                            
                            # Cập nhật High Score
                            old_high_score = SURVIVAL_HIGH_SCORES.get(current_map_index, 0)
                            if last_game_score > old_high_score:
                                SURVIVAL_HIGH_SCORES[current_map_index] = last_game_score
                                is_new_highscore = True
                            else:
                                is_new_highscore = False
                            
                            # Reset trạng thái
                            total_time_survived, enemy_spawn_timer, current_enemies, is_new_highscore = init_survival_mode(all_sprites, enemies, bullets, player, current_map_index)
                            
        
        # --- Vẽ ---
        if game_state in [GameState.SURVIVAL_PLAYING, GameState.GAME_OVER, GameState.PAUSED]:
            current_map = MAPS[current_map_index]
            screen.fill(current_map["color"])
            
            # Draw decorations
            draw_decorations(screen, current_map)
            
            # Draw obstacles
            for obs in current_map["obstacles"]:
                pygame.draw.rect(screen, current_map["obstacle_color"], obs)

            # Draw all sprites (including tank, bullets, and warnings)
            all_sprites.draw(screen)

            # Display game info
            draw_info(screen, int(total_time_survived), current_map_index, current_map["name"], player.lives, game_mode)
            
            # NEW: Draw Pause Overlay on top
            if game_state == GameState.PAUSED:
                draw_pause_screen(screen)

            if game_state == GameState.GAME_OVER:
                draw_game_over_screen(screen, last_game_score, game_mode, last_game_map_index, is_new_highscore, SURVIVAL_HIGH_SCORES)

        elif game_state == GameState.MENU:
            draw_menu_screen(screen)
            
        elif game_state == GameState.INSTRUCTIONS:
            draw_instructions_screen(screen)
            
        elif game_state == GameState.SURVIVAL_SELECT:
            draw_survival_select_screen(screen, SURVIVAL_HIGH_SCORES)
        
        # Cập nhật màn hình
        pygame.display.flip()
        
        # Giới hạn FPS
        clock.tick(FPS)

    pygame.quit()
    # sys.exit()
    return
