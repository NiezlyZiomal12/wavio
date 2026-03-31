import pygame
import random
import math
from .weapon import Weapon


class Meteor(Weapon):
    def __init__(self, config, sprite_sheet, start_pos, target_pos: pygame.Vector2, player):
        super().__init__(config, sprite_sheet, start_pos, player)

        self.attack_duration = config["special"]["attack_duration"] 
        self.hit_cooldown = config["special"]["hit_cooldown"]
        self.max_spawn_range = config["range"]
        self.scatter_factor = config["special"]["scatter_factor"]
        self.min_scatter = config["special"]["min_scatter"]
        self.max_scatter = config["special"]["max_scatter"]

        if self.max_spawn_range < 0:
            self.max_spawn_range = 0.0

        self.should_destroy_on_hit = False
        self.time_alive = 0.0
        self.recent_hits = {}

        desired_center = pygame.Vector2(target_pos)
        from_player = desired_center - pygame.Vector2(player.position)
        if self.max_spawn_range > 0 and from_player.length() > self.max_spawn_range:
            desired_center = pygame.Vector2(player.position) + from_player.normalize() * self.max_spawn_range

        scatter_radius = self.max_spawn_range * self.scatter_factor
        scatter_radius = max(self.min_scatter, min(scatter_radius, self.max_scatter))
        angle = random.uniform(0.0, math.tau)
        distance = random.uniform(0.0, scatter_radius)
        scatter_offset = pygame.Vector2(math.cos(angle), math.sin(angle)) * distance
        self.position = desired_center + scatter_offset

        self.image = self.animation.get_current_frame()
        self.image.set_alpha(200)
        self.rect = self.image.get_rect(center=(int(self.position.x), int(self.position.y)))

    def update(self, dt: float) -> None:
        self.image = self.animation.get_current_frame()
        self.image.set_alpha(200)
        self.animation.update(dt)

        self.time_alive += dt
        if self.time_alive >= self.attack_duration:
            self.kill()
            return

        expired = []
        for enemy, timer in self.recent_hits.items():
            timer -= dt
            if timer <= 0:
                expired.append(enemy)
            else:
                self.recent_hits[enemy] = timer

        for enemy in expired:
            del self.recent_hits[enemy]

        self.rect = self.image.get_rect(center=(int(self.position.x), int(self.position.y)))

    def on_hit_enemy(self, enemy: object) -> bool:
        if enemy in self.recent_hits:
            return False

        self.recent_hits[enemy] = self.hit_cooldown
        return True

