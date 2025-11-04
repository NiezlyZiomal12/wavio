import pygame
import random
from src.enemies import *
from config import HEIGHT, WIDTH, SPAWN_TIMER

class EnemySpawner:
    def __init__(self, spawn_sprite: pygame.Surface, xp_group:pygame.sprite.Group , xp_sprite:pygame.Surface) -> None:
        self.spawn_sprite = spawn_sprite
        self.enemies = []
        self.timer = 0.0
        self.xp_group = xp_group
        self.xp_sprite = xp_sprite

        self.enemy_sprites = {}
        for enemy_type in ENEMY_CONFIG.keys():
            self.enemy_sprites[enemy_type] = pygame.image.load(f"src/assets/{enemy_type}-Sheet.png").convert_alpha()

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
            x = random.randint(100, WIDTH - 100)
            y = random.randint(100, HEIGHT - 100)
    
            enemy_type = random.choice(enemy_types)
            config = ENEMY_CONFIG[enemy_type]
            sprite = self.enemy_sprites[enemy_type]
            enemy_class = self.enemy_classes[config["class"]]
            
            enemy = enemy_class(sprite, x, y, self.spawn_sprite, config)
            enemy.xp_group = self.xp_group
            enemy.xp_sprite = self.xp_sprite
            self.enemies.append(enemy)

