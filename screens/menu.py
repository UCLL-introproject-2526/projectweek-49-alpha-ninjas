import pygame
from settings import WIDTH, HEIGHT, COLORS

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))


class MenuScreen:
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.width = width
        self.height = height

        self.title_font = pygame.font.SysFont("arial", 72, bold=True)
        self.font = pygame.font.SysFont("arial", 28, bold=True)

        self.bg = (12, 12, 18)
        self.accent = COLORS["light"]
        self.text = COLORS["text"]

        # LOAD BACKGROUND ONCE
        self.background = pygame.image.load(
            "assets/images/loading_screen.png"
        ).convert()
        self.background = pygame.transform.smoothscale(
            self.background, (self.width, self.height)
        )

    def enter(self):
        pass

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return "quit"
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return "start"
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                return "quit"
        return None

    def update(self, dt):
        return None

    def draw(self, surface):
        surface.blit(self.background, (0, 0))
