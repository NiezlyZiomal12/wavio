import pygame
import pytmx

from config import WIDTH, HEIGHT, BG_COLOR, WORLD_WIDTH, WORLD_HEIGHT
from ..camera import Camera
from ..player import Player
from ..game_logic import EnemySpawner
from ..ui import LevelUpUi, PauseMenuUi, ShopUi
from ..Map import World
from ..pickables import spawn_random_presents, trigger_bomb
from ..timer import Timer


class GameScene:
    def __init__(self, window: pygame.Surface):
        self.window = window
        self.running = True
        self.paused = False

        # Load assets
        spawning_sprites = pygame.image.load("src/assets/enemies/spawn_animation_sheet.png").convert_alpha()
        player_sprites = pygame.image.load("src/assets/player/playerSpriteSheet.png").convert_alpha()
        fireball_sprites = pygame.image.load("src/assets/weapons/fireball.png").convert_alpha()
        xp_sprite = pygame.image.load("src/assets/dropable/xp.png").convert_alpha()
        coin_sprites = pygame.image.load("src/assets/dropable/coin.png").convert_alpha()
        boomerang_sprites = pygame.image.load("src/assets/weapons/boomerang.png").convert_alpha()
        sword_sprites = pygame.image.load("src/assets/weapons/sword.png").convert_alpha()
        present_image = pygame.image.load("src/assets/pickable/present.png").convert_alpha()
        bomb_image = pygame.image.load("src/assets/pickable/bomb.png").convert_alpha()
        prismat_image = pygame.image.load("src/assets/pickable/prismat.png").convert_alpha()
        stinky_fish = pygame.image.load("src/assets/pickable/stinky_fish.png").convert_alpha()

        # Tilemap
        self.level1 = pytmx.load_pygame("src/assets/tilemaps/tmx/level1_new.tmx")

        # Dropable
        self.xp_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()

        # Pickables
        pickable_list = [
            ("bomb", bomb_image),
            ("prismat", prismat_image),
            ("stinky_fish", stinky_fish),
        ]
        self.pickables = pygame.sprite.Group()

        # Timer
        self.level_timer = Timer(20 * 60)

        # World
        self.world = World(WORLD_WIDTH, WORLD_HEIGHT)
        self.world.load_collisions(self.level1)

        # Load objects
        self.player = Player(player_sprites, WIDTH // 2, HEIGHT // 2)
        self.camera = Camera(HEIGHT, WIDTH, self.world)
        self.spawner = EnemySpawner(
            spawning_sprites,
            self.xp_group,
            xp_sprite,
            self.coin_group,
            coin_sprites,
            self.player,
            self.camera,
        )
        self.presents = pygame.sprite.Group()
        spawn_random_presents(
            5,
            self.presents,
            self.pickables,
            WORLD_WIDTH,
            WORLD_HEIGHT,
            present_image,
            pickable_list,
            self.player,
        )

        # UI
        self.level_up_ui = LevelUpUi(self.window, WIDTH, HEIGHT, self.player)
        self.weapon_sprites = {
            "Fireball": fireball_sprites,
            "Boomerang": boomerang_sprites,
            "Sword": sword_sprites,
        }
        self.shop_ui = ShopUi(self.window, WIDTH, HEIGHT, self.player, self.weapon_sprites)
        self.pause_ui = PauseMenuUi(self.window, WIDTH, HEIGHT, self.player)
        self.shop_timer = 30

        # Starter weapon so the player can fight before first shop.
        self.player.add_weapon("Fireball", fireball_sprites)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        try:
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    return

                # Pausing the game
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.pause_ui.toggle()
                    self.paused = self.pause_ui.active
                    continue

                if self.pause_ui.active:
                    self.pause_ui.handle_event(event)
                    continue

                # Level up mechanics
                selection = self.level_up_ui.handle_event(event)
                if selection is not None:
                    upgrade = self.level_up_ui.options[selection]
                    upgrade.apply(self.player)
                    self.level_up_ui.hide()
                    continue

                # Shop UI
                self.shop_ui.handle_event(event)

        except SystemError as error:
            print(f"Ignoring Pygame event error: {error}")

    def update(self, dt: float) -> None:
        self.pause_ui.update(dt)
        if self.pause_ui.active:
            self.paused = True
            return

        # Shop timer
        if self.level_timer.elapsed >= self.shop_timer:
            self.shop_ui.show()
            self.shop_timer += 30

        self.level_up_ui.update(dt)
        self.shop_ui.update(dt)
        if self.level_up_ui.active or self.shop_ui.active:
            return

        self.paused = False

        keys = pygame.key.get_pressed()
        self.level_timer.update(dt)
        self.player.update(dt, keys, self.spawner.enemies, self.world.collision_rects)
        self.camera.follow(self.player)
        self.camera.update(dt)

        difficulty = 1.0 + (self.level_timer.elapsed // 60)
        self.spawner.update(
            dt,
            self.player,
            self.player.active_projectiles,
            self.world.collision_rects,
            difficulty,
        )
        self.xp_group.update(dt, self.player)
        self.coin_group.update(dt, self.player)
        self.pickables.update(dt, self.player)
        self.presents.update(dt, self.player.active_projectiles)

        # Timer finished
        if self.level_timer.finished:
            self.running = False

        # Bomb pickup
        if self.player.pending_effect == "bomb":
            trigger_bomb(self.spawner, self.camera)
            self.player.pending_effect = None

        # Level up
        if self.player.just_leveled_up:
            self.player.just_leveled_up = False
            self.level_up_ui.show()

        # World boundaries
        self.player.position = self.world.clamp_pos(self.player.position)
        self.player.rect.center = self.player.position
        for enemy in self.spawner.enemies:
            enemy.position = self.world.clamp_pos(enemy.position)
            enemy.rect.center = enemy.position
        for orb in self.xp_group:
            orb.position = self.world.clamp_pos(orb.position)
            orb.rect.center = orb.position
        for coin in self.coin_group:
            coin.position = self.world.clamp_pos(coin.position)
            coin.rect.center = coin.position
        for pick in self.pickables:
            pick.position = self.world.clamp_pos(pick.position)
            pick.rect.center = pick.position
        for present in self.presents:
            present.position = self.world.clamp_pos(present.position)
            present.rect.center = present.position

        for proj in self.player.active_projectiles:
            if not (0 <= proj.position.x <= self.world.width and 0 <= proj.position.y <= self.world.height):
                proj.kill()

    def render(self) -> None:
        self.window.fill(BG_COLOR)

        self.world.draw_tilemap(self.camera, self.level1, self.window)

        for xp_orb in self.xp_group:
            xp_orb.draw(self.window, self.camera)

        for coin in self.coin_group:
            coin.draw(self.window, self.camera)

        for pickable in self.pickables:
            pickable.draw(self.window, self.camera)

        for present in self.presents:
            present.draw(self.window, self.camera)

        self.spawner.draw(self.window, self.camera)
        self.player.draw(self.window, self.camera)
        self.level_timer.draw(self.window)

        if self.level_up_ui.active:
            self.level_up_ui.draw()

        if self.shop_ui.active:
            self.shop_ui.draw()

        if self.pause_ui.active:
            self.pause_ui.draw()

        # Bomb flash
        if self.camera.flash_timer > 0:
            fade = self.camera.flash_timer / 0.2
            alpha = int(255 * fade)
            flash_surface = pygame.Surface(self.window.get_size(), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, alpha))
            self.window.blit(flash_surface, (0, 0))

        pygame.display.update()
