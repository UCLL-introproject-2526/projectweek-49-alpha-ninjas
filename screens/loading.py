import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dark Brown Background")

# Define colors
DARK_BROWN = (40, 26, 13)
BLACK = (0, 0, 0)

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Fill the screen with dark brown
    screen.fill(DARK_BROWN)
    
    # Update the display
    pygame.display.flip()
    
    # Control frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()