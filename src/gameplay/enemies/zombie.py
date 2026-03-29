import pygame
from .enemy import Enemy

class Zombie(Enemy):
        def move(self, player_pos: pygame.Vector2, other_enemies: list, collision_rects:list) -> None:
            if self.dead:
                return

            direction = player_pos - self.position
            if direction.length() > 1:
                chase = direction.normalize()
                separation = self._get_separation_force(other_enemies)
                movement = chase + (separation * 1.2)

                if movement.length_squared() == 0:
                    return

                movement = movement.normalize() * self.speed * 0.5
                self._move_with_world_collision(movement, collision_rects)

                self.facing_left = movement.x < 0