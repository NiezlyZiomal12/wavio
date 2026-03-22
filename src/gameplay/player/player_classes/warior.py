from ..player import Player
from ..characters_config import CHARACTERS


character_config = CHARACTERS["Warrior"]
class Warrior(Player):
	def __init__(self, spriteSheet, start_x: int, start_y: int) -> None:
		super().__init__(spriteSheet, start_x, start_y)
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
        
