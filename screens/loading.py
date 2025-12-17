import pygame
from settings import COLORS, WIDTH, HEIGHT


class LoadingScreen:
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.width = width
        self.height = height

        self.bg_color = COLORS["bg_dark"]
        self.ninja_color = COLORS["light"]
        self.red = COLORS["red"]
        self.text_color = COLORS["text"]

        self.angle = -60
        self.show_title = False

        self.font = pygame.font.SysFont("arial", 48, bold=True)
        self.start_ms = 0

    def enter(self):
        self.angle = -60
        self.show_title = False
        self.start_ms = pygame.time.get_ticks()

    def handle_event(self, event):
        # Optional: allow skipping loading with any key
        if event.type == pygame.KEYDOWN:
            return "menu"
        return None

    def update(self, dt):
        if self.angle < 0:
            self.angle += 240 * dt  # 4 per frame at 60fps ≈ 240 per second
        else:
            self.show_title = True

        # End loading after 2.5 seconds
        if pygame.time.get_ticks() - self.start_ms > 2500:
            return "menu"
        return None

    def draw(self, surface):
        surface.fill(self.bg_color)

        ninja_x, ninja_y = self.width // 2, self.height // 2
        pygame.draw.circle(surface, self.ninja_color, (ninja_x, ninja_y), 60)

        if self.angle > -20:
            pygame.draw.line(
                surface,
                self.red,
                (ninja_x - 80, ninja_y - 40),
                (ninja_x + 80, ninja_y + 40),
                4,
            )

        if self.show_title:
            text = self.font.render("ALPHA NINJA", True, self.text_color)
            rect = text.get_rect(center=(self.width // 2, self.height - 100))
            surface.blit(text, rect)
