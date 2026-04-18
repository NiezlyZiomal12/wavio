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
            delta = self.effect["damage"] * player.dmg_mult
            player.damage = max(1, int(round(player.damage + delta)))

        elif self.name == "Boots":
            delta = self.effect['speed'] * player.speed_mult
            player.speed = max(1, int(round(player.speed + delta)))

        elif self.name == "Heart":
            delta = int(round(self.effect["max_health"] * player.hp_mult))
            player.max_health = max(1, int(player.max_health + delta))
            # Keep current hp in step with max hp growth for better game feel.
            player.current_health = min(player.max_health, player.current_health + delta)

        elif self.name == "Armor":
            delta = self.effect['armor'] * player.armor_mult
            player.armor = max(0.0, min(0.8, player.armor + delta))

        elif self.name == "Pearl":
            player.projectile_count = int(player.projectile_count + self.effect['projectile_count'])

        elif self.name == "Scroll":
            delta = self.effect['reduce_cooldown'] * player.cd_mult
            player.reduce_cooldown = max(0.0, min(0.8, player.reduce_cooldown + delta))

        player.upgrade_levels[self.name] = current_level + 1
        return True

 

def loadUpgrades():
    return [Upgrade(config) for config in UPGRADE_CONFIG.values()]