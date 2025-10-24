import pygame
from config import WIDTH, HEIGHT, BG_COLOR, NUM_ENEMIES

def run_game():
    pygame.init()
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Wavio")

    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(60)
        window.fill((30,30,30))

        pygame.display.update()

        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 

    pygame.quit()

if __name__ == "__main__":
     run_game()
