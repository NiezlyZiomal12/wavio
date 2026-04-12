import pygame
from .weapon import Weapon


class Typhoon(Weapon):
    def __init__(self, config, start_pos, target_pos: pygame.Vector2, player):
        super().__init__(config, start_pos, player)

        self.attack_duration = config["special"]["attack_duration"]
        self.hit_cooldown = config["special"]["hit_cooldown"]

        self.time_alive = 0.0
        self.recent_hits = {}
        self.should_destroy_on_hit = False

        self.image = self.animation.get_current_frame()
        self.image.set_alpha(128)
        self.rect = self.image.get_rect(center=player.rect.center)
        self.position = pygame.Vector2(player.rect.center)

    def update(self, dt: float) -> None:
        self.image = self.animation.get_current_frame()
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

        self.position = pygame.Vector2(self.player.rect.center)
        self.rect = self.image.get_rect(center=(int(self.position.x), int(self.position.y)))

    def on_hit_enemy(self, enemy: object) -> bool:
        if enemy in self.recent_hits:
            return False

        self.recent_hits[enemy] = self.hit_cooldown
        return True

    def draw(self, surface: pygame.Surface, camera: object):
        surface.blit(self.image, camera.apply(self.rect))
