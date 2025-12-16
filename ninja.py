import pygame
import random
import sys
import math
import array

# ------------------ INIT ------------------
pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Ninja - Ultimate Edition")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("arial", 32, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 20, bold=True)
TINY_FONT = pygame.font.SysFont("arial", 16)

# ------------------ SOUND EFFECTS ------------------
def create_sound(frequency, duration, sound_type="splash"):
    """Create various sound effects (no numpy required)"""
    sample_rate = 22050
    samples = int(sample_rate * duration)

    # interleaved stereo 16-bit signed: L, R, L, R, ...
    buf = array.array("h")

    for i in range(samples):
        amplitude = 32767 * (1 - i / samples) * 0.3

        if sound_type == "splash":
            value = amplitude * (
                math.sin(2 * math.pi * frequency * i / sample_rate)
                + 0.5 * math.sin(2 * math.pi * frequency * 2 * i / sample_rate)
            )
        elif sound_type == "bomb":
            value = amplitude * random.uniform(-1, 1) * 0.5
        elif sound_type == "powerup":
            freq = frequency + (i / samples) * 200
            value = amplitude * math.sin(2 * math.pi * freq * i / sample_rate)
        else:
            value = amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)

        s = int(max(-32768, min(32767, value)))
        buf.append(s)  # L
        buf.append(s)  # R

    # Create Sound from raw PCM buffer
    return pygame.mixer.Sound(buffer=buf.tobytes())

try:
    splash_sound = create_sound(400, 0.15, "splash")
    bomb_sound = create_sound(100, 0.3, "bomb")
    powerup_sound = create_sound(600, 0.2, "powerup")
    critical_sound = create_sound(800, 0.1, "powerup")
except Exception:
    splash_sound = bomb_sound = powerup_sound = critical_sound = None

# ------------------ COLORS ------------------
BLACK = (10, 10, 20)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
DARK_RED = (139, 0, 0)
GREEN = (100, 200, 100)
YELLOW = (255, 220, 50)
ORANGE = (255, 140, 50)
PURPLE = (147, 51, 234)
CYAN = (0, 255, 255)
GOLD = (255, 215, 0)

# ------------------ GAME DIFFICULTY ------------------
class DifficultyManager:
    def __init__(self):
        self.level = 1
        self.score_threshold = 100
        self.base_spawn_rate = 50
        self.base_fruit_speed = (3, 6)

    def update(self, score):
        new_level = score // self.score_threshold + 1
        if new_level > self.level:
            self.level = new_level
            return True
        return False

    def get_spawn_rate(self):
        return max(20, self.base_spawn_rate - self.level * 3)

    def get_fruit_speed(self):
        min_speed = self.base_fruit_speed[0] + self.level * 0.5
        max_speed = self.base_fruit_speed[1] + self.level * 0.5
        return (min_speed, max_speed)

# ------------------ FRUIT TYPES ------------------
FRUIT_TYPES = {
    'watermelon': {'color': (34, 139, 34), 'inner': (255, 69, 96), 'stripe': (25, 100, 25), 'size': 60, 'points': 15},
    'mango': {'color': (255, 140, 0), 'inner': (255, 200, 50), 'size': 50, 'points': 10},
    'banana': {'color': (255, 225, 53), 'inner': (255, 245, 157), 'outline': (200, 180, 40), 'size': 55, 'points': 12},
    'apple': {'color': (220, 20, 60), 'inner': (255, 100, 120), 'size': 45, 'points': 8},
    'orange': {'color': (255, 165, 0), 'inner': (255, 200, 100), 'size': 48, 'points': 9},
    'strawberry': {'color': (255, 50, 80), 'inner': (255, 150, 150), 'size': 40, 'points': 7}
}

# ------------------ SPECIAL ITEMS ------------------
class Bomb:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = -40
        self.size = 40
        self.speed = random.uniform(3, 5)
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
        self.sliced = False

    def update(self):
        self.y += self.speed
        self.rotation += self.rotation_speed

    def draw(self):
        pygame.draw.circle(screen, (30, 30, 30), (int(self.x), int(self.y)), self.size//2)
        pygame.draw.circle(screen, (60, 60, 60), (int(self.x - 5), int(self.y - 5)), self.size//6)

        fuse_length = 15
        fuse_angle = self.rotation
        fuse_x = self.x + (self.size//2) * math.cos(math.radians(fuse_angle))
        fuse_y = self.y - (self.size//2) * math.sin(math.radians(fuse_angle))
        pygame.draw.line(screen, (139, 69, 19), (self.x, self.y - self.size//2),
                         (fuse_x, fuse_y - fuse_length), 3)

        spark_colors = [(255, 200, 0), (255, 100, 0), (255, 0, 0)]
        for i, color in enumerate(spark_colors):
            pygame.draw.circle(screen, color,
                               (int(fuse_x + random.randint(-2, 2)),
                                int(fuse_y - fuse_length + random.randint(-2, 2))), 4 - i)

        pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), self.size//2, 2)

    def get_rect(self):
        return pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)

class PowerUp:
    def __init__(self):
        self.types = ['freeze', 'double_points', 'frenzy']
        self.type = random.choice(self.types)
        self.x = random.randint(50, WIDTH - 50)
        self.y = -40
        self.size = 35
        self.speed = random.uniform(2, 4)
        self.rotation = 0
        self.sliced = False
        self.glow = 0
        self.glow_direction = 1

    def update(self):
        self.y += self.speed
        self.rotation += 3
        self.glow += self.glow_direction * 2
        if self.glow >= 20 or self.glow <= 0:
            self.glow_direction *= -1

    def draw(self):
        for i in range(3):
            size = self.size + self.glow + i * 5
            color = self.get_color()
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size//2, 2)

        points = []
        for i in range(10):
            angle = i * 36 + self.rotation
            radius = self.size//2 if i % 2 == 0 else self.size//4
            px = self.x + radius * math.cos(math.radians(angle))
            py = self.y + radius * math.sin(math.radians(angle))
            points.append((px, py))
        pygame.draw.polygon(screen, self.get_color(), points)

        icon_font = TINY_FONT
        if self.type == 'freeze':
            icon = "F"
        elif self.type == 'double_points':
            icon = "x2"
        else:
            icon = "Z"
        text = icon_font.render(icon, True, WHITE)
        rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, rect)

    def get_color(self):
        if self.type == 'freeze':
            return CYAN
        elif self.type == 'double_points':
            return GOLD
        else:
            return PURPLE

    def get_rect(self):
        return pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)

# ------------------ BACKGROUND ------------------
def draw_background(time):
    for i in range(HEIGHT):
        ratio = i / HEIGHT
        phase = math.sin(time * 0.001) * 20
        r = int(40 + ratio * 80 + phase)
        g = int(20 + ratio * 50 + phase)
        b = int(60 + ratio * 80 + phase)
        pygame.draw.line(screen, (r, g, b), (0, i), (WIDTH, i))

    points = [(0, HEIGHT//2 + 80), (150, HEIGHT//2 - 20), (300, HEIGHT//2 + 60),
              (450, HEIGHT//2 - 40), (600, HEIGHT//2 + 40), (WIDTH, HEIGHT//2 + 20),
              (WIDTH, HEIGHT), (0, HEIGHT)]
    pygame.draw.polygon(screen, (30, 20, 50), points)

    pygame.draw.rect(screen, (20, 15, 35), (650, HEIGHT//2 + 50, 30, 80))
    pygame.draw.polygon(screen, (20, 15, 35), [(630, HEIGHT//2 + 50), (665, HEIGHT//2 + 30), (700, HEIGHT//2 + 50)])

    pygame.draw.line(screen, (60, 40, 30), (0, 100), (200, 180), 8)
    for pos in [(50, 90), (120, 110), (170, 100)]:
        offset = math.sin(time * 0.003 + pos[0]) * 3
        pygame.draw.circle(screen, (255, 182, 193), (pos[0], int(pos[1] + offset)), 8)

# ------------------ PARTICLE ------------------
class Particle:
    def __init__(self, x, y, color, particle_type="splash"):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6) if particle_type == "splash" else random.uniform(4, 10)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - random.uniform(1, 3)
        self.color = color
        self.size = random.randint(3, 8) if particle_type == "splash" else random.randint(5, 12)
        self.lifetime = 60 if particle_type == "splash" else 90
        self.max_lifetime = self.lifetime
        self.type = particle_type

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3 if self.type == "splash" else 0.5
        self.lifetime -= 1
        self.size = max(1, self.size - 0.1)

    def draw(self):
        if self.lifetime > 0:
            alpha_ratio = self.lifetime / self.max_lifetime
            color = tuple(int(c * alpha_ratio) for c in self.color)
            if self.type == "explosion":
                pygame.draw.circle(screen, (255, 150, 0), (int(self.x), int(self.y)), int(self.size) + 2)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.size))

# ------------------ FRUIT ------------------
class Fruit:
    def __init__(self, speed_range):
        self.type = random.choice(list(FRUIT_TYPES.keys()))
        self.info = FRUIT_TYPES[self.type]
        self.size = self.info['size']
        self.points = self.info['points']
        self.x = random.randint(self.size, WIDTH - self.size)
        self.y = -self.size
        self.speed = random.uniform(speed_range[0], speed_range[1])
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-3, 3)
        self.sliced = False
        self.is_critical = random.random() < 0.1

    def update(self):
        self.y += self.speed
        self.rotation += self.rotation_speed

    def draw(self):
        offset = abs(math.sin(math.radians(self.rotation))) * 3

        if self.is_critical:
            for i in range(3):
                glow_size = self.size + 10 + i * 5
                pygame.draw.circle(screen, GOLD, (int(self.x), int(self.y + offset)), glow_size//2, 1)

        if self.type == 'watermelon':
            pygame.draw.circle(screen, self.info['color'], (int(self.x), int(self.y + offset)), self.size//2)
            for i in range(-3, 4):
                stripe_x = int(self.x + i * 8)
                pygame.draw.line(screen, self.info['stripe'],
                                 (stripe_x, int(self.y - self.size//2 + offset)),
                                 (stripe_x, int(self.y + self.size//2 + offset)), 3)

        elif self.type == 'mango':
            pygame.draw.ellipse(screen, self.info['color'],
                                (int(self.x - self.size//2), int(self.y - self.size//2.5 + offset),
                                 self.size, int(self.size * 1.2)))

        elif self.type == 'banana':
            points = []
            for i in range(7):
                curve_x = int(self.x + (i - 3) * 10)
                curve_y = int(self.y + offset)
                points.append((curve_x, curve_y - 15))
            for i in range(6, -1, -1):
                curve_x = int(self.x + (i - 3) * 10)
                curve_y = int(self.y + offset)
                points.append((curve_x, curve_y + 15))
            pygame.draw.polygon(screen, self.info['color'], points)

        elif self.type == 'apple':
            pygame.draw.circle(screen, self.info['color'], (int(self.x), int(self.y + offset)), self.size//2)

        elif self.type == 'orange':
            pygame.draw.circle(screen, self.info['color'], (int(self.x), int(self.y + offset)), self.size//2)

        elif self.type == 'strawberry':
            points = [(self.x, self.y - self.size//2 + offset),
                      (self.x - self.size//2, self.y + self.size//3 + offset),
                      (self.x, self.y + self.size//2 + offset),
                      (self.x + self.size//2, self.y + self.size//3 + offset)]
            pygame.draw.polygon(screen, self.info['color'], points)

        points_value = self.points * 2 if self.is_critical else self.points
        label_color = GOLD if self.is_critical else WHITE
        points_text = SMALL_FONT.render(f"+{points_value}", True, label_color)
        text_rect = points_text.get_rect(center=(int(self.x), int(self.y + self.size//2 + 15)))
        screen.blit(points_text, text_rect)

    def get_rect(self):
        return pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)

# ------------------ NINJA ------------------
class Ninja:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.width = 60
        self.height = 80
        self.speed = 8
        self.sword_angle = -45
        self.target_angle = -45
        self.is_slashing = False
        self.slash_cooldown = 0
        self.dash_cooldown = 0
        self.dash_direction = 0

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.x > self.width//2:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width//2:
            self.x += self.speed

        if keys[pygame.K_SPACE] and self.dash_cooldown == 0:
            if keys[pygame.K_LEFT]:
                self.dash_direction = -1
            elif keys[pygame.K_RIGHT]:
                self.dash_direction = 1
            if self.dash_direction != 0:
                self.dash_cooldown = 30

        if self.dash_cooldown > 20:
            dash_speed = 15
            self.x += self.dash_direction * dash_speed
            self.x = max(self.width//2, min(WIDTH - self.width//2, self.x))

        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
            if self.dash_cooldown == 0:
                self.dash_direction = 0

        if self.is_slashing:
            self.target_angle = -90
            self.slash_cooldown = 15
            self.is_slashing = False
        elif self.slash_cooldown > 0:
            self.slash_cooldown -= 1
            if self.slash_cooldown == 0:
                self.target_angle = -45

        angle_diff = self.target_angle - self.sword_angle
        self.sword_angle += angle_diff * 0.3

    def trigger_slash(self):
        self.is_slashing = True

    def draw(self):
        x, y = int(self.x), int(self.y)

        pygame.draw.ellipse(screen, (50, 50, 50), (x - 30, y + 60, 60, 15))
        pygame.draw.circle(screen, (30, 30, 40), (x, y - 25), 18)
        pygame.draw.rect(screen, (180, 0, 0), (x - 20, y - 30, 40, 10))
        pygame.draw.circle(screen, BLACK, (x - 6, y - 26), 2)
        pygame.draw.circle(screen, BLACK, (x + 6, y - 26), 2)

        pygame.draw.rect(screen, (40, 40, 50), (x - 18, y - 10, 36, 45))

        arm_end_x = x + 35
        arm_end_y = y - 15
        pygame.draw.line(screen, (40, 40, 50), (x + 18, y - 5), (arm_end_x, arm_end_y), 8)

        sword_base_x, sword_base_y = arm_end_x + 5, arm_end_y - 5
        sword_length = 50
        angle_rad = math.radians(self.sword_angle)
        sword_tip_x = sword_base_x + sword_length * math.cos(angle_rad)
        sword_tip_y = sword_base_y + sword_length * math.sin(angle_rad)

        pygame.draw.line(screen, (220, 220, 230), (sword_base_x, sword_base_y),
                         (sword_tip_x, sword_tip_y), 5)

        pygame.draw.line(screen, (40, 40, 50), (x - 8, y + 35), (x - 15, y + 60), 10)
        pygame.draw.line(screen, (40, 40, 50), (x + 8, y + 35), (x + 15, y + 60), 10)

    def get_slash_area(self):
        angle_rad = math.radians(self.sword_angle)
        sword_reach = 80
        center_x = self.x + sword_reach * math.cos(angle_rad) / 2
        center_y = self.y - 40 + sword_reach * math.sin(angle_rad) / 2
        return pygame.Rect(center_x - 60, center_y - 60, 120, 120)

# ------------------ DRAW HEARTS ------------------
def draw_heart(x, y, filled=True):
    color = RED if filled else (80, 80, 80)
    pygame.draw.circle(screen, color, (x - 6, y), 8)
    pygame.draw.circle(screen, color, (x + 6, y), 8)
    pygame.draw.polygon(screen, color, [(x - 12, y + 2), (x + 12, y + 2), (x, y + 16)])

# ------------------ FLOATING TEXT ------------------
class FloatingText:
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = 60
        self.vy = -2

    def update(self):
        self.y += self.vy
        self.lifetime -= 1

    def draw(self):
        text_surf = FONT.render(self.text, True, self.color)
        screen.blit(text_surf, (int(self.x), int(self.y)))

# ------------------ GAME STATE ------------------
fruits = []
bombs = []
powerups = []
particles = []
floating_texts = []
ninja = Ninja()
difficulty = DifficultyManager()

spawn_timer = 0
bomb_spawn_timer = 0
powerup_spawn_timer = 0
score = 0
high_score = 0
combo = 0
max_combo = 0
lives = 3
running = True
game_time = 0
paused = False

active_powerups = {
    'freeze': 0,
    'double_points': 0,
    'frenzy': 0
}

stats = {
    'fruits_sliced': 0,
    'bombs_hit': 0,
    'critical_hits': 0,
    'powerups_collected': 0
}

# ------------------ MAIN LOOP ------------------
while running:
    dt = clock.tick(60)
    game_time += dt

    draw_background(game_time)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused

            elif event.key == pygame.K_r and lives <= 0:
                fruits = []
                bombs = []
                powerups = []
                particles = []
                floating_texts = []
                ninja = Ninja()
                difficulty = DifficultyManager()
                spawn_timer = 0
                bomb_spawn_timer = 0
                powerup_spawn_timer = 0
                score = 0
                combo = 0
                max_combo = 0
                lives = 3
                game_time = 0
                active_powerups = {'freeze': 0, 'double_points': 0, 'frenzy': 0}
                stats = {'fruits_sliced': 0, 'bombs_hit': 0, 'critical_hits': 0, 'powerups_collected': 0}

    if paused:
        pause_text = FONT.render("PAUSED - Press P", True, WHITE)
        screen.blit(pause_text, (WIDTH//2 - 150, HEIGHT//2))
        pygame.display.flip()
        continue

    if lives <= 0:
        high_score = max(high_score, score)
        over = FONT.render("GAME OVER", True, RED)
        hs = SMALL_FONT.render(f"High Score: {high_score}", True, WHITE)
        rs = SMALL_FONT.render("Press R to Restart", True, WHITE)
        screen.blit(over, over.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
        screen.blit(hs, hs.get_rect(center=(WIDTH//2, HEIGHT//2 + 10)))
        screen.blit(rs, rs.get_rect(center=(WIDTH//2, HEIGHT//2 + 45)))
        pygame.display.flip()
        continue

    keys = pygame.key.get_pressed()
    ninja.update(keys)

    for key in active_powerups:
        if active_powerups[key] > 0:
            active_powerups[key] -= 1

    if difficulty.update(score):
        floating_texts.append(FloatingText(WIDTH//2 - 100, HEIGHT//2, f"LEVEL {difficulty.level}!", GOLD))

    spawn_rate = difficulty.get_spawn_rate()
    if active_powerups['frenzy'] > 0:
        spawn_rate = max(10, spawn_rate // 2)

    if active_powerups['freeze'] == 0:
        spawn_timer += 1
        bomb_spawn_timer += 1
        powerup_spawn_timer += 1

    if spawn_timer > spawn_rate:
        fruits.append(Fruit(difficulty.get_fruit_speed()))
        spawn_timer = 0

    if bomb_spawn_timer > 180:
        bombs.append(Bomb())
        bomb_spawn_timer = random.randint(-30, 0)

    if powerup_spawn_timer > 400:
        powerups.append(PowerUp())
        powerup_spawn_timer = 0

    slash_area = ninja.get_slash_area()

    for fruit in fruits[:]:
        if active_powerups['freeze'] == 0:
            fruit.update()
        if not fruit.sliced and fruit.get_rect().colliderect(slash_area):
            fruit.sliced = True
            fruits.remove(fruit)
            points = fruit.points
            if active_powerups['double_points'] > 0:
                points *= 2
            if fruit.is_critical:
                points *= 2
                stats['critical_hits'] += 1
                if critical_sound:
                    critical_sound.play()
                floating_texts.append(FloatingText(fruit.x - 50, fruit.y, "CRITICAL!", GOLD))
            score += points
            combo += 1
            max_combo = max(max_combo, combo)
            stats['fruits_sliced'] += 1
            ninja.trigger_slash()
            if splash_sound:
                splash_sound.play()
            for _ in range(25):
                particles.append(Particle(fruit.x, fruit.y, fruit.info['color'], "splash"))
                particles.append(Particle(fruit.x, fruit.y, fruit.info['inner'], "splash"))
        elif fruit.y > HEIGHT + 50:
            if fruit in fruits:
                fruits.remove(fruit)
                lives -= 1
                combo = 0

    for bomb in bombs[:]:
        if active_powerups['freeze'] == 0:
            bomb.update()
        if not bomb.sliced and bomb.get_rect().colliderect(slash_area):
            bomb.sliced = True
            bombs.remove(bomb)
            lives -= 1
            combo = 0
            stats['bombs_hit'] += 1
            if bomb_sound:
                bomb_sound.play()
            for _ in range(50):
                particles.append(Particle(bomb.x, bomb.y, (255, 100, 0), "explosion"))
                particles.append(Particle(bomb.x, bomb.y, (255, 200, 0), "explosion"))
            floating_texts.append(FloatingText(bomb.x - 40, bomb.y, "-1 LIFE", RED))
        elif bomb.y > HEIGHT + 50:
            if bomb in bombs:
                bombs.remove(bomb)

    for powerup in powerups[:]:
        if active_powerups['freeze'] == 0:
            powerup.update()
        if not powerup.sliced and powerup.get_rect().colliderect(slash_area):
            powerup.sliced = True
            powerups.remove(powerup)
            active_powerups[powerup.type] = 300
            stats['powerups_collected'] += 1
            if powerup_sound:
                powerup_sound.play()
            powerup_messages = {
                'freeze': "TIME FREEZE!",
                'double_points': "DOUBLE POINTS!",
                'frenzy': "FRUIT FRENZY!"
            }
            floating_texts.append(FloatingText(powerup.x - 80, powerup.y, powerup_messages[powerup.type], powerup.get_color()))
            for _ in range(30):
                particles.append(Particle(powerup.x, powerup.y, powerup.get_color(), "splash"))
        elif powerup.y > HEIGHT + 50:
            if powerup in powerups:
                powerups.remove(powerup)

    for particle in particles[:]:
        particle.update()
        if particle.lifetime <= 0:
            particles.remove(particle)

    for text in floating_texts[:]:
        text.update()
        if text.lifetime <= 0:
            floating_texts.remove(text)

    for particle in particles:
        particle.draw()

    for fruit in fruits:
        fruit.draw()

    for bomb in bombs:
        bomb.draw()

    for powerup in powerups:
        powerup.draw()

    ninja.draw()

    for text in floating_texts:
        text.draw()

    score_text = FONT.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (20, 20))

    if combo > 1:
        combo_color = GOLD if combo >= 10 else YELLOW if combo >= 5 else WHITE
        combo_text = FONT.render(f"x{combo} COMBO!", True, combo_color)
        screen.blit(combo_text, (WIDTH//2 - 90, 20))

    level_text = SMALL_FONT.render(f"Level: {difficulty.level}", True, WHITE)
    screen.blit(level_text, (20, 60))

    # Draw hearts (lives)
    for i in range(3):
        filled = i < lives
        draw_heart(WIDTH - 120 + i * 30, 35, filled)

    # Powerup HUD
    y0 = 90
    if active_powerups['freeze'] > 0:
        t = SMALL_FONT.render("Freeze", True, CYAN)
        screen.blit(t, (20, y0)); y0 += 22
    if active_powerups['double_points'] > 0:
        t = SMALL_FONT.render("x2 Points", True, GOLD)
        screen.blit(t, (20, y0)); y0 += 22
    if active_powerups['frenzy'] > 0:
        t = SMALL_FONT.render("Frenzy", True, PURPLE)
        screen.blit(t, (20, y0)); y0 += 22

    pygame.display.flip()

pygame.quit()
sys.exit()