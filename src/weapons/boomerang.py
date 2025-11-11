import pygame
from .weapon import Weapon
import random

class Boomerang(Weapon):
    def __init__(self, config, sprite_sheet, start_pos,target_pos, player):
        super().__init__(config, sprite_sheet, start_pos, player)

        self.start_pos = pygame.Vector2(start_pos)
        self.player = player
        self.pierce_count = config['pierce_count']
        self.return_speed = config['return_speed']
        self.lifetime = config['lifetime']

        offset_strength = 0.05
        direction = target_pos - player.position
        if direction.length() > 0:
            offset = pygame.Vector2(-direction.y, direction.x)
            offset *= random.uniform(-offset_strength, offset_strength) * direction.length()
            direction += offset

            self.velocity = direction.normalize() * self.speed
        else:
            self.velocity = pygame.Vector2(0,0)

        self.returning = False
        self.time_alive = 0.0
        self.facing_left = direction.x > 0
        self.should_destroy_on_hit = False
        self.hit_cooldown = 0.15
        self.recent_hits = {}


    def update(self, dt:float) -> None:
        super().update(dt)

        enemies_to_remove = []
        for enemy, timer in self.recent_hits.items():
            timer -= dt
            if timer <= 0:
                enemies_to_remove.append(enemy)
            else:
                self.recent_hits[enemy] = timer
        for enemy in enemies_to_remove:
            del self.recent_hits[enemy]

        self.time_alive += dt

        if not self.returning and self.time_alive > self.lifetime / 2 :
            self.returning = True

        if self.returning:
            to_player = (pygame.Vector2(self.player.rect.center) - pygame.Vector2(self.rect.center))
            if to_player.length() > 5:
                self.velocity = to_player.normalize() * self.return_speed
            else:
                self.kill()

        self.rect.center += self.velocity * dt

        if self.time_alive >= self.lifetime:
            self.kill()

        
    def on_hit_enemy(self, enemy:object) -> None:
        if enemy in self.recent_hits:
            return
        self.recent_hits[enemy] = self.hit_cooldown
        self.pierce_count -= 1
        if self.pierce_count <= 0:
            self.returning = True