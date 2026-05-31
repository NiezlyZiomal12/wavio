import pygame
import math
from .weapon import Weapon
from src.core.utils import build_random_pitch_sounds


class Lightning(Weapon):
    _shoot_sounds: list[pygame.mixer.Sound] = None

    def __init__(self, config, start_pos, target_pos: pygame.Vector2, player: object, chains_remaining: int = None, hit_targets: set = None):
        super().__init__(config, start_pos, player)

        direction = target_pos - start_pos
        if direction.length() > 0:
            self.velocity = direction.normalize() * self.speed
            self.facing_left = direction.x > 0
        else:
            self.velocity = pygame.Vector2(0, 0)
            self.facing_left = False

        self.time_alive = 0.0
        self.lifetime = config['special']['lifetime']

        # chaining
        self.chain_amount = config['special']['chain_amount']
        self.chain_range = config['special']['chain_range']
        if chains_remaining is None:
            self.chains_remaining = self.chain_amount
        else:
            self.chains_remaining = chains_remaining

        if hit_targets is None:
            self.hit_targets = set()
        else:
            self.hit_targets = set(hit_targets)

        Lightning._shoot_sounds = build_random_pitch_sounds("src/assets/sounds/game/weapons/lightning.wav")
        self.shoot_sound = Lightning._shoot_sounds

    def update(self, dt: float):
        super().update(dt)
        self.position += self.velocity * dt
        self.rect.center = (int(self.position.x), int(self.position.y))

        self.time_alive += dt
        if self.time_alive >= self.lifetime:
            self.kill()

    def on_hit_enemy(self, enemy: object) -> bool:
        # prevent hitting same enemy twice
        if enemy in self.hit_targets:
            return False
        # mark hit
        self.hit_targets.add(enemy)

        # spawn chain to next nearest valid enemy
        if self.chains_remaining > 0:
            candidates = getattr(self.player, '_last_shoot_targets', [])
            best = None
            best_dist = None
            for cand in candidates:
                if cand is enemy or getattr(cand, 'dead', False) or getattr(cand, 'spawning', False):
                    continue
                if cand in self.hit_targets:
                    continue
                dist = (cand.position - enemy.position).length()
                if dist <= self.chain_range:
                    if best is None or dist < best_dist:
                        best = cand
                        best_dist = dist

            if best is not None:
                # create new lightning projectile from this enemy towards best
                new_proj = Lightning(
                    self.config,
                    pygame.Vector2(enemy.position),
                    pygame.Vector2(best.position),
                    self.player,
                    chains_remaining=self.chains_remaining - 1,
                    hit_targets=self.hit_targets,
                )
                # keep same damage scaling
                new_proj.damage = self.damage
                self.player.active_projectiles.add(new_proj)

        return True
