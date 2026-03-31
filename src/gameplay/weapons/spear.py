import math
import pygame
from .weapon import Weapon


class Spear(Weapon):
    def __init__(self, config, start_pos, target_pos: pygame.Vector2, player):
        super().__init__(config, start_pos, player)

        self.attack_duration = config["special"]["attack_duration"]
        self.attack_range = config["special"]["attack_range"]
        self.hit_cooldown = config["special"]["hit_cooldown"]

        self.time_alive = 0.0
        self.recent_hits = {}
        self.should_destroy_on_hit = False
        self.hitbox_width = int(config["special"]["hitbox_width"])
        self.hitbox_length = int(config["special"]["hitbox_length"])

        self.direction = target_pos - pygame.Vector2(player.rect.center)
        if self.direction.length_squared() == 0:
            self.direction = pygame.Vector2(1, 0)
        else:
            self.direction = self.direction.normalize()

        self.facing_left = self.direction.x > 0

        # Rotate once towards target and reuse base image for cheap runtime updates.
        base_frame = self.animation.get_current_frame()
        angle = -math.degrees(math.atan2(self.direction.y, self.direction.x))
        self.image = pygame.transform.rotate(base_frame, angle)
        self.draw_rect = self.image.get_rect(center=player.rect.center)
        self.rect = pygame.Rect(0, 0, self.hitbox_width, self.hitbox_width)
        self.position = pygame.Vector2(player.rect.center)
        self.rect.center = (int(self.position.x), int(self.position.y))

    def _tip_position(self, base_position: pygame.Vector2) -> pygame.Vector2:
        return base_position + self.direction * self.hitbox_length

    def _thrust_distance(self, progress: float) -> float:
        # Fast forward stab then retract in second half.
        if progress <= 0.5:
            return self.attack_range * (progress / 0.5)
        return self.attack_range * (1.0 - ((progress - 0.5) / 0.5))

    def update(self, dt: float) -> None:
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

        progress = self.time_alive / self.attack_duration
        offset = self._thrust_distance(progress)

        start_from_player = max(16, self.player.rect.width * 0.3)
        self.position = (
            pygame.Vector2(self.player.rect.center)
            + (self.direction * (start_from_player + offset))
        )

        tip = self._tip_position(self.position)
        self.draw_rect.center = (int(self.position.x), int(self.position.y))
        self.rect.center = (int(tip.x), int(tip.y))

    def on_hit_enemy(self, enemy: object) -> bool:
        if enemy in self.recent_hits:
            return False

        self.recent_hits[enemy] = self.hit_cooldown
        return True

    def draw(self, surface: pygame.Surface, camera: object):
        surface.blit(self.image, camera.apply(self.draw_rect))
