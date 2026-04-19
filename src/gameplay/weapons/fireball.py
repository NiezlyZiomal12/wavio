import pygame
from .weapon import Weapon
from src.core.utils import build_random_pitch_sounds

class Fireball(Weapon):
    _shoot_sounds: list[pygame.mixer.Sound] = None
    def __init__(self, config, start_pos, target_pos: pygame.Vector2, player: object):
        super().__init__(config, start_pos, player)

        direction = target_pos - start_pos
        if direction.length() > 0:
            self.velocity = direction.normalize() * self.speed
            self.facing_left = direction.x >0
        else:
            self.velocity = pygame.Vector2(0,0)
            self.facing_left = False
    
        self.lifetime = config['special']['lifetime']
        self.time_alive = 0.0

        Fireball._shoot_sounds = build_random_pitch_sounds("src/assets/sounds/game/weapons/fireball.wav", volume=0.05)
        self.shoot_sound = Fireball._shoot_sounds

    def update(self, dt:float):
        super().update(dt) 
        self.position += self.velocity * dt
        self.rect.center = self.position

        self.time_alive += dt
        if self.time_alive >= self.lifetime:
            self.kill()
    
        