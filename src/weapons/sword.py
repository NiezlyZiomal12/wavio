import pygame
from .weapon import Weapon

class Sword(Weapon):
    def __init__(self, config, sprite_sheet, start_pos, target_pos : pygame.Vector2, player= None):
        super().__init__(config, sprite_sheet, start_pos, player)

        self.attack_radius = config['special']['attack_radius']
        self.attack_duration = config['special']['attack_duration']
        # Track swing timing
        self.time_alive = 0.0
        self.facing_left = target_pos.x < player.rect.centerx
        self.should_destroy_on_hit = False
        
        self.swing_done = False 
        self.recent_hits = set()

        self.offset_distance = self.attack_radius * 0.5

    
    def update(self, dt:float) -> None:
        super().update(dt)

        self.time_alive += dt
        if self.time_alive >= self.attack_duration:
            self.kill()
            return

        # Update position near player
        offset_x = self.offset_distance if not self.facing_left else -self.offset_distance
        self.rect.center = (
            self.player.rect.centerx + offset_x,
            self.player.rect.centery
        )


    def on_hit_enemy(self, enemy: object) -> bool:
        if enemy in self.recent_hits:
            return False

        self.recent_hits.add(enemy)
        return True