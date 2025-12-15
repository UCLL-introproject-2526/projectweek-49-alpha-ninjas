import pygame

def create_main_surface():
    WIDTH, HEIGHT = 800, 600
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("My Game")
    return surface

def render_frame(surface, x):
    pygame.draw.circle(
        surface,
        (255, 0, 0),
        (x, 300),
        50
    )
    pygame.display.flip()

def MAIN():
    pygame.init()
    surface = create_main_surface()
    x = 400
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        render_frame(surface, x)
        x += 1


MAIN()
