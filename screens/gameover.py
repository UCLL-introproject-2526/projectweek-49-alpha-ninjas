# screens/game_over.py
import pygame


class GameOverScreen:
    """
    Game Over screen for Ninja Cutter (fruit slicing).
    Usage:
        screen_obj = GameOverScreen(width, height)
        screen_obj.enter(final_score, best_score)
        action = screen_obj.update(events, dt)
        screen_obj.draw(surface)

    action will be one of:
        None, "retry", "menu", "quit"
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.final_score = 0
        self.best_score = None

        self._pulse_t = 0.0  # for small animation

        # Fonts are created after pygame.init() in most projects,
        # but pygame.font works as long as pygame.init() has been called.
        self.title_font = pygame.font.Font(None, 96)
        self.score_font = pygame.font.Font(None, 44)
        self.hint_font = pygame.font.Font(None, 30)

    def enter(self, final_score: int, best_score: int | None = None) -> None:
        self.final_score = int(final_score)
        self.best_score = int(best_score) if best_score is not None else None
        self._pulse_t = 0.0

    def update(self, events: list[pygame.event.Event], dt: float):
        """
        dt = seconds since last frame (e.g. clock.tick(60)/1000)
        Returns: None or "retry" or "menu" or "quit"
        """
        self._pulse_t += dt

        for event in events:
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

    def draw(self, surface: pygame.Surface) -> None:
        # Background
        surface.fill((12, 12, 18))

        # Subtle pulsing title (simple game feel)
        pulse = 1.0 + 0.03 * (pygame.math.Vector2(1, 0).rotate(self._pulse_t * 240).x)
        title_surf = self.title_font.render("GAME OVER", True, (255, 70, 70))
        title_surf = pygame.transform.smoothscale(
            title_surf,
            (int(title_surf.get_width() * pulse), int(title_surf.get_height() * pulse)),
        )

        title_rect = title_surf.get_rect(center=(self.width // 2, self.height // 2 - 140))
        surface.blit(title_surf, title_rect)

        # Score
        score_text = f"Score: {self.final_score}"
        score_surf = self.score_font.render(score_text, True, (230, 230, 240))
        score_rect = score_surf.get_rect(center=(self.width // 2, self.height // 2 - 35))
        surface.blit(score_surf, score_rect)

        # Best score (optional)
        if self.best_score is not None:
            best_text = f"Best: {self.best_score}"
            best_surf = self.score_font.render(best_text, True, (180, 210, 255))
            best_rect = best_surf.get_rect(center=(self.width // 2, self.height // 2 + 10))
            surface.blit(best_surf, best_rect)

        # Controls / hints
        hints = [
            "R  - Retry (slice again!)",
            "M - Back to Menu",
            "Q / ESC - Quit",
        ]
        y = self.height // 2 + 100
        for line in hints:
            hint_surf = self.hint_font.render(line, True, (170, 170, 185))
            hint_rect = hint_surf.get_rect(center=(self.width // 2, y))
            surface.blit(hint_surf, hint_rect)
            y += 36

        # Footer vibe
        footer = self.hint_font.render("Ninja Cutter — sharpen your reflexes.", True, (120, 120, 135))
        surface.blit(footer, footer.get_rect(center=(self.width // 2, self.height - 40)))
