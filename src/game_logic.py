import pygame
import random
from src import Slime
from config import HEIGHT, WIDTH, SPAWN_TIMER

class EnemySpawner:
    def __init__(self, slime_sprite: pygame.Surface, spawn_sprite: pygame.Surface, xp_group:pygame.sprite.Group , xp_sprite:pygame.Surface) -> None:
        self.slime_sprite = slime_sprite
        self.spawn_sprite = spawn_sprite
        self.enemies = []
        self.timer = 0.0
        self.xp_group = xp_group
        self.xp_sprite = xp_sprite

    def update(self,dt, player: object, fireball_group: pygame.sprite.Group= None, xp_group: pygame.sprite.Group= None) -> None:
        self.timer += dt
        if self.timer >= SPAWN_TIMER:
            self.spawn_slime()
            self.timer = 0.0
        
        for enemy in self.enemies:
            enemy.xp_group = xp_group
            enemy.xp_sprite = self.xp_sprite
            enemy.update(dt, player, self.enemies, fireball_group)

        for enemy in self.enemies:
            enemy.update(dt, player, self.enemies, fireball_group)
        
        self.enemies = [enemy for enemy in self.enemies if not enemy.killed]


    def draw(self, surface: pygame.Surface, camera: object) -> None:
        for enemy in self.enemies:
            enemy.draw(surface, camera)


    def spawn_slime(self) -> None:
        for i in range(3):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            slime = Slime(self.slime_sprite,x, y, self.spawn_sprite)
            self.enemies.append(slime)

