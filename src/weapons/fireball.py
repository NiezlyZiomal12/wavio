import pygame
from .weapon import Weapon

class Fireball(Weapon):
    def __init__(self, config, sprite_sheet, start_pos, target_pos: pygame.Vector2):
        super().__init__(config, sprite_sheet, start_pos)

        direction = target_pos - start_pos
        if direction.length() > 0:
            self.velocity = direction.normalize() * self.speed
            self.facing_left = direction.x > 0
        else:
            self.velocity = pygame.Vector2(0,0)
            self.facing_left = False
    
        self.lifetime = 1.5
        self.time_alive = 0.0

    def update(self, dt:float):
        super().update(dt) 
        self.rect.center += self.velocity * dt

        self.time_alive += dt
        if self.time_alive >= self.lifetime:
            self.kill()
    
        