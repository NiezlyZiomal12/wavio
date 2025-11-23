import pygame
from config import WIDTH, HEIGHT, BG_COLOR, FPS, WORLD_WIDTH, WORLD_HEIGHT
from src import Camera, Player, EnemySpawner, LevelUpUi, loadUpgrades, World
import random

class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Wavio")
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        
        # Load assets
        spawning_sprites = pygame.image.load("src/assets/spawn_animation_sheet.png").convert_alpha()
        player_sprites = pygame.image.load("src/assets/playerSpriteSheet.png").convert_alpha()  
        fireball_sprites = pygame.image.load("src/assets/fireball.png").convert_alpha()    
        xp_sprite = pygame.image.load("src/assets/xp.png").convert_alpha()
        boomerang_sprites = pygame.image.load('src/assets/boomerang.png').convert_alpha()
        sword_sprites = pygame.image.load('src/assets/sword.png').convert_alpha()

        #XP
        self.xp_group = pygame.sprite.Group()
        
        #World
        self.world = World(WORLD_WIDTH, WORLD_HEIGHT)
        
        # Load objects
        self.player = Player(player_sprites, WIDTH // 2, HEIGHT // 2)
        self.camera = Camera(HEIGHT, WIDTH, self.world)
        self.spawner = EnemySpawner(spawning_sprites, self.xp_group, xp_sprite, self.player)
        self.upgrades = loadUpgrades()

        #UI
        self.level_up_ui = LevelUpUi(self.window, WIDTH, HEIGHT)
        
        #weapons
        self.player.add_weapon("Fireball", fireball_sprites)
        self.player.add_weapon("Boomerang", boomerang_sprites)
        self.player.add_weapon("Sword", sword_sprites)


    def handle_events(self) -> None:
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return

                #level up mechanics
                selection = self.level_up_ui.handle_event(event)
                if selection is not None:
                    upgrade = self.level_up_ui.options[selection]
                    upgrade.apply(self.player)
                    self.level_up_ui.hide()
                    continue
                
        except SystemError as e:
            print(f"Ignoring Pygame event error: {e}")


    def update(self) -> None:
        dt = self.clock.get_time() / 1000

        self.level_up_ui.update(dt)
        if self.level_up_ui.active:
            return
        
        keys = pygame.key.get_pressed()

        self.player.update(dt,keys,self.spawner.enemies)
        self.camera.follow(self.player)
        
        self.spawner.update(dt, self.player, self.player.active_projectiles, self.xp_group)
        self.xp_group.update(dt, self.player)

        #lvl up
        if self.player.just_leveled_up:
            self.player.just_leveled_up = False
            upgrades = random.sample(self.upgrades, 3)
            self.level_up_ui.show(upgrades)

        #World boundaries
        self.player.position = self.world.clamp_pos(self.player.position)
        self.player.rect.center
        for enemy in self.spawner.enemies:
            enemy.position = self.world.clamp_pos(enemy.position)
            enemy.rect.center = enemy.position
        for orb in self.xp_group:
            orb.position = self.world.clamp_pos(orb.position)
            orb.rect.center = orb.positiona


    def render(self) -> None:
        self.window.fill(BG_COLOR)

        for xp_orb in self.xp_group:
            xp_orb.draw(self.window, self.camera)

        self.spawner.draw(self.window, self.camera)
        self.player.draw(self.window, self.camera)

        if self.level_up_ui.active:
            self.level_up_ui.draw()

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