import pygame
import pytmx

from config import WIDTH, HEIGHT, BG_COLOR
from src.core import Camera, Timer
from src.gameplay.player.player_classes import Warrior, Mage, Rogue
from src.game_logic import EnemySpawner
from src.ui import LevelUpUi, PauseMenuUi, ShopUi
from ..Map import World
from src.gameplay.pickables import spawn_random_presents, trigger_bomb


CHARACTER_CLASSES = {
    "Warrior": Warrior,
    "Mage": Mage,
    "Rogue": Rogue,
}

DIFFICULTY_SETTINGS = {
    "Normal": {
        "enemy_hp_mult": 1.0,
        "enemy_damage_mult": 1.0,
        "enemy_speed_mult": 1.0,
        "xp_gain_mult": 1.0,
        "shop_price_mult": 1.0,
        "spawn_rate_mult": 1.0,
    },
    "Hard": {
        "enemy_hp_mult": 1.35,
        "enemy_damage_mult": 1.25,
        "enemy_speed_mult": 1.1,
        "xp_gain_mult": 0.85,
        "shop_price_mult": 1.25,
        "spawn_rate_mult": 1.15,
    },
    "Nightmare": {
        "enemy_hp_mult": 1.8,
        "enemy_damage_mult": 1.55,
        "enemy_speed_mult": 1.2,
        "xp_gain_mult": 0.7,
        "shop_price_mult": 1.5,
        "spawn_rate_mult": 1.3,
    },
}

class GameScene:
    def __init__(self, window: pygame.Surface, selected_character: str, selected_level:str, selected_difficulty: str = "Normal"):
        self.window = window
        self.running = True
        self.paused = False
        self.current_size = self.window.get_size()
        self.width, self.height = self.current_size
        self.selected_difficulty = selected_difficulty
        self.difficulty = DIFFICULTY_SETTINGS[self.selected_difficulty]

        bomb_image = pygame.image.load("src/assets/items/pickable/bomb.png").convert_alpha()
        prismat_image = pygame.image.load("src/assets/items/pickable/prismat.png").convert_alpha()
        stinky_fish = pygame.image.load("src/assets/items/pickable/stinky_fish.png").convert_alpha()

        # Tilemap
        self.level = pytmx.load_pygame(selected_level["tmx_path"])

        # Dropable
        self.xp_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()

        # Pickables
        pickable_list = [
            ("bomb", bomb_image),
            ("prismat", prismat_image),
            ("stinky_fish", stinky_fish),
        ]
        self.pickable_list = pickable_list
        self.pickables = pygame.sprite.Group()
        self.present_spawn_timer = 0.0
        self.present_spawn_interval = 60.0

        # Timer
        self.level_timer = Timer(20 * 60)

        # World
        map_world_width = self.level.width * self.level.tilewidth
        map_world_height = self.level.height * self.level.tileheight
        self.world = World(map_world_width, map_world_height, self.window)
        self.world.load_collisions(self.level)

        # Load objects
        selected_player_class = CHARACTER_CLASSES[selected_character]
        self.player = selected_player_class(self.width // 2, self.height // 2)
        self.player.xp_gain *= self.difficulty["xp_gain_mult"]
        self.camera = Camera(self.height, self.width, self.world)
        self.spawner = EnemySpawner(
            self.xp_group,
            self.coin_group,
            self.player,
            self.camera,
            enemy_hp_multiplier=self.difficulty["enemy_hp_mult"],
            enemy_damage_multiplier=self.difficulty["enemy_damage_mult"],
            enemy_speed_multiplier=self.difficulty["enemy_speed_mult"],
        )
        self.presents = pygame.sprite.Group()
        spawn_random_presents(
            50,
            self.presents,
            self.pickables,
            self.world.width,
            self.world.height,
            self.pickable_list,
            self.player,
            self.world.collision_rects,
        )

        # UI
        self.level_up_ui = LevelUpUi(self.window, WIDTH, HEIGHT, self.player)
        self.shop_ui = ShopUi(
            self.window,
            WIDTH,
            HEIGHT,
            self.player,
            price_multiplier=self.difficulty["shop_price_mult"],
        )
        self.pause_ui = PauseMenuUi(self.window, self.player)
        self.shop_timer = 1

        # FPS overlay
        self.fps_font = pygame.font.Font(None, 24)
        self.fps_smoothed = 0.0

        # Starter weapon based on selected character.
        starter_weapon = self.player.starting_weapon_name
        self.player.add_weapon(starter_weapon)


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
        if dt > 0:
            current_fps = 1.0 / dt
            if self.fps_smoothed == 0.0:
                self.fps_smoothed = current_fps
            else:
                self.fps_smoothed = (self.fps_smoothed * 0.9) + (current_fps * 0.1)

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
        self.present_spawn_timer += dt

        if self.present_spawn_timer >= self.present_spawn_interval:
            spawn_random_presents(
                10,
                self.presents,
                self.pickables,
                self.world.width,
                self.world.height,
                self.pickable_list,
                self.player,
                self.world.collision_rects,
            )
            self.present_spawn_timer = 0.0

        shoot_targets = list(self.spawner.enemies)
        shoot_targets.extend(present for present in self.presents if not present.spawning)

        self.player.update(dt, keys, shoot_targets, self.world.collision_rects)
        self.camera.follow(self.player)
        self.camera.update(dt)

        difficulty = self.difficulty["spawn_rate_mult"] * (1.0 + (self.level_timer.elapsed // 60))
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

        self.world.draw_tilemap(self.camera, self.level, self.window)

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

        fps_text = self.fps_font.render(f"FPS: {int(self.fps_smoothed)}", True, (255, 255, 255))
        fps_bg = pygame.Surface((fps_text.get_width() + 10, fps_text.get_height() + 6), pygame.SRCALPHA)
        fps_bg.fill((0, 0, 0, 140))
        fps_x = self.window.get_width() - fps_bg.get_width() - 10
        fps_y = 10
        self.window.blit(fps_bg, (fps_x, fps_y))
        self.window.blit(fps_text, (fps_x + 5, fps_y + 3))

