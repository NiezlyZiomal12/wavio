import pygame
import random
from src.enemies import *
from config import HEIGHT, WIDTH, SPAWN_TIMER, WORLD_HEIGHT, WORLD_WIDTH

class EnemySpawner:
    def __init__(self, spawn_sprite: pygame.Surface, xp_group:pygame.sprite.Group , xp_sprite:pygame.Surface, player:object, camera:object) -> None:
        self.spawn_sprite = spawn_sprite
        self.enemies = []
        self.timer = 0.0
        self.xp_group = xp_group
        self.xp_sprite = xp_sprite
        self.player = player
        self.camera = camera

        #loading enemy sprites
        self.enemy_sprites = {}
        for enemy_type in ENEMY_CONFIG.keys():
            self.enemy_sprites[enemy_type] = pygame.image.load(f"src/assets/{enemy_type}-Sheet.png").convert_alpha()

        #adding enemy classes
        self.enemy_classes = {
            "Slime" : Slime,
            "Zombie" : Zombie,
            "Bat" : Bat,
        }


    def update(self,dt, player: object, weapon_groups: dict, xp_group: pygame.sprite.Group= None) -> None:
        self.timer += dt
        if self.timer >= SPAWN_TIMER:
            self.spawn_enemies()
            self.timer = 0.0
        
        #killing enemies and dropping xp
        for enemy in self.enemies:
            enemy.xp_group = xp_group
            enemy.xp_sprite = self.xp_sprite
            enemy.update(dt, player, self.enemies, weapon_groups)
        
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
            self.enemies.append(enemy)


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


