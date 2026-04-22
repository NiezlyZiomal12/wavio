import pygame
import random
from src.gameplay.enemies import *
from src.gameplay.enemies.bosses import *
from config import SPAWN_TIMER, BOSS_SPAWN_TIMER

class EnemySpawner:
    def __init__(
        self,
        xp_group:pygame.sprite.Group,
        coin_group:pygame.sprite.Group,
        player:object,
        camera:object,
        enemy_hp_multiplier: float,
        enemy_damage_multiplier: float,
        enemy_speed_multiplier: float,
    ) -> None:
        self.spawn_sprite = pygame.image.load("src/assets/entities/enemies/spawn_animation_sheet.png").convert_alpha()
        self.xp_sprite = pygame.image.load("src/assets/items/dropable/xp.png").convert_alpha()
        self.coin_sprite = pygame.image.load("src/assets/items/dropable/coin.png").convert_alpha()
       
        self.enemies = []
        self.timer = 0.0
        self.boss_timer = 0.0
        self.game_time = 0.0
        self.xp_group = xp_group
        self.coin_group = coin_group
        self.player = player
        self.camera = camera
        self.enemy_hp_multiplier = enemy_hp_multiplier
        self.enemy_damage_multiplier = enemy_damage_multiplier
        self.enemy_speed_multiplier = enemy_speed_multiplier

        #loading enemy sprites
        self.enemy_sprites = {}
        for enemy_type in ENEMY_CONFIG.keys():
            self.enemy_sprites[enemy_type] = pygame.image.load(f"src/assets/entities/enemies/{enemy_type}-Sheet.png").convert_alpha()

        self.boss_sprites = {}
        #loading bosses sprites
        for boss_type in BOSS_CONFIG.keys():
            self.boss_sprites[boss_type] = pygame.image.load(f"src/assets/entities/bosses/{boss_type}-Sheet.png").convert_alpha()

        #adding enemy classes
        self.enemy_classes = {
            "Slime" : Slime,
            "Zombie" : Zombie,
            "Bat" : Bat,
        }
        self.boss_classes = {
            "Golem" : Golem
        }


    def update(self, dt: float, player: object, weapon_group: pygame.sprite.Group,
            collision_rects:list, difficulty:float =1.0) -> None:
        
        # track total game time
        self.timer += dt * difficulty
        self.game_time += dt
        self.boss_timer += dt

        if self.timer >= SPAWN_TIMER:
            self.spawn_enemies(collision_rects)
            self.timer = 0.0

        #BOSS tiemer
        if self.boss_timer >= BOSS_SPAWN_TIMER:
            boss_amount = 1 + int(self.game_time // 300)
            self.spawn_boss(boss_amount, collision_rects)
            self.boss_timer = 0.0

        # Update all living enemies (including bosses).
        for enemy in self.enemies:
            enemy.xp_group = self.xp_group
            enemy.xp_sprite = self.xp_sprite
            enemy.coin_group = self.coin_group
            enemy.coin_sprite = self.coin_sprite
            enemy.update(dt, player, self.enemies, weapon_group, collision_rects)

        self.enemies = [enemy for enemy in self.enemies if not enemy.killed]


    def draw(self, surface: pygame.Surface, camera: object) -> None:
        for enemy in self.enemies:
            enemy.draw(surface, camera)


    def spawn_enemies(self, collision_rects: list) -> None:
        total_enemies = random.randint(4, 8)
        enemy_types = list(ENEMY_CONFIG.keys())
        for i in range(total_enemies):
            enemy_type = random.choice(enemy_types)
            config = ENEMY_CONFIG[enemy_type]
            sprite = self.enemy_sprites[enemy_type]
            enemy_class = self.enemy_classes[config["class"]]

            x, y = self._spawn_outside_camera(config, collision_rects, margin=200)
            
            enemy = enemy_class(sprite, x, y, self.spawn_sprite, config, self.player)
            enemy.apply_time_scaling(
                self.game_time,
                hp_multiplier=self.enemy_hp_multiplier,
                damage_multiplier=self.enemy_damage_multiplier,
                speed_multiplier=self.enemy_speed_multiplier,
            )
            enemy.xp_group = self.xp_group
            enemy.xp_sprite = self.xp_sprite
            enemy.coin_group = self.coin_group
            enemy.coin_sprite = self.coin_sprite
            self.enemies.append(enemy)


    def spawn_boss(self, amount: int, collision_rects: list) -> None:
        boss_types = list(BOSS_CONFIG.keys())
        for i in range(amount):
            boss_type = random.choice(boss_types)
            config = BOSS_CONFIG[boss_type]
            sprite = self.boss_sprites[boss_type]
            boss_class = self.boss_classes[config["class"]]

            x, y = self._spawn_outside_camera(config, collision_rects, margin=260)
            
            boss = boss_class(sprite, x, y, self.spawn_sprite, config, self.player)
            # boss.apply_time_scaling(
            #     self.game_time,
            #     hp_multiplier=self.enemy_hp_multiplier,
            #     damage_multiplier=self.enemy_damage_multiplier,
            #     speed_multiplier=self.enemy_speed_multiplier,
            # )
            boss.xp_group = self.xp_group
            boss.xp_sprite = self.xp_sprite
            boss.coin_group = self.coin_group
            boss.coin_sprite = self.coin_sprite
            self.enemies.append(boss)


    def _is_valid_spawn_position(self, x: int, y: int, config: dict, collision_rects: list) -> bool:
        sprite_w = config["Animation"]["sprite_width"]
        sprite_h = config["Animation"]["sprite_height"]
        enemy_rect = pygame.Rect(0, 0, sprite_w, sprite_h)
        enemy_rect.center = (x, y)

        if any(enemy_rect.colliderect(rect) for rect in collision_rects):
            return False

        min_enemy_spacing = int(max(sprite_w, sprite_h) * 0.9)
        min_enemy_spacing_sq = min_enemy_spacing * min_enemy_spacing
        for enemy in self.enemies:
            if (enemy.position.x - x) ** 2 + (enemy.position.y - y) ** 2 < min_enemy_spacing_sq:
                return False

        # Prevent instant contact spawn on top of player.
        min_player_spacing = int(max(sprite_w, sprite_h) * 1.2)
        if (self.player.position.x - x) ** 2 + (self.player.position.y - y) ** 2 < min_player_spacing * min_player_spacing:
            return False

        return True


    def _random_point_outside_camera(self, margin: int) -> tuple[int, int]:
        cam_x = int(self.camera.offset.x)
        cam_y = int(self.camera.offset.y)
        screen_w = int(self.camera.width)
        screen_h = int(self.camera.height)

        left = cam_x - margin
        right = cam_x + screen_w + margin
        top = cam_y - margin
        bottom = cam_y + screen_h + margin

        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            return random.randint(left, right), top
        if side == "bottom":
            return random.randint(left, right), bottom
        if side == "left":
            return left, random.randint(top, bottom)
        return right, random.randint(top, bottom)


    def _spawn_outside_camera(self, config: dict, collision_rects: list, margin: int = 200) -> tuple[int, int]:
        sprite_w = config["Animation"]["sprite_width"]
        sprite_h = config["Animation"]["sprite_height"]
        half_w = max(16, sprite_w // 2)
        half_h = max(16, sprite_h // 2)
        world_w = int(self.camera.world.width)
        world_h = int(self.camera.world.height)

        for _ in range(40):
            x, y = self._random_point_outside_camera(margin)
            x = max(half_w, min(world_w - half_w, x))
            y = max(half_h, min(world_h - half_h, y))

            if self._is_valid_spawn_position(x, y, config, collision_rects):
                return x, y

        # Fallback if safe point is hard to find.
        for _ in range(80):
            x = random.randint(half_w, world_w - half_w)
            y = random.randint(half_h, world_h - half_h)
            if self._is_valid_spawn_position(x, y, config, collision_rects):
                return x, y

        # Last-resort spawn near player but still inside map bounds.
        return (
            max(half_w, min(world_w - half_w, int(self.player.position.x + random.randint(-120, 120)))),
            max(half_h, min(world_h - half_h, int(self.player.position.y + random.randint(-120, 120)))),
        )


