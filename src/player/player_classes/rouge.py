from ..player import Player
from ..characters_config import CHARACTERS

character_config = CHARACTERS["Rogue"]
class Rogue(Player):
	def __init__(self, spriteSheet, start_x: int, start_y: int) -> None:
		super().__init__(spriteSheet, start_x, start_y)
		self.class_name = "Rogue"
		self.max_health = character_config["Stats"]["max_health"]
		self.current_health = self.max_health
		self.speed = character_config["Stats"]["speed"]
		self.crit_chance = character_config["Stats"]["crit_chance"]
		self.starting_weapon_name = character_config["Starting_weapon"]
		self.speed_mult = character_config["Passive"]["speed_mult"]
		self.crit_mult = character_config["Passive"]["crit_mult"]


# Backward-compatible alias.
Rouge = Rogue
