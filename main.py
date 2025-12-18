import pygame
from settings import WIDTH, HEIGHT, FPS

from screens.loading import LoadingScreen
from screens.menu import MenuScreen
from screens.gameplay import GameScreen
from screens.game_over import GameOverScreen


FULLSCREEN = False

def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error:
        pass

    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    if FULLSCREEN:
        surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Alpha Ninja")
    clock = pygame.time.Clock()

    loading = LoadingScreen(WIDTH, HEIGHT)
    menu = MenuScreen(WIDTH, HEIGHT)
    gameplay = GameScreen(WIDTH, HEIGHT)
    gameover = GameOverScreen(WIDTH, HEIGHT)

    current = loading
    current.enter()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # seconds

        events = pygame.event.get()

        # 1) handle events
        action = None
        for event in events:
            a = current.handle_event(event)
            if a is not None:
                action = a
            # To toggle fullscreen mode
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()

        # 2) update (if no action yet)
        if action is None:
            action = current.update(dt)

        # 3) transitions
        if action == "quit":
            running = False

        elif action == "menu":
            current = menu
            current.enter()

        elif action == "start":
            gameplay.enter()
            current = gameplay

        elif action == "retry":
            gameplay.enter()
            current = gameplay

        elif isinstance(action, tuple) and action[0] == "game_over":
            _, final_score, best_score = action
            gameover.enter(final_score, best_score)
            current = gameover

        # 4) draw
        current.draw(surface)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
