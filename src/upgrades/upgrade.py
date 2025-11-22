import pygame
from .upgrade_config import UPGRADE_CONFIG

class Upgrade(pygame.sprite.Sprite):
    def __init__(self, config:dict):
        super().__init__()

        self.name = config['name']
        self.description = config['description']
        self.image = pygame.image.load(config['image']).convert_alpha()
        self.effect = config['effect']


    def draw(self, surface:pygame.Surface, camera: object):
        surface.blit(self.image, camera.apply(self.rect))


    def apply(self, player):
        if self.name == "Order":
            player.damage *= (1 +self.effect["damage"])

        elif self.name == "Boots":
            player.speed *= (1 +self.effect['speed'])

        elif self.name == "Heart":
            player.max_health *= (1 + self.effect["max_health"])

        elif self.name == "Armor":
            player.armor *= (1 + self.effect['armor'])

        elif self.name == "Pearl":
            player.projectile_count += self.effect['projectile_count']

        elif self.name == "Scroll":
            player.reduce_cooldown *= (1 + self.effect['reduce_cooldown'])

 

def loadUpgrades():
    return [Upgrade(config) for config in UPGRADE_CONFIG.values()]