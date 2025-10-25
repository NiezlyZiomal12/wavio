import pygame
from config import WIDTH, HEIGHT, BG_COLOR, FPS
from src import Camera, Player

class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Wavio")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Load assets
        player_sprites = pygame.image.load("src/assets/playerSpriteSheet.png").convert_alpha()        
        
        # Load objects
        self.player = Player(player_sprites, WIDTH // 2, HEIGHT // 2)
        self.camera = Camera(HEIGHT, WIDTH)


    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False


    def update(self) -> None:
        dt = self.clock.get_time() / 1000
        keys = pygame.key.get_pressed()
        
        self.player.update(dt,keys)
        self.camera.follow(self.player)


    def render(self) -> None:
        self.window.fill(BG_COLOR)
        self.player.draw(self.window, self.camera)

        pygame.display.update()


    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        pygame.quit()

def run_game():
    game = Game()
    game.run()

if __name__ == "__main__":
    run_game()