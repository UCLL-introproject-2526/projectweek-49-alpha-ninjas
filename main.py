import pygame
import sys

# 1. Initialize pygame
pygame.init()

# 2. Create a window
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Hello pygame")

# 3. Clock (controls FPS)
clock = pygame.time.Clock()

# 4. Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 5. Fill background color
    screen.fill((30, 30, 30))

    # 6. Update the screen
    pygame.display.flip()

    # 7. Limit FPS
    clock.tick(60)

# 8. Quit properly
pygame.quit()
sys.exit()
