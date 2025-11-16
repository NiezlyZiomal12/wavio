import pygame

class Upgrade(pygame.sprite.Sprite):
    def __init__(self, config:dict):
        super().__init__()

        self.name = config['name']
        self.description = config['description']
        self.image = config['image']
        self.effect = config['effect']


    def draw(self, surface:pygame.Surface, camera: object):
        surface.blit(self.image, camera.apply(self.rect))
 