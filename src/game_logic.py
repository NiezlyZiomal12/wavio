import pygame
import random
from src.gameplay.enemies import *
from src.gameplay.enemies.bosses import *
from config import HEIGHT, WIDTH, SPAWN_TIMER, WORLD_HEIGHT, WORLD_WIDTH, BOSS_SPAWN_TIMER

class EnemySpawner:
    def __init__(self, xp_group:pygame.sprite.Group, coin_group:pygame.sprite.Group, player:object, camera:object) -> None:
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
            self.spawn_enemies()
            self.timer = 0.0

        #BOSS tiemer
        if self.boss_timer >= BOSS_SPAWN_TIMER:
            boss_amount = 1 + int(self.game_time // 300)
            self.spawn_boss(boss_amount)
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


    def spawn_enemies(self) -> None:
        total_enemies = random.randint(4, 8)
        enemy_types = list(ENEMY_CONFIG.keys())
        for i in range(total_enemies): 
            x,y = self._spawn_outside_camera(200)
    
            enemy_type = random.choice(enemy_types)
            config = ENEMY_CONFIG[enemy_type]
            sprite = self.enemy_sprites[enemy_type]
            enemy_class = self.enemy_classes[config["class"]]
            
            enemy = enemy_class(sprite, x, y, self.spawn_sprite, config, self.player)
            enemy.xp_group = self.xp_group
            enemy.xp_sprite = self.xp_sprite
            enemy.coin_group = self.coin_group
            enemy.coin_sprite = self.coin_sprite
            self.enemies.append(enemy)


    def spawn_boss(self, amount= int) -> None:
        boss_types = list(BOSS_CONFIG.keys())
        for i in range(amount): 
            x,y = self._spawn_outside_camera(200)
    
            boss_type = random.choice(boss_types)
            config = BOSS_CONFIG[boss_type]
            sprite = self.boss_sprites[boss_type]
            boss_class = self.boss_classes[config["class"]]
            
            boss = boss_class(sprite, x, y, self.spawn_sprite, config, self.player)
            boss.xp_group = self.xp_group
            boss.xp_sprite = self.xp_sprite
            boss.coin_group = self.coin_group
            boss.coin_sprite = self.coin_sprite
            self.enemies.append(boss)


    def _spawn_outside_camera(self, margin=200):
        cam_x, cam_y = self.camera.offset

        cam_x = int(cam_x)
        cam_y = int(cam_y)

        left = cam_x - margin
        right = cam_x + WIDTH + margin
        top = cam_y - margin
        bottom = cam_y + HEIGHT + margin

        left = int(left)
        right = int(right)
        top = int(top)
        bottom = int(bottom)

        side = random.choice(["top", "bottom", "left", "right"])

        if side == "top":
            x = random.randint(left, right)
            y = top
        elif side == "bottom":
            x = random.randint(left, right)
            y = bottom
        elif side == "left":
            x = left
            y = random.randint(top, bottom)
        else:
            x = right
            y = random.randint(top, bottom)

        x = max(32, min(WORLD_WIDTH - 32, x))
        y = max(32, min(WORLD_HEIGHT - 32, y))

        return x, y


