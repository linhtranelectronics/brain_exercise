import pygame
import random
import sys
import math

# Khởi tạo Pygame
pygame.init()

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
COLOR_BUfLLET_FAST = (0, 0, 200)         # Fast Bullet (Dark Blue)
COLOR_BULLET_SPIRAL = (255, 165, 0)     # Spiral Bullet (Orange)
COLOR_WARNING = (255, 200, 0)           # Orange-Yellow for Triangle Warning
COLOR_CACTUS = (0, 150, 0)
COLOR_ROCK = (100, 100, 100)
COLOR_BULLET_SMART = (0, 255, 255)      # Smart Bullet (Cyan)
COLOR_BULLET_SPLIT = (255, 255, 0)      # Split Bullet (Yellow)

# --- Thông số Game ---
PLAYER_SPEED = 5
TANK_SIZE = 30
BULLET_SIZE = 5
MAX_LIVES = 5                           # Initial Lives
MAP_DURATION = 45 * 1000                # Duration of each map in Campaign mode (45 seconds)
SPIRAL_BOMB_MAX_RADIUS = 200            # MAX: Max spread radius of the spiral bullet

# Định nghĩa các loại đạn cho màn hình Hướng dẫn (Đã dịch)
BULLET_TYPE_INFO = [
    ("Normal (Straight)", "Moves straight, basic speed, aims near the tank's last position.", COLOR_BULLET_NORMAL),
    ("Fast (Homing)", "Moves faster, tracks the tank's exact current position (Basic Homing).", COLOR_BUfLLET_FAST),
    ("Line Wall", "Fires in a horizontal/vertical row, creating a wall.", COLOR_BULLET_NORMAL),
    ("Spiral Bomb", "Explodes, creating wide-spreading spiral bullets. Has a triangle warning.", COLOR_BULLET_SPIRAL),
    ("Smart", "Slow (Speed 4) but constantly changes direction to home onto the tank.", COLOR_BULLET_SMART),
    ("Split", "After 150px of travel, splits into 4 small bullets in an X-shape.", COLOR_BULLET_SPLIT),
]

# Thiết lập màn hình
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(CAPTION)
clock = pygame.time.Clock()
# Giữ nguyên font mặc định của Pygame (None) vì nó hỗ trợ tốt các ký tự ASCII, 
# nếu muốn hỗ trợ tiếng Việt có dấu trong font tiếng Anh, cần load font .ttf cụ thể.
font_large = pygame.font.Font(None, 74) 
font_medium = pygame.font.Font(None, 40)
font_small = pygame.font.Font(None, 24)
font_micro = pygame.font.Font(None, 20)

# --- Quản lý trạng thái Game ---
class GameState:
    MENU = 0
    INSTRUCTIONS = 1
    PLAYING = 2             # Campaign Mode
    GAME_OVER = 3
    SURVIVAL_SELECT = 4     # Survival Map Selection Screen
    SURVIVAL_PLAYING = 5    # Survival Mode
    PAUSED = 6              # NEW: Pause State

# --- Cấu hình Bản đồ (Maps) (Đã dịch) ---
MAPS = {
    1: {"name": "Desert Arena", "color": (245, 222, 179), "obstacles": [], "decor": "cactus", "decor_color": COLOR_CACTUS, "base_rate": 80},
    2: {"name": "Forest Ambush", "color": (34, 139, 34), "obstacles": [
        pygame.Rect(200, 200, 50, 50), pygame.Rect(550, 350, 50, 50),
    ], "obstacle_color": (139, 69, 19), "decor": "tree_stump", "decor_color": (101, 67, 33), "base_rate": 70},
    3: {"name": "City Ruins", "color": (128, 128, 128), "obstacles": [
        pygame.Rect(100, 50, 50, 500), pygame.Rect(650, 50, 50, 500),
    ], "obstacle_color": (80, 80, 80), "decor": "rock", "decor_color": COLOR_ROCK, "base_rate": 60},
    4: {"name": "Snow Field", "color": (224, 255, 255), "obstacles": [
        pygame.Rect(0, 0, 100, 100), pygame.Rect(700, 0, 100, 100), pygame.Rect(0, 500, 100, 100), pygame.Rect(700, 500, 100, 100),
    ], "obstacle_color": (192, 192, 192), "decor": "ice_patch", "decor_color": (173, 216, 230), "base_rate": 55},
    # NEW MAPS
    5: {"name": "Volcanic Core", "color": (150, 40, 40), "obstacles": [
        pygame.Rect(200, 0, 20, 250), pygame.Rect(580, 350, 20, 250),
        pygame.Rect(300, 50, 200, 20), pygame.Rect(300, 530, 200, 20),
    ], "obstacle_color": (255, 100, 0), "decor": "lava_rock", "decor_color": (255, 69, 0), "base_rate": 50},
    6: {"name": "Neon Grid", "color": (250, 250, 250), "obstacles": [], "decor": "star", "decor_color": (0, 255, 255), "base_rate": 45},
}

# Tạo vật trang trí ngẫu nhiên cho mỗi Map
MAP_DECORATIONS = {}
for index, map_info in MAPS.items():
    decor_list = []
    if map_info["decor"]:
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(5, 15)
            decor_list.append((x, y, size))
    MAP_DECORATIONS[index] = decor_list
    MAPS[index]["index"] = index # Gán index vào Map info để dễ truy cập

# --- Lớp Xe Tăng Người Chơi (PlayerTank) ---
class PlayerTank(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = TANK_SIZE
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.lives = MAX_LIVES 
        self.hit_cooldown = 0
        self.MAX_COOLDOWN = 60
        self.draw_tank()

    def draw_tank(self):
        self.image.fill((0, 0, 0, 0))
        body_rect = pygame.Rect(0, 0, self.size, self.size)
        
        # Flashing effect when invulnerable
        if self.hit_cooldown > 0 and self.hit_cooldown % 10 < 5:
            color = (150, 255, 150)
        else:
            color = COLOR_PLAYER_TANK
            
        pygame.draw.rect(self.image, color, body_rect, border_radius=5)
        # Turret - represents movement direction
        turret_rect = pygame.Rect(self.size // 2 - 5, -5, 10, 10)
        pygame.draw.rect(self.image, (50, 50, 50), turret_rect, border_radius=2)
        
    def update(self, keys, current_obstacles):
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
            self.draw_tank()

        dx, dy = 0, 0
        if keys[pygame.K_w]: dy = -PLAYER_SPEED
        if keys[pygame.K_s]: dy = PLAYER_SPEED
        if keys[pygame.K_a]: dx = -PLAYER_SPEED
        if keys[pygame.K_d]: dx = PLAYER_SPEED
        
        # Move and check obstacle collision (X-axis)
        self.rect.x += dx
        self.rect.clamp_ip(screen.get_rect())
        for obs in current_obstacles:
            if self.rect.colliderect(obs):
                self.rect.x -= dx
                break
            
        # Move and check obstacle collision (Y-axis)
        self.rect.y += dy
        self.rect.clamp_ip(screen.get_rect())
        for obs in current_obstacles:
            if self.rect.colliderect(obs):
                self.rect.y -= dy
                break

    def take_hit(self):
        if self.hit_cooldown == 0:
            self.lives -= 1
            self.hit_cooldown = self.MAX_COOLDOWN
            return True
        return False

# --- Lớp Đạn (Bullet) Base Class ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, speed, color):
        super().__init__()
        self.size = BULLET_SIZE
        self.speed = speed
        self.color = color
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.size, self.size), self.size)
        self.rect = self.image.get_rect(center=start_pos)
        self.vx = 0
        self.vy = 0

    def is_off_screen(self):
        return (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or 
                self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT)

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

class StraightBullet(Bullet):
    def __init__(self, start_pos, target_pos, speed=6):
        super().__init__(start_pos, speed, COLOR_BULLET_NORMAL)
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        dist = math.hypot(dx, dy)
        if dist == 0: dist = 1
        
        self.vx = (dx / dist) * self.speed
        self.vy = (dy / dist) * self.speed

class FastBullet(StraightBullet):
    def __init__(self, start_pos, target_pos):
        super().__init__(start_pos, target_pos, speed=9)
        self.color = COLOR_BUfLLET_FAST
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, self.color, (self.size, self.size), self.size)

class SpiralBullet(Bullet):
    def __init__(self, center_pos, radius, angle, angular_speed=0.08, radial_speed=0.5):
        super().__init__(center_pos, 0, COLOR_BULLET_SPIRAL)
        self.center_x, self.center_y = center_pos
        self.radius = radius
        self.angle = angle
        self.angular_speed = angular_speed
        self.radial_speed = radial_speed    
        
        self.rect.centerx = self.center_x + self.radius * math.cos(self.angle)
        self.rect.centery = self.center_y + self.radius * math.sin(self.angle)

    def update(self):
        # Check radius limit (Increased)
        if self.radius < SPIRAL_BOMB_MAX_RADIUS:
            self.radius += self.radial_speed
        
        self.angle += self.angular_speed
        
        self.rect.centerx = self.center_x + self.radius * math.cos(self.angle)
        self.rect.centery = self.center_y + self.radius * math.sin(self.angle)

# --- NEW Bullet Type: SmartBullet ---
class SmartBullet(Bullet):
    """Bullet that constantly changes direction to home onto the player."""
    def __init__(self, start_pos, player_rect):
        super().__init__(start_pos, speed=4, color=COLOR_BULLET_SMART) 
        self.player_rect = player_rect
        self.tracking_strength = 0.05 # Homing sensitivity

        # Initial movement direction
        dx = self.player_rect.centerx - start_pos[0]
        dy = self.player_rect.centery - start_pos[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.vx = (dx / dist) * self.speed
            self.vy = (dy / dist) * self.speed
        
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, self.color, (self.size, self.size), self.size)


    def update(self):
        # 1. Calculate vector towards player
        target_x, target_y = self.player_rect.center
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            # 2. Target velocity vector
            target_vx = (dx / dist) * self.speed
            target_vy = (dy / dist) * self.speed
            
            # 3. Smooth the current velocity (homing)
            self.vx = self.vx * (1 - self.tracking_strength) + target_vx * self.tracking_strength
            self.vy = self.vy * (1 - self.tracking_strength) + target_vy * self.tracking_strength
            
            # 4. Keep speed constant (re-normalize)
            current_dist = math.hypot(self.vx, self.vy)
            if current_dist > 0:
                self.vx = (self.vx / current_dist) * self.speed
                self.vy = (self.vy / current_dist) * self.speed

        # Update position
        self.rect.x += self.vx
        self.rect.y += self.vy

# --- NEW Bullet Type: SplitBullet ---
class SplitBullet(Bullet):
    """Large bullet that moves straight and splits into 4 smaller bullets after a distance."""
    def __init__(self, start_pos, target_pos):
        super().__init__(start_pos, speed=5, color=COLOR_BULLET_SPLIT)
        
        # Initial straight movement towards target
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        dist = math.hypot(dx, dy)
        if dist == 0: dist = 1
        
        self.vx = (dx / dist) * self.speed
        self.vy = (dy / dist) * self.speed
        
        self.initial_pos = start_pos
        self.max_travel_distance = 150 # Distance before splitting
        self.has_split = False
        self.size = 8 # Larger initial size
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.rect(self.image, self.color, self.image.get_rect(), border_radius=4)


    def spawn_splits(self):
        """Creates 4 small bullets in an X-shape."""
        new_bullets = []
        split_speed = 4
        # Splits into 4 directions: Right, Left, Down, Up
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)] 
        
        for dx, dy in directions:
            # Create a simple straight bullet flying outward
            split_bullet = StraightBullet(self.rect.center, (self.rect.centerx + dx * 10, self.rect.centery + dy * 10), speed=split_speed)
            # Use Split Bullet color
            split_bullet.color = COLOR_BULLET_SPLIT
            split_bullet.image.fill((0, 0, 0, 0))
            pygame.draw.circle(split_bullet.image, split_bullet.color, (split_bullet.size, split_bullet.size), split_bullet.size)
            new_bullets.append(split_bullet)
            
        return new_bullets

# --- Spiral Bomb Warning Class ---
class SpiralBombWarning(pygame.sprite.Sprite):
    """Displays a triangle warning before a Spiral Bomb explodes."""
    def __init__(self, center_pos, map_index):
        super().__init__()
        self.center_pos = center_pos
        self.radius = SPIRAL_BOMB_MAX_RADIUS
        
        # Calculate warning duration (shorter for later maps)
        self.warning_duration = max(200, 2000 - (map_index - 1) * 200) 
        
        self.start_time = pygame.time.get_ticks()
        self.is_active = True
        self.has_exploded = False
        
        # Create a large surface to draw the warning
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center_pos)
        self.draw_warning()

    def draw_warning(self):
        self.image.fill((0, 0, 0, 0))
        
        elapsed = pygame.time.get_ticks() - self.start_time
        time_ratio = 1 - (elapsed / self.warning_duration)
        
        if time_ratio > 0:
            # Flashing alpha effect
            alpha = int(255 * (0.5 + 0.5 * abs(math.sin(elapsed / 100))))
            self.image.set_alpha(alpha)
            
            # Pulsing size effect
            size_factor = 0.8 + 0.2 * abs(math.sin(elapsed / 100)) 
            
            points = [
                (self.radius, self.radius * 0.2), 
                (self.radius * 0.2, self.radius * 1.8), 
                (self.radius * 1.8, self.radius * 1.8) 
            ]
            
            # Scale points to fit size_factor and center
            scaled_points = []
            for px, py in points:
                new_x = self.radius + (px - self.radius) * size_factor
                new_y = self.radius + (py - self.radius) * size_factor
                scaled_points.append((new_x, new_y))

            # Draw triangle
            pygame.draw.polygon(self.image, COLOR_WARNING, scaled_points, 5)

            # Draw exclamation mark '!'
            text = font_medium.render("!", True, COLOR_WARNING)
            text_rect = text.get_rect(center=(self.radius, self.radius))
            self.image.blit(text, text_rect)
            
        else:
            # If time is up, make the surface transparent
            self.image.set_alpha(0) 

    def update(self):
        if not self.is_active:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.warning_duration:
            self.is_active = False
            self.has_exploded = True 
        else:
            self.draw_warning()
            
    def spawn_bullets(self):
        """Spawns spiral bullets after the warning ends."""
        if self.has_exploded:
            bullets_to_spawn = []
            num_bullets = 12
            initial_radius = 5 # Bullets start near the center
            
            for i in range(num_bullets):
                angle = i * (2 * math.pi / num_bullets)
                # Increase radial speed to suit the larger radius
                bullets_to_spawn.append(SpiralBullet(self.center_pos, radius=initial_radius, angle=angle, radial_speed=0.8)) 
            return bullets_to_spawn
        return []

# --- Random Bullet Pattern Creator Function ---
def create_random_bullet_pattern(player_rect, current_time, last_spiral_time, current_map_index):
    bullets_to_spawn = []
    
    # Logic to choose a starting position (always off-screen)
    side = random.randint(0, 3)
    if side == 0: start_x, start_y = random.randint(0, SCREEN_WIDTH), -10  # Top
    elif side == 1: start_x, start_y = SCREEN_WIDTH + 10, random.randint(0, SCREEN_HEIGHT) # Right
    elif side == 2: start_x, start_y = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 10 # Bottom
    else: start_x, start_y = -10, random.randint(0, SCREEN_HEIGHT) # Left
    start_pos = (start_x, start_y)

    # Add new bullets to weights
    pattern_choice = random.choices(
        ['straight', 'fast', 'line_wall', 'spiral_bomb', 'smart', 'split'],
        weights=[50, 15, 10, 10, 10, 5], # Adjusted spawn rates
        k=1
    )[0]

    if pattern_choice == 'straight':
        target_pos = (player_rect.centerx + random.randint(-80, 80), player_rect.centery + random.randint(-80, 80))
        bullets_to_spawn.append(StraightBullet(start_pos, target_pos))
        
    elif pattern_choice == 'fast':
        target_pos = player_rect.center 
        bullets_to_spawn.append(FastBullet(start_pos, target_pos))
        
    elif pattern_choice == 'line_wall':
        num_bullets = 5
        offset = 50 
        
        if side == 0 or side == 2:
            center_x = start_x
            target_y = player_rect.centery
            for i in range(num_bullets):
                current_x = center_x + (i - num_bullets // 2) * offset
                current_start_pos = (current_x, start_y)
                current_target_pos = (current_x, target_y if side == 0 else SCREEN_HEIGHT - target_y)
                bullets_to_spawn.append(StraightBullet(current_start_pos, current_target_pos))
                
        else:
            center_y = start_y
            target_x = player_rect.centerx
            for i in range(num_bullets):
                current_y = center_y + (i - num_bullets // 2) * offset
                current_start_pos = (start_x, current_y)
                current_target_pos = (target_x if side == 3 else SCREEN_WIDTH - target_x, current_y)
                bullets_to_spawn.append(StraightBullet(current_start_pos, current_target_pos))

    # Create Spiral Bomb Warning
    elif pattern_choice == 'spiral_bomb' and (current_time - last_spiral_time) > 8000: # Cooldown 8s
        center_pos = player_rect.center
        warning = SpiralBombWarning(center_pos, current_map_index)
        return [warning], current_time # Return warning object and update time
        
    # Create Smart Bullet
    elif pattern_choice == 'smart':
        bullets_to_spawn.append(SmartBullet(start_pos, player_rect))
        
    # Create Split Bullet
    elif pattern_choice == 'split':
        target_pos = player_rect.center
        bullets_to_spawn.append(SplitBullet(start_pos, target_pos))
        
    return bullets_to_spawn, last_spiral_time

# --- Draw Menu Screen Function (Đã dịch) ---
def draw_menu_screen(screen):
    screen.fill((10, 10, 30))
    
    title_text = font_large.render("TANK DODGE ADVANCED", True, (0, 255, 255))
    screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150)))

    # Button positions
    button_start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, 300, 60)
    button_survival_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 30, 300, 60)
    button_instr_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 110, 300, 60)

    # Draw buttons
    pygame.draw.rect(screen, (0, 150, 0), button_start_rect, border_radius=10)
    pygame.draw.rect(screen, (255, 100, 0), button_survival_rect, border_radius=10) # Orange for Survival
    pygame.draw.rect(screen, (200, 200, 0), button_instr_rect, border_radius=10)

    # Button text (Đã dịch)
    text_start = font_medium.render("CAMPAIGN MODE", True, COLOR_WHITE)
    text_survival = font_medium.render("SURVIVAL MODE", True, COLOR_WHITE)
    text_instr = font_medium.render("INSTRUCTIONS", True, COLOR_BLACK)
    
    screen.blit(text_start, text_start.get_rect(center=button_start_rect.center))
    screen.blit(text_survival, text_survival.get_rect(center=button_survival_rect.center))
    screen.blit(text_instr, text_instr.get_rect(center=button_instr_rect.center))
    
    return button_start_rect, button_survival_rect, button_instr_rect

# --- Draw Survival Map Selection Screen Function (Đã dịch) ---
def draw_survival_select_screen(screen, high_scores):
    screen.fill((20, 20, 40))
    
    title = font_large.render("SELECT SURVIVAL MAP", True, (255, 100, 0))
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 50)))
    
    map_rects = []
    
    # Draw 6 Map buttons
    num_maps = len(MAPS)
    cols = 2
    rows = math.ceil(num_maps / cols)
    
    start_x = SCREEN_WIDTH // 2 - 300
    start_y = 150
    gap = 20
    button_width = 280
    button_height = 80
    
    for i, (index, map_info) in enumerate(MAPS.items()):
        row = i // cols
        col = i % cols
        
        x = start_x + col * (button_width + gap * 2)
        y = start_y + row * (button_height + gap)
        
        rect = pygame.Rect(x, y, button_width, button_height)
        map_rects.append((index, rect))
        
        # Draw button
        pygame.draw.rect(screen, map_info["color"], rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=10) # Border
        
        # Map Name Text (Đã dịch tên map)
        text_name = font_medium.render(f"MAP {index}: {map_info['name']}", True, COLOR_BLACK)
        screen.blit(text_name, text_name.get_rect(midtop=(rect.centerx, rect.y + 10)))
        
        # High Score Text (Đã dịch)
        score = high_scores.get(index, 0.0)
        text_score = font_small.render(f"Record: {score:.2f} seconds", True, COLOR_RED)
        screen.blit(text_score, text_score.get_rect(midbottom=(rect.centerx, rect.bottom - 10)))

    # Back Button (Đã dịch)
    button_back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
    pygame.draw.rect(screen, (100, 100, 100), button_back_rect, border_radius=10)
    text_back = font_medium.render("BACK", True, COLOR_WHITE)
    screen.blit(text_back, text_back.get_rect(center=button_back_rect.center))
    
    return map_rects, button_back_rect

# --- Draw Instructions Screen Function (Đã dịch) ---
def draw_instructions_screen(screen):
    screen.fill((20, 20, 40))
    
    title = font_large.render("INSTRUCTIONS & BULLET TYPES", True, (255, 200, 0))
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 50)))
    
    # Control Text (Đã dịch)
    control_text = font_medium.render("Controls: W A S D to move. Objective: Dodge bullets!", True, (150, 150, 255))
    screen.blit(control_text, control_text.get_rect(center=(SCREEN_WIDTH // 2, 120)))
    
    # Table start position
    table_x = 50
    table_y = 180
    col_widths = [180, 400, 100] # Name | Description | Color
    row_height = 40
    
    # Header (Đã dịch)
    header_data = ["Bullet Name", "Description / Characteristic", "Color"]
    for i, text in enumerate(header_data):
        rect = pygame.Rect(table_x + sum(col_widths[:i]), table_y, col_widths[i], row_height)
        pygame.draw.rect(screen, (50, 50, 100), rect)
        text_surf = font_small.render(text, True, COLOR_WHITE)
        screen.blit(text_surf, text_surf.get_rect(center=rect.center))

    # Data Rows (Sử dụng BULLET_TYPE_INFO đã dịch)
    for r, (name, desc, color) in enumerate(BULLET_TYPE_INFO):
        y_pos = table_y + (r + 1) * row_height
        
        # Draw row
        pygame.draw.rect(screen, (30, 30, 50), (table_x, y_pos, sum(col_widths), row_height), 1)
        
        # Col 1: Name
        rect1 = pygame.Rect(table_x, y_pos, col_widths[0], row_height)
        text1 = font_small.render(name, True, COLOR_WHITE)
        screen.blit(text1, text1.get_rect(center=rect1.center))
        
        # Col 2: Description (Use midleft for left alignment)
        rect2 = pygame.Rect(table_x + col_widths[0], y_pos, col_widths[1], row_height)
        # Use smaller font for long description
        text2 = font_micro.render(desc, True, (200, 200, 200)) 
        screen.blit(text2, text2.get_rect(midleft=(rect2.x + 10, rect2.centery)))

        # Col 3: Color (Draw circle)
        rect3 = pygame.Rect(table_x + col_widths[0] + col_widths[1], y_pos, col_widths[2], row_height)
        pygame.draw.circle(screen, color, rect3.center, 10)

    # Back Button (Đã dịch)
    button_back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
    pygame.draw.rect(screen, (100, 100, 100), button_back_rect, border_radius=10)
    text_back = font_medium.render("BACK", True, COLOR_WHITE)
    screen.blit(text_back, text_back.get_rect(center=button_back_rect.center))
    
    return button_back_rect

# --- Draw Pause Screen Function (NEW) ---
def draw_pause_screen(screen):
    # Dark semi-transparent overlay
    s = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
    s.fill((0, 0, 0, 180)) 
    screen.blit(s, (0, 0))

    text_paused = font_large.render("PAUSED", True, (255, 255, 255))
    screen.blit(text_paused, text_paused.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)))

    # Button positions
    button_resume_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 60)
    button_menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 80, 300, 60)

    # Draw buttons
    pygame.draw.rect(screen, (0, 150, 0), button_resume_rect, border_radius=10) # Green for Resume
    pygame.draw.rect(screen, (200, 50, 50), button_menu_rect, border_radius=10) # Red for Menu

    # Button text 
    text_resume = font_medium.render("RESUME (ESC)", True, COLOR_WHITE)
    text_menu = font_medium.render("MAIN MENU", True, COLOR_WHITE)
    
    screen.blit(text_resume, text_resume.get_rect(center=button_resume_rect.center))
    screen.blit(text_menu, text_menu.get_rect(center=button_menu_rect.center))
    
    return button_resume_rect, button_menu_rect

# --- Function to Display Score, Map, and Lives (Đã dịch) ---
def draw_info(screen, score, current_map_index, map_name, lives, game_mode):
    score_label = "Time Survived" if game_mode == 'survival' else "Map Time" # Đã dịch
    score_text = font_small.render(f"{score_label}: {score:.1f} seconds", True, COLOR_BLACK) # Đã dịch
    
    map_label = "Fixed Map" if game_mode == 'survival' else "Map" # Đã dịch
    map_text = font_small.render(f"{map_label} {current_map_index}: {map_name}", True, COLOR_BLACK)
    
    # Display Lives (Đã dịch)
    lives_text = font_small.render("Lives:", True, COLOR_BLACK)
    screen.blit(lives_text, (10, 35))
    
    # Draw hearts (or squares) representing lives
    start_x = 70
    for i in range(MAX_LIVES):
        color = COLOR_RED if i < lives else (150, 150, 150)
        pygame.draw.circle(screen, color, (start_x + i * 20, 42), 7)
        
    screen.blit(score_text, (10, 10))
    screen.blit(map_text, (SCREEN_WIDTH - map_text.get_width() - 10, 10))
    
    # NEW: Draw a small Pause Button hint (always visible during gameplay)
    pause_text = font_small.render("Press ESC to PAUSE", True, (100, 100, 100))
    screen.blit(pause_text, (SCREEN_WIDTH - pause_text.get_width() - 10, 40))


# --- Function to Draw Map Decorations (Logic not changed, only the names) ---
def draw_decorations(screen, map_info):
    decor_type = map_info.get("decor")
    decor_color = map_info.get("decor_color")
    decor_list = MAP_DECORATIONS.get(map_info["index"], [])
    
    for x, y, size in decor_list:
        if decor_type == "cactus":
            pygame.draw.circle(screen, decor_color, (x, y), size // 3)
            pygame.draw.circle(screen, decor_color, (x - size // 2, y + size // 2), size // 3)
            pygame.draw.circle(screen, decor_color, (x + size // 2, y + size // 2), size // 3)
        elif decor_type == "tree_stump":
            pygame.draw.circle(screen, decor_color, (x, y), size // 2)
        elif decor_type == "rock":
            pygame.draw.ellipse(screen, decor_color, pygame.Rect(x - size, y - size // 2, size * 2, size))
        elif decor_type == "ice_patch":
            s = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
            s.fill(decor_color + (100,))
            screen.blit(s, (x - size * 1.5, y - size * 1.5))
        elif decor_type == "star":
            # Map Neon Grid (Star)
            pygame.draw.circle(screen, decor_color, (x, y), 1)
        elif decor_type == "lava_rock":
            # Map Volcanic Core
            pygame.draw.circle(screen, decor_color, (x, y), size // 2)
            pygame.draw.circle(screen, (255, 255, 0), (x, y), size // 4) # Lava effect

# --- Game Over Screen Function (Đã dịch) ---
def draw_game_over_screen(screen, score, game_mode, map_index, is_new_highscore, high_scores):
    s = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    screen.blit(s, (0, 0))

    text_main = font_large.render("GAME OVER!", True, COLOR_RED)
    rect_main = text_main.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(text_main, rect_main)

    # Score (Đã dịch)
    text_score = font_medium.render(f"You survived: {score:.2f} seconds.", True, (255, 255, 100))
    rect_score = text_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
    screen.blit(text_score, rect_score)
    
    # Display High Score for Survival Mode (Đã dịch)
    if game_mode == 'survival':
        map_name = MAPS[map_index]['name']
        
        if is_new_highscore:
            hs_text = font_medium.render("NEW HIGH SCORE!", True, (0, 255, 0))
            hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            screen.blit(hs_text, hs_rect)
            
            new_best_text = font_small.render(f"Record on {map_name}: {score:.2f} seconds", True, (0, 255, 0))
            new_best_rect = new_best_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 65))
            screen.blit(new_best_text, new_best_rect)
        else:
            current_hs = high_scores.get(map_index, 0.0)
            hs_text = font_medium.render("Record not broken!", True, (255, 100, 100))
            hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            screen.blit(hs_text, hs_rect)
            
            old_best_text = font_small.render(f"Record on {map_name}: {current_hs:.2f} seconds", True, (255, 100, 100))
            old_best_rect = old_best_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 65))
            screen.blit(old_best_text, old_best_rect)
    else:
        # Campaign mode (Đã dịch)
        instruction_text = font_small.render("Press SPACE or CLICK to RETURN TO MENU", True, (150, 150, 150))
        rect_instruction = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        screen.blit(instruction_text, rect_instruction)

    # Back to Menu Button (Đã dịch)
    button_menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 120, 240, 50)
    pygame.draw.rect(screen, (50, 50, 150), button_menu_rect, border_radius=10)
    text_menu = font_medium.render("MENU", True, COLOR_WHITE)
    screen.blit(text_menu, text_menu.get_rect(center=button_menu_rect.center))
    
    return button_menu_rect

# --- Main Game Loop ---
def game_loop():
    # --- Global Game Variables ---
    game_state = GameState.MENU
    running = True
    
    # --- Game Mode Variables ---
    game_mode = 'campaign' # 'campaign', 'survival'
    current_map_index = 1
    
    # Survival Mode Variables
    SURVIVAL_HIGH_SCORES = {i: 0.0 for i in MAPS.keys()}
    
    # --- Game Reset Variables ---
    def reset_game(mode, initial_map_index):
        nonlocal game_mode, current_map_index, total_time_survived, map_start_time, bullet_spawn_rate, last_bullet_spawn, last_spiral_time
        
        player = PlayerTank()
        all_sprites = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        warnings = pygame.sprite.Group()
        all_sprites.add(player)
        
        game_mode = mode
        current_map_index = initial_map_index
        total_time_survived = 0.0
        
        current_time = pygame.time.get_ticks()
        map_start_time = current_time
        
        bullet_spawn_rate = MAPS[current_map_index]["base_rate"]
        last_bullet_spawn = current_time
        last_spiral_time = current_time
        
        return player, all_sprites, bullets, warnings
    
    # Initial setup
    player, all_sprites, bullets, warnings = reset_game('campaign', 1)
    
    # Initialize variables to avoid UnboundLocalError
    total_time_survived = 0.0
    map_start_time = pygame.time.get_ticks()
    bullet_spawn_rate = MAPS[1]["base_rate"]
    last_bullet_spawn = pygame.time.get_ticks()
    last_spiral_time = pygame.time.get_ticks()
    last_game_score = 0.0
    last_game_map_index = 1
    is_new_highscore = False


    while running:
        current_time = pygame.time.get_ticks()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left click
                mouse_pos = event.pos
                
                if game_state == GameState.MENU:
                    # Need to redraw to get the rects
                    start_rect, survival_rect, instr_rect = draw_menu_screen(screen) 
                    if start_rect.collidepoint(mouse_pos):
                        player, all_sprites, bullets, warnings = reset_game('campaign', 1)
                        game_state = GameState.PLAYING
                        
                    elif survival_rect.collidepoint(mouse_pos): # Go to Survival Map Selection
                        game_state = GameState.SURVIVAL_SELECT

                    elif instr_rect.collidepoint(mouse_pos):
                        game_state = GameState.INSTRUCTIONS
                        
                elif game_state == GameState.INSTRUCTIONS:
                    # Need to redraw to get the rects
                    button_back_rect = draw_instructions_screen(screen) 
                    if button_back_rect.collidepoint(mouse_pos):
                        game_state = GameState.MENU
                        
                elif game_state == GameState.SURVIVAL_SELECT:
                    # Need to redraw to get the rects
                    map_rects, back_rect = draw_survival_select_screen(screen, SURVIVAL_HIGH_SCORES)
                    if back_rect.collidepoint(mouse_pos):
                        game_state = GameState.MENU
                    
                    for index, rect in map_rects:
                        if rect.collidepoint(mouse_pos):
                            # Start Survival Mode on the selected map
                            player, all_sprites, bullets, warnings = reset_game('survival', index)
                            game_state = GameState.SURVIVAL_PLAYING
                            break

                elif game_state == GameState.GAME_OVER:
                    # Need to redraw to get the rects
                    menu_rect = draw_game_over_screen(screen, last_game_score, game_mode, last_game_map_index, is_new_highscore, SURVIVAL_HIGH_SCORES)
                    if menu_rect.collidepoint(mouse_pos):
                        game_state = GameState.MENU
                        
                elif game_state == GameState.PAUSED: # NEW: Handle PAUSED click
                    resume_rect, menu_rect = draw_pause_screen(screen) # Redraw to get rects
                    
                    if resume_rect.collidepoint(mouse_pos):
                        if game_mode == 'campaign':
                            game_state = GameState.PLAYING
                        elif game_mode == 'survival':
                            game_state = GameState.SURVIVAL_PLAYING
                            
                    elif menu_rect.collidepoint(mouse_pos):
                        game_state = GameState.MENU

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_state == GameState.GAME_OVER:
                        # Return to Menu
                        game_state = GameState.MENU
                
                # NEW: ESC key for Pause/Resume
                if event.key == pygame.K_ESCAPE:
                    if game_state == GameState.PLAYING:
                        game_state = GameState.PAUSED
                    elif game_state == GameState.SURVIVAL_PLAYING:
                        game_state = GameState.PAUSED
                    elif game_state == GameState.PAUSED:
                        # Resume (Needs to know which mode to resume to)
                        if game_mode == 'campaign':
                            game_state = GameState.PLAYING
                        elif game_mode == 'survival':
                            game_state = GameState.SURVIVAL_PLAYING


        # --- Game Logic Update (Only when playing) ---
        if game_state == GameState.PLAYING or game_state == GameState.SURVIVAL_PLAYING:
            
            # 1. Update Time and Difficulty
            delta_time = clock.get_time() / 1000.0
            total_time_survived += delta_time
            
            current_map_info = MAPS[current_map_index]
            base_rate = current_map_info["base_rate"]
            
            map_time_elapsed = current_time - map_start_time
            difficulty_factor = (map_time_elapsed / 10000) * 5 # Increase difficulty every 10 seconds
            bullet_spawn_rate = max(10, int(base_rate - difficulty_factor))
            
            # 2. Handle tank movement
            keys = pygame.key.get_pressed()
            player.update(keys, current_map_info["obstacles"])
            
            # 3. Create random bullets or warnings
            if current_time - last_bullet_spawn > bullet_spawn_rate * (1000 / FPS):
                new_sprites, new_spiral_time = create_random_bullet_pattern(
                    player.rect, current_time, last_spiral_time, current_map_index
                )
                
                if new_spiral_time != last_spiral_time:
                    last_spiral_time = new_spiral_time
                
                for sprite in new_sprites:
                    all_sprites.add(sprite)
                    if isinstance(sprite, Bullet) or isinstance(sprite, SplitBullet) or isinstance(sprite, SmartBullet):
                        bullets.add(sprite)
                    elif isinstance(sprite, SpiralBombWarning):
                        warnings.add(sprite)
                
                last_bullet_spawn = current_time

            # 4a. Update warnings and spawn real bullets
            warnings.update()
            for warning in list(warnings):
                if warning.has_exploded:
                    # Spawn real Spiral Bullets
                    new_spiral_bullets = warning.spawn_bullets()
                    for bullet in new_spiral_bullets:
                        all_sprites.add(bullet)
                        bullets.add(bullet)
                    warning.kill() # Remove warning from all groups immediately

            # 4b. Update bullets, handle split bullets, and remove off-screen bullets
            newly_spawned_bullets = []
            for bullet in list(bullets): # Iterate over a copy of the list
                
                # Handle Split Bullet
                if isinstance(bullet, SplitBullet) and not bullet.has_split:
                    bullet.update() # Keep moving
                    current_distance = math.hypot(bullet.rect.centerx - bullet.initial_pos[0], bullet.rect.centery - bullet.initial_pos[1])
                    if current_distance >= bullet.max_travel_distance:
                        bullet.has_split = True
                        newly_spawned_bullets.extend(bullet.spawn_splits())
                        bullet.kill() # Remove parent bullet
                        continue 
                        
                else:
                    bullet.update() # Update movement (SmartBullet, Straight, Fast, Spiral)
                
                # Cleanup
                # Remove off-screen bullets or spiral bullets that reached max radius
                if bullet.is_off_screen() or (isinstance(bullet, SpiralBullet) and bullet.radius >= SPIRAL_BOMB_MAX_RADIUS):
                    bullet.kill()

            # Add newly spawned bullets from SplitBullet to the group
            for bullet in newly_spawned_bullets:
                all_sprites.add(bullet)
                bullets.add(bullet)


            # 5. Check for Collision (Tank vs. Bullet)
            if player.hit_cooldown == 0:
                hit_bullet = pygame.sprite.spritecollideany(player, bullets)
                if hit_bullet:
                    hit_bullet.kill() 
                    if player.take_hit():
                        if player.lives <= 0:
                            last_game_score = total_time_survived
                            last_game_map_index = current_map_index
                            
                            # Update High Score for Survival Mode
                            is_new_highscore = False
                            if game_mode == 'survival':
                                if total_time_survived > SURVIVAL_HIGH_SCORES.get(current_map_index, 0.0):
                                    SURVIVAL_HIGH_SCORES[current_map_index] = total_time_survived
                                    is_new_highscore = True

                            game_state = GameState.GAME_OVER 
            
            # 6. Change Map (Campaign Mode Only)
            if game_mode == 'campaign' and map_time_elapsed >= MAP_DURATION:
                current_map_index += 1
                if current_map_index > len(MAPS):
                    current_map_index = 1 # Loop map
                
                # Reset time and clear bullets/warnings
                map_start_time = current_time
                bullet_spawn_rate = MAPS[current_map_index]["base_rate"]
                bullets.empty() 
                warnings.empty()


        # --- Drawing based on GameState ---
        # Draw game screen elements if playing, paused, or game over
        if game_state in [GameState.PLAYING, GameState.SURVIVAL_PLAYING, GameState.GAME_OVER, GameState.PAUSED]:
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
            draw_info(screen, total_time_survived, current_map_index, current_map["name"], player.lives, game_mode)
            
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


        # Update screen and limit FPS
        pygame.display.flip()
        clock.tick(FPS)

while True:
    game_loop()