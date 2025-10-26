import pygame
import random
from src import Slime
from config import HEIGHT, WIDTH, SPAWN_TIMER

class EnemySpawner:
    def __init__(self, slime_sprite: pygame.Surface, spawn_sprite: pygame.Surface) -> None:
        self.slime_sprite = slime_sprite
        self.spawn_sprite = spawn_sprite
        self.enemies = []
        self.timer = 0.0


    def update(self,dt, player_pos: pygame.math.Vector2) -> None:
        self.timer += dt
        if self.timer >= SPAWN_TIMER:
            self.spawn_slime()
            self.timer = 0.0
        
        for enemy in self.enemies:
            enemy.update(dt, player_pos, self.enemies)


    def draw(self, surface: pygame.Surface, camera: object) -> None:
        for enemy in self.enemies:
            enemy.draw(surface, camera)


    def spawn_slime(self) -> None:
        for i in range(3):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            slime = Slime(self.slime_sprite,x, y, self.spawn_sprite)
            self.enemies.append(slime)

