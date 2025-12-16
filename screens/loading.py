import pygame

class LoadingScreen:
    def __init__(self, surface):
        self.surface = surface
        self.clock = pygame.time.Clock()

        self.bg_color = (43, 11, 14)     # dark maroon
        self.ninja_color = (244, 245, 154)  # warm yellow
        self.red = (216, 52, 26)

        self.angle = -60
        self.show_title = False
        self.done = False

        self.font = pygame.font.SysFont("arial", 48, bold=True)
        self.start_time = pygame.time.get_ticks()

    def update(self):
        if self.angle < 0:
            self.angle += 4
        else:
            self.show_title = True

        # End loading after 2.5 seconds
        if pygame.time.get_ticks() - self.start_time > 2500:
            self.done = True

    def render(self):
        self.surface.fill(self.bg_color)

        # Fake ninja (circle placeholder)
        ninja_x, ninja_y = 400, 300
        pygame.draw.circle(
            self.surface,
            self.ninja_color,
            (ninja_x, ninja_y),
            60
        )

        # Fake sword slash
        if self.angle > -20:
            pygame.draw.line(
                self.surface,
                self.red,
                (ninja_x - 80, ninja_y - 40),
                (ninja_x + 80, ninja_y + 40),
                4
            )

        # Title text
        if self.show_title:
            text = self.font.render("ALPHA NINJA", True, (246, 242, 232))
            rect = text.get_rect(center=(400, 500))
            self.surface.blit(text, rect)

        pygame.display.flip()
        self.clock.tick(60)
