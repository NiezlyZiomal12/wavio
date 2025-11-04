import pygame
from src.utils import Animation


class Weapon(pygame.sprite.Sprite):
    def __init__(self, config: dict, sprite_sheet: pygame.sprite.Sprite, start_pos: pygame.Vector2):
        super().__init__()
        self.config = config

        self.speed = config['speed']
        self.sprite_width = config.get('sprite_width')
        self.sprite_height = config.get("sprite_height")
        self.cooldown = config['cooldown']
        self.projectile_count = config['projectile_count']
        self.damage = config['damage']

        self.animation = Animation(
            sprite_sheet,
            self.sprite_width,
            self.sprite_height,
            config["start_row"],
            config["start_frames"], 
            config["animation_speed"]
        )

        self.image = self.animation.get_current_frame()
        self.rect = self.image.get_rect(center=start_pos)
        self.facing_left = False


    def update_animation(self, dt:float) -> None:
        self.image = self.animation.get_current_frame(flip_x=self.facing_left)

    
    def update(self, dt:float) -> None:
        self.update_animation(dt)


    def draw(self, surface:pygame.Surface, camera: object):
        surface.blit(self.image, camera.apply(self.rect))


