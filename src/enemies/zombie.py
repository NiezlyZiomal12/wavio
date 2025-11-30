import pygame
from .enemy import Enemy

class Zombie(Enemy):
        def move(self, player_pos: pygame.Vector2, other_enemies: list, collision_rects:list) -> None:
            if self.dead:
                return

            direction = player_pos - self.position
            if direction.length() > 1:
                direction = direction.normalize() * self.speed * 0.5
                new_position = self.position + direction
                new_rect = self.rect.copy()
                new_rect.center = (int(new_position.x), int(new_position.y))

                can_move = True
                for enemy in other_enemies:
                    if enemy != self and not enemy.dead:
                        overlap_rect = new_rect.clip(enemy.rect)
                        if overlap_rect.width > self.sprite_width // 2 and overlap_rect.height > self.sprite_height // 2:
                            can_move = False
                            break
                
                if can_move:
                    for rect in collision_rects:
                        if new_rect.colliderect(rect):
                            can_move = False
                            break

                if can_move:
                    self.position = new_position
                    self.facing_left = direction.x < 0
                    self.rect.center = (int(self.position.x), int(self.position.y))