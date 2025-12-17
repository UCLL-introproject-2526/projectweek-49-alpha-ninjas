import pygame
from settings import WIDTH, HEIGHT, COLORS


class MenuScreen:
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.width = width
        self.height = height

        self.title_font = pygame.font.SysFont("arial", 72, bold=True)
        self.font = pygame.font.SysFont("arial", 28, bold=True)

        self.bg = (12, 12, 18)
        self.accent = COLORS["light"]
        self.text = COLORS["text"]

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
        surface.fill(self.bg)

        title = self.title_font.render("ALPHA NINJA", True, self.accent)
        surface.blit(title, title.get_rect(center=(self.width // 2, 170)))

        lines = [
            "Press ENTER / SPACE to Start",
            "Arrow Keys: Move",
            "SPACE + Arrow: Dash",
            "P: Pause",
            "Q / ESC: Quit",
        ]
        y = 290
        for line in lines:
            t = self.font.render(line, True, self.text)
            surface.blit(t, t.get_rect(center=(self.width // 2, y)))
            y += 42
