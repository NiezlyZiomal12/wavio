import pygame

from ..player import Player
from ..characters_config import CHARACTERS


class Mage(Player):
	def __init__(self, start_x: int, start_y: int) -> None:
		sprite_sheet = pygame.image.load("src/assets/player/mageSpriteSheet.png").convert_alpha()
		super().__init__(sprite_sheet, start_x, start_y)
		character_config = CHARACTERS["Mage"]
		self.class_name = "Mage"
		self.unlocked = True
		
		self.max_health = character_config["Stats"]["max_health"]
		self.current_health = self.max_health
		self.reduce_cooldown = character_config["Stats"]["reduce_cooldown"]
		self.projectile_count = character_config["Stats"]["projectile_count"]
		self.starting_weapon_name = character_config["Starting_weapon"]
		self.cd_mult = character_config["Passive"]["cd_mult"]
		self.dmg_mult = character_config["Passive"]["dmg_mult"]
