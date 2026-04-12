import pygame

from ..player import Player
from ..characters_config import CHARACTERS


class Mage(Player):
	def __init__(self, start_x: int, start_y: int) -> None:
		sprite_sheet = pygame.image.load("src/assets/player/mageSpriteSheet.png").convert_alpha()
		animation_config = {
			"frame_size": (64, 64),
			"animations": {
				"idle": {"row": 1, "frame_count": 4, "speed": 0.2},
				"walk": {"row": 0, "frame_count": 6, "speed": 0.1},
				"hurt": {"row": 1, "frame_count": 1, "speed": 0.1},
			},
		}
		super().__init__(sprite_sheet, start_x, start_y, animation_config=animation_config)
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
