import pygame
from .upgrade_config import UPGRADE_CONFIG

class Upgrade(pygame.sprite.Sprite):
    def __init__(self, config:dict):
        super().__init__()

        self.name = config['name']
        self.description = config['description']
        self.image = pygame.image.load(config['image']).convert_alpha()
        self.effect = config['effect']
        self.max_level = config['max_level']


    def draw(self, surface:pygame.Surface, camera: object):
        surface.blit(self.image, camera.apply(self.rect))


    def is_maxed(self, player) -> bool:
        current_level = player.upgrade_levels.get(self.name, 0)
        return current_level >= self.max_level


    def apply(self, player) -> bool:
        current_level = player.upgrade_levels.get(self.name, 0)
        if current_level >= self.max_level:
            return False

        if self.name == "Order":
            player.damage *= (1 +self.effect["damage"]) * player.dmg_mult

        elif self.name == "Boots":
            player.speed *= (1 +self.effect['speed']) * player.speed_mult

        elif self.name == "Heart":
            player.max_health *= (1 + self.effect["max_health"]) * player.hp_mult

        elif self.name == "Armor":
            player.armor *= (1 + self.effect['armor']) * player.armor_mult

        elif self.name == "Pearl":
            player.projectile_count += self.effect['projectile_count']

        elif self.name == "Scroll":
            player.reduce_cooldown *= (1 + self.effect['reduce_cooldown']) * player.cd_mult

        player.upgrade_levels[self.name] = current_level + 1
        return True

 

def loadUpgrades():
    return [Upgrade(config) for config in UPGRADE_CONFIG.values()]