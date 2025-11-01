import pygame
from src.utils import Animation

class Fireball(pygame.sprite.Sprite):
    def __init__(self, spritesheet:pygame.Surface, start_pos: pygame.Vector2, target_pos: pygame.Vector2):
        super().__init__()
        self.speed = 8
        self.animation = Animation(spritesheet, 51, 32, 0, 4, 0.1)
        self.image = self.animation.get_current_frame()
        self.rect = self.image.get_rect(center=start_pos)

        direction = target_pos - start_pos
        if direction.length() > 0:
            self.velocity = direction.normalize() * self.speed
            self.facing_left = direction.x > 0
        else:
            self.velocity = pygame.Vector2(0,0)
            self.facing_left = False
    

    def update(self, dt:float):
        self.animation.update(dt)
        self.image = self.animation.get_current_frame(flip_x=self.facing_left)
        self.rect.center += self.velocity
    

    def draw(self, surface:pygame.Surface, camera: object):
        surface.blit(self.image, camera.apply(self.rect))
        