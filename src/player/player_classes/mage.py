from ..player import Player
from ..characters_config import CHARACTERS


class Mage(Player):
	def __init__(self, spriteSheet, start_x: int, start_y: int) -> None:
		super().__init__(spriteSheet, start_x, start_y)
		character_config = CHARACTERS["Mage"]
		self.class_name = "Mage"
		self.max_health = character_config["Stats"]["max_health"]
		self.current_health = self.max_health
		self.reduce_cooldown = character_config["Stats"]["reduce_cooldown"]
		self.projectile_count = character_config["Stats"]["projectile_count"]
		self.starting_weapon_name = character_config["Starting_weapon"]
		self.cd_mult = character_config["Passive"]["cd_mult"]
		self.dmg_mult = character_config["Passive"]["dmg_mult"]
