import pygame

def create_main_surface():
    WIDTH, HEIGHT = 800, 600
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("My Game")
    return surface

def render_frame(surface):
    pygame.draw.circle(
        surface,
        (255, 0, 0),
        (400, 300),
        50
    )
    pygame.display.flip()

def MAIN():
    pygame.init()
    surface = create_main_surface()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        render_frame(surface)

MAIN()
