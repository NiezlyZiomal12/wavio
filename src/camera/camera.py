import pygame
import random

class Camera:
    def __init__(self, height: int, width: int, world:object) -> None:
        self.offset = pygame.Vector2(0,0)
        self.height = height
        self.width = width
        self.lerp_speed = 0.1
        self.world = world
        self.flash_timer = 0
        self.shake_timer = 0
        self.shake_strength = 0


    def follow(self, target: pygame.sprite.Sprite) -> None:
        
        target_center = pygame.Vector2(target.rect.center)
        desired_offset = pygame.Vector2(
            target_center.x - self.width // 2,
            target_center.y - self.height // 2
        )
        self.offset += (desired_offset - self.offset) * self.lerp_speed
        self.offset = self.world.clamp_camera(
            self.offset, 
            self.width,
            self.height
        )


    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        shaken_rect = rect.move(-self.offset.x, -self.offset.y)

        if self.shake_timer > 0:
            shaken_rect.x += random.randint(-self.shake_strength, self.shake_strength)
            shaken_rect.y += random.randint(-self.shake_strength, self.shake_strength)
        return shaken_rect
    

    def update(self, dt:float):
        if self.flash_timer > 0:
            self.flash_timer -= dt

        if self.shake_timer > 0:
            self.shake_timer -= dt