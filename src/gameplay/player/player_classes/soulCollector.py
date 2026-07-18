import pygame

from ..player import Player
from ..characters_config import CHARACTERS

character_config = CHARACTERS["SoulCollector"]
class SoulCollector(Player):
	def __init__(self, start_x: int, start_y: int) -> None:
		sprite_sheet = pygame.image.load(character_config["Image_path"]).convert_alpha()
		animation_config = {
			"frame_size": character_config["animation_config"]["frame_size"],
			"animations": {
				"idle": {"row": 1, "frame_count": 4, "speed": 0.2},
				"walk": {"row": 0, "frame_count": 8, "speed": 0.1},
				"hurt": {"row": 1, "frame_count": 1, "speed": 0.1},
			},
		}
		super().__init__(sprite_sheet, start_x, start_y, animation_config=animation_config)
		self.class_name = "SoulCollector"
		self.unlocked = True

		self.max_health = character_config["Stats"]["max_health"]
		self.current_health = self.max_health
		self.speed = character_config["Stats"]["speed"]
		self.pickup_range = character_config["Stats"]["pickup_range"]
		self.damage = character_config["Stats"]["damage"]
		self.starting_weapon_name = character_config["Starting_weapon"]

		self.xp_gain *= character_config["Passive"]["xp_gain_mult"]
		self.item_stat_mult = character_config["Passive"]["item_stat_mult"]
		self.xp_damage_per_point = character_config["Passive"]["xp_damage_per_point"]
		self.total_xp_collected = 0

	def on_xp_collected(self, amount: int) -> None:
		self.total_xp_collected += amount
		self.damage += amount * self.xp_damage_per_point
		
