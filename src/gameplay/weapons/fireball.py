import pygame
from .weapon import Weapon
import random

class Fireball(Weapon):
    def __init__(self, config, sprite_sheet, start_pos, target_pos: pygame.Vector2, player: object):
        super().__init__(config, sprite_sheet, start_pos, player)

        #slight offset for more randomness
        offset_strength = 0.005
        direction = target_pos - start_pos
        if direction.length() > 0:
            offset = pygame.Vector2(-direction.y, direction.x)
            offset *= random.uniform(-offset_strength, offset_strength) * direction.length()
            direction += offset

            self.velocity = direction.normalize() * self.speed
            self.facing_left = direction.x >0
        else:
            self.velocity = pygame.Vector2(0,0)
            self.facing_left = False
    
        self.lifetime = config['special']['lifetime']
        self.time_alive = 0.0

    def update(self, dt:float):
        super().update(dt) 
        self.position += self.velocity * dt
        self.rect.center = self.position

        self.time_alive += dt
        if self.time_alive >= self.lifetime:
            self.kill()
    
        