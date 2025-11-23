import pygame
from src.utils import Animation
import random


class Weapon(pygame.sprite.Sprite):
    def __init__(self, config: dict, sprite_sheet: pygame.sprite.Sprite, start_pos: pygame.Vector2, player:object):
        super().__init__()
        self.config = config

        #adding player attribute for some weapons 
        self.player = player

        self.speed = config['speed']
        self.sprite_width = config['animation']['sprite_width']
        self.sprite_height = config['animation']['sprite_height']
        self.cooldown = config['cooldown'] - (config['cooldown'] *self.player.reduce_cooldown)
        self.damage = config['damage'] * self.player.damage

        crit = random.random() < (self.player.crit_chance)
        if crit:
            self.damage *= 2

        self.animation = Animation(
            sprite_sheet,
            self.sprite_width,
            self.sprite_height,
            config['animation']["start_row"],
            config['animation']["start_frames"], 
            config['animation']["animation_speed"]
        )

        self.position = pygame.Vector2(start_pos)
        self.image = self.animation.get_current_frame()
        self.rect = self.image.get_rect(center=self.position)
        self.facing_left = False

        #single hit projectiles prop
        self.should_destroy_on_hit = True


    def update_animation(self, dt:float) -> None:
        self.image = self.animation.get_current_frame(flip_x=self.facing_left)
        self.animation.update(dt)

    
    def update(self, dt:float) -> None:
        self.update_animation(dt)


    def draw(self, surface:pygame.Surface, camera: object):
        surface.blit(self.image, camera.apply(self.rect))


