import pygame

from ..player import Player
from ..characters_config import CHARACTERS

character_config = CHARACTERS["Rogue"]
class Rogue(Player):
	def __init__(self, start_x: int, start_y: int) -> None:
		sprite_sheet = pygame.image.load("src/assets/player/rougeSpriteSheet.png").convert_alpha()
		animation_config = {
			"frame_size": (43, 64),
			"animations": {
				"idle": {"row": 1, "frame_count": 4, "speed": 0.2},
				"walk": {"row": 0, "frame_count": 4, "speed": 0.2},
				"hurt": {"row": 0, "frame_count": 4, "speed": 0.1},
			},
		}
		super().__init__(sprite_sheet, start_x, start_y, animation_config=animation_config)
		self.class_name = "Rogue"
		self.unlocked = True
		
		self.max_health = character_config["Stats"]["max_health"]
		self.current_health = self.max_health
		self.speed = character_config["Stats"]["speed"]
		self.crit_chance = character_config["Stats"]["crit_chance"]
		self.starting_weapon_name = character_config["Starting_weapon"]
		self.speed_mult = character_config["Passive"]["speed_mult"]
		self.crit_mult = character_config["Passive"]["crit_mult"]


# Backward-compatible alias.
Rouge = Rogue
