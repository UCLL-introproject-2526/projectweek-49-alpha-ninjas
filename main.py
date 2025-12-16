import pygame
from screens.loading import LoadingScreen

<<<<<<< Updated upstream
=======
class State:
    def __init__(self):
        self.x = 0

    def update(self):
        self.x += 1

    def render(self, surface):
        pygame.draw.circle(surface, (255, 0, 0), (self.x, 300), 50)

>>>>>>> Stashed changes
def create_main_surface():
    surface = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Alpha Ninja")
    return surface

<<<<<<< Updated upstream
def render_frame(surface):
    pygame.draw.circle(
        surface,
        (255, 0, 0),
        (400, 300),
        50
    )
=======
def render_frame(surface, state):
    surface.fill((0, 0, 0))
    state.render(surface)
>>>>>>> Stashed changes
    pygame.display.flip()

def MAIN():
    pygame.init()
    surface = create_main_surface()
<<<<<<< Updated upstream
=======

    # ✅ LOADING SCREEN (NO IMAGES)
    loading = LoadingScreen(surface)
    while not loading.done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()



        loading.update()
        loading.render()

    # ✅ GAME STARTS
>>>>>>> Stashed changes

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        render_frame(surface)

MAIN()
