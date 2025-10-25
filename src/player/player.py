import pygame
from config import PLAYER_SPEED
from ..utils.Animation import Animation


class Player(pygame.sprite.Sprite):
    def __init__(self, spriteSheet:pygame.Surface, start_x:int, start_y:int) -> None:
        super().__init__()
        self.speed = PLAYER_SPEED
        self.position = pygame.math.Vector2(start_x, start_y)
        self.sprite_size = 32

        #Animations
        self.idle_animation = Animation(spriteSheet, self.sprite_size, self.sprite_size, 0, 2, 0.5)
        self.walk_animation = Animation(spriteSheet, self.sprite_size, self.sprite_size, 3, 8, 0.1)        
        self.current_animation = self.idle_animation
        self.image = self.current_animation.get_current_frame()
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.facing_left = False


    def move(self, keys: pygame.key.ScancodeWrapper) -> None:
        # Create movement vector
        movement = pygame.math.Vector2(0, 0)
        
        if keys[pygame.K_w]: movement.y -= 1
        if keys[pygame.K_s]: movement.y += 1
        if keys[pygame.K_a]:
            movement.x -= 1
            self.facing_left = True
        if keys[pygame.K_d]:
            movement.x += 1
            self.facing_left = False
        
        if movement.length() > 0:
            movement = movement.normalize() * self.speed

            if self.current_animation != self.walk_animation:
                self.walk_animation.reset()
                self.current_animation = self.walk_animation
        else:
            if self.current_animation != self.idle_animation:
                self.idle_animation.reset()
                self.current_animation = self.idle_animation

        self.position += movement
        self.rect.center = (int(self.position.x), int(self.position.y))


    def update_animation(self, dt: float) -> None:
        self.current_animation.update(dt)
        self.image = self.current_animation.get_current_frame(flip_x=self.facing_left)


    def update(self,dt:float, keys:pygame.key.ScancodeWrapper):
        self.move(keys)
        self.update_animation(dt)


    def draw(self, surface:pygame.Surface, camera: object):
        surface.blit(self.image, camera.apply(self.rect))