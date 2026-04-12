import pygame

from ..player import Player
from ..characters_config import CHARACTERS


character_config = CHARACTERS["Warrior"]
class Warrior(Player):
	def __init__(self, start_x: int, start_y: int) -> None:
		sprite_sheet = pygame.image.load("src/assets/player/playerSpriteSheet.png").convert_alpha()
		animation_config = {
			"frame_size": (64, 64),
			"animations": {
				"idle": {"row": 0, "frame_count": 2, "speed": 0.5},
				"walk": {"row": 3, "frame_count": 8, "speed": 0.1},
				"hurt": {"row": 6, "frame_count": 3, "speed": 0.1},
			},
		}
		super().__init__(sprite_sheet, start_x, start_y, animation_config=animation_config)
		self.class_name = "Warrior"
		self.unlocked = True
		
		self.max_health = character_config["Stats"]["max_health"]
		self.current_health = self.max_health
		self.damage = character_config["Stats"]['damage']
		self.armor = character_config["Stats"]["armor"]
		self.speed = character_config["Stats"]["speed"]
		self.starting_weapon_name = character_config["Starting_weapon"]
		self.hp_mult = character_config["Passive"]["hp_mult"]
		self.armor_mult = character_config["Passive"]["armor_mult"]


# Backward-compatible alias.
Warior = Warrior
        
