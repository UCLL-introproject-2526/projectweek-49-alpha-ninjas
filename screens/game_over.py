import pygame
from settings import WIDTH, HEIGHT


class GameOverScreen:
    """
    Returns actions: None, "retry", "menu", "quit"
    """

    def __init__(self, width=WIDTH, height=HEIGHT):
        self.width = width
        self.height = height

        self.final_score = 0
        self.best_score = None
        self._pulse_t = 0.0

        self.title_font = pygame.font.Font(None, 96)
        self.score_font = pygame.font.Font(None, 44)
        self.hint_font = pygame.font.Font(None, 30)

    def enter(self, final_score: int, best_score: int | None = None) -> None:
        self.final_score = int(final_score)
        self.best_score = int(best_score) if best_score is not None else None
        self._pulse_t = 0.0

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return "quit"

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                return "quit"
            if event.key == pygame.K_r:
                return "retry"
            if event.key == pygame.K_m:
                return "menu"
        return None

    def update(self, dt: float):
        self._pulse_t += dt
        return None

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((12, 12, 18))

        pulse = 1.0 + 0.03 * (pygame.math.Vector2(1, 0).rotate(self._pulse_t * 240).x)
        title_surf = self.title_font.render("GAME OVER", True, (255, 70, 70))
        title_surf = pygame.transform.smoothscale(
            title_surf,
            (int(title_surf.get_width() * pulse), int(title_surf.get_height() * pulse)),
        )

        surface.blit(title_surf, title_surf.get_rect(center=(self.width // 2, self.height // 2 - 140)))

        score_surf = self.score_font.render(f"Score: {self.final_score}", True, (230, 230, 240))
        surface.blit(score_surf, score_surf.get_rect(center=(self.width // 2, self.height // 2 - 35)))

        if self.best_score is not None:
            best_surf = self.score_font.render(f"Best: {self.best_score}", True, (180, 210, 255))
            surface.blit(best_surf, best_surf.get_rect(center=(self.width // 2, self.height // 2 + 10)))

        hints = ["R  - Retry (slice again!)", "M - Back to Menu", "Q / ESC - Quit"]
        y = self.height // 2 + 100
        for line in hints:
            hint_surf = self.hint_font.render(line, True, (170, 170, 185))
            surface.blit(hint_surf, hint_surf.get_rect(center=(self.width // 2, y)))
            y += 36

        footer = self.hint_font.render("Ninja Cutter — sharpen your reflexes.", True, (120, 120, 135))
        surface.blit(footer, footer.get_rect(center=(self.width // 2, self.height - 40)))
