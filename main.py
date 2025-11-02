import pygame
from config import WIDTH, HEIGHT, BG_COLOR, FPS
from src import Camera, Player, EnemySpawner

class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Wavio")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Load assets
        spawning_sprites = pygame.image.load("src/assets/spawn_animation_sheet.png").convert_alpha()
        player_sprites = pygame.image.load("src/assets/playerSpriteSheet.png").convert_alpha()  
        self.fireball_sprites = pygame.image.load("src/assets/fireball.png").convert_alpha()    
        xp_sprite = pygame.image.load("src/assets/xp.png").convert_alpha()

        #XP
        self.xp_group = pygame.sprite.Group()
        
        # Load objects
        self.player = Player(player_sprites, WIDTH // 2, HEIGHT // 2)
        self.camera = Camera(HEIGHT, WIDTH)
        self.spawner = EnemySpawner(spawning_sprites, self.xp_group, xp_sprite)
        
        #weapons
        self.fireballs = pygame.sprite.Group()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False


    def update(self) -> None:
        dt = self.clock.get_time() / 1000
        keys = pygame.key.get_pressed()
        
        self.player.update(dt,keys)
        self.camera.follow(self.player)
        self.player.shoot(dt, self.fireballs, self.fireball_sprites, self.spawner.enemies)
        
        self.spawner.update(dt, self.player, self.fireballs, self.xp_group)
        self.xp_group.update(dt, self.player)
        self.fireballs.update(dt)



    def render(self) -> None:
        self.window.fill(BG_COLOR)

        for xp_orb in self.xp_group:
            xp_orb.draw(self.window, self.camera)

        self.spawner.draw(self.window, self.camera)

        for fireball in self.fireballs:
            fireball.draw(self.window, self.camera)
        
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