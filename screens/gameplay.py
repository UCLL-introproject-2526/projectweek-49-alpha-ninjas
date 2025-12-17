import pygame
import random
import math
from settings import WIDTH, HEIGHT


# ------------------ PATHS ------------------
SND_BG_GAMEPLAY = "assets/sounds/backgroundmusic_gameplay.mp3"
SND_GAME_START = "assets/sounds/game_start_sound.mp3"
SND_GAME_OVER = "assets/sounds/game-over-arcade-6435.mp3"
SND_SLICE = "assets/sounds/splicing_side.mp3"


# ------------------ COLORS ------------------
BLACK = (10, 10, 20)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
YELLOW = (255, 220, 50)
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

        # Bomb difficulty tuning
        self.base_bomb_interval = 180
        self.min_bomb_interval = 60
        self.base_bomb_speed = (3.0, 5.0)

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

    # ✅ Bombs fall faster with level
    def get_bomb_speed(self):
        min_speed = self.base_bomb_speed[0] + self.level * 0.35
        max_speed = self.base_bomb_speed[1] + self.level * 0.35
        return (min_speed, max_speed)

    # ✅ Bombs spawn more often with level
    def get_bomb_interval(self):
        interval = self.base_bomb_interval - self.level * 10
        return max(self.min_bomb_interval, interval)

    # ✅ Spawn multiple bombs sometimes (burst)
    def get_bomb_burst_count(self):
        roll = random.random()
        if self.level >= 7:
            if roll < 0.20:
                return 3
            if roll < 0.55:
                return 2
            return 1
        if self.level >= 4:
            return 2 if roll < 0.35 else 1
        return 1


FRUIT_TYPES = {
    "watermelon": {"color": (34, 139, 34), "inner": (255, 69, 96), "stripe": (25, 100, 25), "size": 60, "points": 15},
    "mango": {"color": (255, 140, 0), "inner": (255, 200, 50), "size": 50, "points": 10},
    "banana": {"color": (255, 225, 53), "inner": (255, 245, 157), "outline": (200, 180, 40), "size": 55, "points": 12},
    "apple": {"color": (220, 20, 60), "inner": (255, 100, 120), "size": 45, "points": 8},
    "orange": {"color": (255, 165, 0), "inner": (255, 200, 100), "size": 48, "points": 9},
    "strawberry": {"color": (255, 50, 80), "inner": (255, 150, 150), "size": 40, "points": 7},
}


class Bomb:
    def __init__(self, speed_range=(3.0, 5.0)):
        self.x = random.randint(50, WIDTH - 50)
        self.y = -40
        self.size = 40
        self.speed = random.uniform(speed_range[0], speed_range[1])
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
        self.sliced = False

    def update(self):
        self.y += self.speed
        self.rotation += self.rotation_speed

    def draw(self, surface):
        pygame.draw.circle(surface, (30, 30, 30), (int(self.x), int(self.y)), self.size // 2)
        pygame.draw.circle(surface, (60, 60, 60), (int(self.x - 5), int(self.y - 5)), self.size // 6)

        fuse_length = 15
        fuse_angle = self.rotation
        fuse_x = self.x + (self.size // 2) * math.cos(math.radians(fuse_angle))
        fuse_y = self.y - (self.size // 2) * math.sin(math.radians(fuse_angle))
        pygame.draw.line(surface, (139, 69, 19), (self.x, self.y - self.size // 2), (fuse_x, fuse_y - fuse_length), 3)

        spark_colors = [(255, 200, 0), (255, 100, 0), (255, 0, 0)]
        for i, color in enumerate(spark_colors):
            pygame.draw.circle(
                surface,
                color,
                (int(fuse_x + random.randint(-2, 2)), int(fuse_y - fuse_length + random.randint(-2, 2))),
                4 - i,
            )

        pygame.draw.circle(surface, (255, 0, 0), (int(self.x), int(self.y)), self.size // 2, 2)

    def get_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)


class PowerUp:
    def __init__(self, tiny_font):
        self.types = ["freeze", "double_points", "frenzy"]
        self.type = random.choice(self.types)
        self.x = random.randint(50, WIDTH - 50)
        self.y = -40
        self.size = 35
        self.speed = random.uniform(2, 4)
        self.rotation = 0
        self.sliced = False
        self.glow = 0
        self.glow_direction = 1
        self.tiny_font = tiny_font

    def update(self):
        self.y += self.speed
        self.rotation += 3
        self.glow += self.glow_direction * 2
        if self.glow >= 20 or self.glow <= 0:
            self.glow_direction *= -1

    def get_color(self):
        if self.type == "freeze":
            return CYAN
        if self.type == "double_points":
            return GOLD
        return PURPLE

    def draw(self, surface):
        for i in range(3):
            size = self.size + self.glow + i * 5
            pygame.draw.circle(surface, self.get_color(), (int(self.x), int(self.y)), size // 2, 2)

        points = []
        for i in range(10):
            angle = i * 36 + self.rotation
            radius = self.size // 2 if i % 2 == 0 else self.size // 4
            px = self.x + radius * math.cos(math.radians(angle))
            py = self.y + radius * math.sin(math.radians(angle))
            points.append((px, py))
        pygame.draw.polygon(surface, self.get_color(), points)

        icon = "F" if self.type == "freeze" else ("x2" if self.type == "double_points" else "Z")
        text = self.tiny_font.render(icon, True, WHITE)
        surface.blit(text, text.get_rect(center=(int(self.x), int(self.y))))

    def get_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)


def draw_background(surface, t_ms):
    for i in range(HEIGHT):
        ratio = i / HEIGHT
        phase = math.sin(t_ms * 0.001) * 20
        r = int(40 + ratio * 80 + phase)
        g = int(20 + ratio * 50 + phase)
        b = int(60 + ratio * 80 + phase)
        pygame.draw.line(surface, (r, g, b), (0, i), (WIDTH, i))

    points = [
        (0, HEIGHT // 2 + 80),
        (150, HEIGHT // 2 - 20),
        (300, HEIGHT // 2 + 60),
        (450, HEIGHT // 2 - 40),
        (600, HEIGHT // 2 + 40),
        (WIDTH, HEIGHT // 2 + 20),
        (WIDTH, HEIGHT),
        (0, HEIGHT),
    ]
    pygame.draw.polygon(surface, (30, 20, 50), points)

    pygame.draw.rect(surface, (20, 15, 35), (650, HEIGHT // 2 + 50, 30, 80))
    pygame.draw.polygon(surface, (20, 15, 35), [(630, HEIGHT // 2 + 50), (665, HEIGHT // 2 + 30), (700, HEIGHT // 2 + 50)])

    pygame.draw.line(surface, (60, 40, 30), (0, 100), (200, 180), 8)
    for pos in [(50, 90), (120, 110), (170, 100)]:
        offset = math.sin(t_ms * 0.003 + pos[0]) * 3
        pygame.draw.circle(surface, (255, 182, 193), (pos[0], int(pos[1] + offset)), 8)


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

    def draw(self, surface):
        if self.lifetime <= 0:
            return
        alpha_ratio = self.lifetime / self.max_lifetime
        color = tuple(int(c * alpha_ratio) for c in self.color)
        if self.type == "explosion":
            pygame.draw.circle(surface, (255, 150, 0), (int(self.x), int(self.y)), int(self.size) + 2)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size))


class Fruit:
    def __init__(self, speed_range, small_font):
        self.type = random.choice(list(FRUIT_TYPES.keys()))
        self.info = FRUIT_TYPES[self.type]
        self.size = self.info["size"]
        self.points = self.info["points"]
        self.x = random.randint(self.size, WIDTH - self.size)
        self.y = -self.size
        self.speed = random.uniform(speed_range[0], speed_range[1])
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-3, 3)
        self.sliced = False
        self.is_critical = random.random() < 0.1
        self.small_font = small_font

    def update(self):
        self.y += self.speed
        self.rotation += self.rotation_speed

    def draw(self, surface):
        offset = abs(math.sin(math.radians(self.rotation))) * 3

        if self.is_critical:
            for i in range(3):
                glow_size = self.size + 10 + i * 5
                pygame.draw.circle(surface, GOLD, (int(self.x), int(self.y + offset)), glow_size // 2, 1)

        if self.type == "watermelon":
            pygame.draw.circle(surface, self.info["color"], (int(self.x), int(self.y + offset)), self.size // 2)
            for i in range(-3, 4):
                stripe_x = int(self.x + i * 8)
                pygame.draw.line(surface, self.info["stripe"], (stripe_x, int(self.y - self.size // 2 + offset)), (stripe_x, int(self.y + self.size // 2 + offset)), 3)
        elif self.type == "mango":
            pygame.draw.ellipse(surface, self.info["color"], (int(self.x - self.size // 2), int(self.y - self.size // 2.5 + offset), self.size, int(self.size * 1.2)))
        elif self.type == "banana":
            points = []
            for i in range(7):
                curve_x = int(self.x + (i - 3) * 10)
                curve_y = int(self.y + offset)
                points.append((curve_x, curve_y - 15))
            for i in range(6, -1, -1):
                curve_x = int(self.x + (i - 3) * 10)
                curve_y = int(self.y + offset)
                points.append((curve_x, curve_y + 15))
            pygame.draw.polygon(surface, self.info["color"], points)
        elif self.type == "apple":
            pygame.draw.circle(surface, self.info["color"], (int(self.x), int(self.y + offset)), self.size // 2)
        elif self.type == "orange":
            pygame.draw.circle(surface, self.info["color"], (int(self.x), int(self.y + offset)), self.size // 2)
        elif self.type == "strawberry":
            points = [
                (self.x, self.y - self.size // 2 + offset),
                (self.x - self.size // 2, self.y + self.size // 3 + offset),
                (self.x, self.y + self.size // 2 + offset),
                (self.x + self.size // 2, self.y + self.size // 3 + offset),
            ]
            pygame.draw.polygon(surface, self.info["color"], points)

        points_value = self.points * 2 if self.is_critical else self.points
        label_color = GOLD if self.is_critical else WHITE
        points_text = self.small_font.render(f"+{points_value}", True, label_color)
        surface.blit(points_text, points_text.get_rect(center=(int(self.x), int(self.y + self.size // 2 + 15))))

    def get_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)


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
        if keys[pygame.K_LEFT] and self.x > self.width // 2:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width // 2:
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
            self.x = max(self.width // 2, min(WIDTH - self.width // 2, self.x))

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

        self.sword_angle += (self.target_angle - self.sword_angle) * 0.3

    def trigger_slash(self):
        self.is_slashing = True

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        pygame.draw.ellipse(surface, (50, 50, 50), (x - 30, y + 60, 60, 15))
        pygame.draw.circle(surface, (30, 30, 40), (x, y - 25), 18)
        pygame.draw.rect(surface, (180, 0, 0), (x - 20, y - 30, 40, 10))
        pygame.draw.circle(surface, BLACK, (x - 6, y - 26), 2)
        pygame.draw.circle(surface, BLACK, (x + 6, y - 26), 2)

        pygame.draw.rect(surface, (40, 40, 50), (x - 18, y - 10, 36, 45))

        arm_end_x, arm_end_y = x + 35, y - 15
        pygame.draw.line(surface, (40, 40, 50), (x + 18, y - 5), (arm_end_x, arm_end_y), 8)

        sword_base_x, sword_base_y = arm_end_x + 5, arm_end_y - 5
        sword_length = 50
        angle_rad = math.radians(self.sword_angle)
        sword_tip_x = sword_base_x + sword_length * math.cos(angle_rad)
        sword_tip_y = sword_base_y + sword_length * math.sin(angle_rad)

        pygame.draw.line(surface, (220, 220, 230), (sword_base_x, sword_base_y), (sword_tip_x, sword_tip_y), 5)

        pygame.draw.line(surface, (40, 40, 50), (x - 8, y + 35), (x - 15, y + 60), 10)
        pygame.draw.line(surface, (40, 40, 50), (x + 8, y + 35), (x + 15, y + 60), 10)

    def get_slash_area(self):
        angle_rad = math.radians(self.sword_angle)
        sword_reach = 80
        center_x = self.x + sword_reach * math.cos(angle_rad) / 2
        center_y = self.y - 40 + sword_reach * math.sin(angle_rad) / 2
        return pygame.Rect(center_x - 60, center_y - 60, 120, 120)


class FloatingText:
    def __init__(self, x, y, text, color, font):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = 60
        self.vy = -2
        self.font = font

    def update(self):
        self.y += self.vy
        self.lifetime -= 1

    def draw(self, surface):
        surface.blit(self.font.render(self.text, True, self.color), (int(self.x), int(self.y)))


# ------------------ SOUND MANAGER (simple) ------------------
class SoundBank:
    def __init__(self):
        self.ok = False
        self.slice = None
        self.start = None
        self.over = None
        self.bg_loaded = False

        # ✅ keep channel reference
        self._start_channel = None

        try:
            if pygame.mixer.get_init():
                self.ok = True
                self.slice = pygame.mixer.Sound(SND_SLICE)
                self.slice.set_volume(0.35)   # 🔽 much lower
                self.start = pygame.mixer.Sound(SND_GAME_START)
                self.start.set_volume(0.6)
                self.over = pygame.mixer.Sound(SND_GAME_OVER)
                self.over.set_volume(0.7)
        except Exception:
            self.ok = False

    def play_slice(self):
        if self.ok and self.slice:
            self.slice.play()

    def play_start(self):
        if self.ok and self.start:
            # ✅ play once (no loops), keep channel so we can stop it
            self._start_channel = self.start.play(loops=0)

    def stop_start(self):
        # ✅ stops the start sound immediately (if still playing)
        if self._start_channel:
            self._start_channel.stop()
            self._start_channel = None

    def play_game_over(self):
        if self.ok and self.over:
            self.over.play()

    def start_bg(self, volume=0.35):
        if not self.ok:
            return
        try:
            pygame.mixer.music.load(SND_BG_GAMEPLAY)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
            self.bg_loaded = True
        except Exception:
            self.bg_loaded = False

    def stop_bg(self):
        if self.ok and self.bg_loaded:
            pygame.mixer.music.stop()
            self.bg_loaded = False


class GameScreen:
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.width = width
        self.height = height

        self.font = pygame.font.SysFont("arial", 32, bold=True)
        self.small_font = pygame.font.SysFont("arial", 20, bold=True)
        self.tiny_font = pygame.font.SysFont("arial", 16)

        self.sounds = SoundBank()

        self.best_score = 0
        self.max_bomb_hits = 3
        self.enter()

    def enter(self):
        # sounds: start gameplay
        self.sounds.play_start()
        self.sounds.start_bg(volume=0.35)
        self._start_sound_cut_done = False


        self.fruits = []
        self.bombs = []
        self.powerups = []
        self.particles = []
        self.floating_texts = []

        self.ninja = Ninja()
        self.difficulty = DifficultyManager()

        self.spawn_timer = 0
        self.bomb_spawn_timer = 0
        self.powerup_spawn_timer = 0

        self.score = 0
        self.combo = 0
        self.max_combo = 0

        self.bomb_hits = 0

        self.game_time_ms = 0
        self.paused = False

        self.active_powerups = {"freeze": 0, "double_points": 0, "frenzy": 0}
        self.stats = {"fruits_sliced": 0, "bombs_hit": 0, "critical_hits": 0, "powerups_collected": 0}

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return "quit"
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                return "quit"
            if event.key == pygame.K_p:
                self.paused = not self.paused
        return None

    def update(self, dt):
        self.game_time_ms += int(dt * 1000)

        if self.paused:
            return None
        if not self._start_sound_cut_done:
            self.sounds.stop_start()
            self._start_sound_cut_done = True

        # ✅ Game over only by bombs
        if self.bomb_hits >= self.max_bomb_hits:
            self.best_score = max(self.best_score, self.score)

            # stop bg + play game over
            self.sounds.stop_bg()
            self.sounds.play_game_over()

            return ("game_over", self.score, self.best_score)

        keys = pygame.key.get_pressed()
        self.ninja.update(keys)

        for k in self.active_powerups:
            if self.active_powerups[k] > 0:
                self.active_powerups[k] -= 1

        if self.difficulty.update(self.score):
            self.floating_texts.append(
                FloatingText(self.width // 2 - 100, self.height // 2, f"LEVEL {self.difficulty.level}!", GOLD, self.font)
            )

        spawn_rate = self.difficulty.get_spawn_rate()
        if self.active_powerups["frenzy"] > 0:
            spawn_rate = max(10, spawn_rate // 2)

        if self.active_powerups["freeze"] == 0:
            self.spawn_timer += 1
            self.bomb_spawn_timer += 1
            self.powerup_spawn_timer += 1

        # fruits
        if self.spawn_timer > spawn_rate:
            self.fruits.append(Fruit(self.difficulty.get_fruit_speed(), self.small_font))
            self.spawn_timer = 0

        # bombs: interval + burst + speed with level
        bomb_interval = self.difficulty.get_bomb_interval()
        if self.bomb_spawn_timer > bomb_interval:
            burst = self.difficulty.get_bomb_burst_count()
            bomb_speed_range = self.difficulty.get_bomb_speed()

            # optional: spread bombs in a burst so it's fairer
            used_x = []
            for _ in range(burst):
                b = Bomb(bomb_speed_range)
                # try to keep some horizontal separation
                for _try in range(6):
                    if all(abs(b.x - x) > 80 for x in used_x):
                        break
                    b.x = random.randint(50, WIDTH - 50)
                used_x.append(b.x)
                self.bombs.append(b)

            self.bomb_spawn_timer = random.randint(-15, 0)

        # powerups
        if self.powerup_spawn_timer > 400:
            self.powerups.append(PowerUp(self.tiny_font))
            self.powerup_spawn_timer = 0

        slash_area = self.ninja.get_slash_area()

        # fruits
        for fruit in self.fruits[:]:
            if self.active_powerups["freeze"] == 0:
                fruit.update()

            if not fruit.sliced and fruit.get_rect().colliderect(slash_area):
                fruit.sliced = True
                self.fruits.remove(fruit)

                points = fruit.points
                if self.active_powerups["double_points"] > 0:
                    points *= 2
                if fruit.is_critical:
                    points *= 2
                    self.stats["critical_hits"] += 1
                    self.floating_texts.append(FloatingText(fruit.x - 50, fruit.y, "CRITICAL!", GOLD, self.font))

                self.score += points
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)
                self.stats["fruits_sliced"] += 1

                self.ninja.trigger_slash()
                self.sounds.play_slice()

                for _ in range(25):
                    self.particles.append(Particle(fruit.x, fruit.y, fruit.info["color"], "splash"))
                    self.particles.append(Particle(fruit.x, fruit.y, fruit.info["inner"], "splash"))

            elif fruit.y > self.height + 50:
                if fruit in self.fruits:
                    self.fruits.remove(fruit)
                    self.combo = 0

        # bombs
        for bomb in self.bombs[:]:
            if self.active_powerups["freeze"] == 0:
                bomb.update()

            if not bomb.sliced and bomb.get_rect().colliderect(slash_area):
                bomb.sliced = True
                self.bombs.remove(bomb)

                self.bomb_hits += 1
                self.combo = 0
                self.stats["bombs_hit"] += 1

                # (optional) also play slice sound on bomb hit
                self.sounds.play_slice()

                for _ in range(50):
                    self.particles.append(Particle(bomb.x, bomb.y, (255, 100, 0), "explosion"))
                    self.particles.append(Particle(bomb.x, bomb.y, (255, 200, 0), "explosion"))

                self.floating_texts.append(
                    FloatingText(bomb.x - 90, bomb.y, f"BOMB {self.bomb_hits}/{self.max_bomb_hits}", RED, self.font)
                )

            elif bomb.y > self.height + 50:
                if bomb in self.bombs:
                    self.bombs.remove(bomb)

        # powerups
        for p in self.powerups[:]:
            if self.active_powerups["freeze"] == 0:
                p.update()

            if not p.sliced and p.get_rect().colliderect(slash_area):
                p.sliced = True
                self.powerups.remove(p)
                self.active_powerups[p.type] = 300
                self.stats["powerups_collected"] += 1

                # slice sound works here too
                self.sounds.play_slice()

                msg = {"freeze": "TIME FREEZE!", "double_points": "DOUBLE POINTS!", "frenzy": "FRUIT FRENZY!"}[p.type]
                self.floating_texts.append(FloatingText(p.x - 80, p.y, msg, p.get_color(), self.font))

                for _ in range(30):
                    self.particles.append(Particle(p.x, p.y, p.get_color(), "splash"))

            elif p.y > self.height + 50:
                if p in self.powerups:
                    self.powerups.remove(p)

        # particles / floating text
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

        for text in self.floating_texts[:]:
            text.update()
            if text.lifetime <= 0:
                self.floating_texts.remove(text)

        return None

    def draw(self, surface):
        draw_background(surface, self.game_time_ms)

        for particle in self.particles:
            particle.draw(surface)
        for fruit in self.fruits:
            fruit.draw(surface)
        for bomb in self.bombs:
            bomb.draw(surface)
        for p in self.powerups:
            p.draw(surface)

        self.ninja.draw(surface)

        for text in self.floating_texts:
            text.draw(surface)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        surface.blit(score_text, (20, 20))

        if self.combo > 1:
            combo_color = GOLD if self.combo >= 10 else (YELLOW if self.combo >= 5 else WHITE)
            combo_text = self.font.render(f"x{self.combo} COMBO!", True, combo_color)
            surface.blit(combo_text, (self.width // 2 - 90, 20))

        level_text = self.small_font.render(f"Level: {self.difficulty.level}", True, WHITE)
        surface.blit(level_text, (20, 60))

        bomb_text = self.small_font.render(f"Bomb hits: {self.bomb_hits}/{self.max_bomb_hits}", True, (255, 200, 200))
        surface.blit(bomb_text, (self.width - 220, 20))

        y0 = 90
        if self.active_powerups["freeze"] > 0:
            surface.blit(self.small_font.render("Freeze", True, CYAN), (20, y0))
            y0 += 22
        if self.active_powerups["double_points"] > 0:
            surface.blit(self.small_font.render("x2 Points", True, GOLD), (20, y0))
            y0 += 22
        if self.active_powerups["frenzy"] > 0:
            surface.blit(self.small_font.render("Frenzy", True, PURPLE), (20, y0))
            y0 += 22

        if self.paused:
            t = self.font.render("PAUSED - Press P", True, WHITE)
            surface.blit(t, t.get_rect(center=(self.width // 2, self.height // 2)))
