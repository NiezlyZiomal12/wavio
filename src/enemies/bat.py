import pygame
from .enemy import Enemy

class Bat(Enemy):
    def move(self, player_pos: pygame.Vector2, other_enemies: list) -> None:
        """Flying enemies ignore ground collisions"""
        if self.dead:
            return
        
        direction = player_pos - self.position
        if direction.length() > 1:
            direction = direction.normalize() * self.speed
            self.position += direction
            
            self.facing_left = direction.x < 0
            self.rect.center = (int(self.position.x), int(self.position.y))