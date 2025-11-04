import pygame
from .weapon import Weapon

class Sword(Weapon):
    def __init__(self, config, sprite_sheet, start_pos):
        super().__init__(config, sprite_sheet, start_pos)