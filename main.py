import pygame

class State:
    def __init__(self):
        self.x = 0

    def update(self):
        self.x += 1

    def render(self, surface):
        pygame.draw.circle(
            surface,
            (255, 0, 0),
            (self.x, 300),
            50
        )

def create_main_surface():
    WIDTH, HEIGHT = 800, 600
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("My Game")
    return surface

def render_frame(surface, state):
    state.render(surface)
    pygame.display.flip()

def MAIN():
    pygame.init()
    surface = create_main_surface()
    state = State()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        state.update()
        render_frame(surface, state)

MAIN()
