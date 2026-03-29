import pygame
from ..enemy import Enemy
from ..attacks.bullet import Bullet


class Golem(Enemy):
    def __init__(self, sprite_sheet: pygame.Surface, x: int, y: int, spawn_sheet: pygame.Surface, config: dict, player: object):
        super().__init__(sprite_sheet, x, y, spawn_sheet, config, player)

        self.base_damage = self.damage

        self.dash_cooldown = 2.0
        self.dash_duration = 1.0
        self.dash_speed_multiplier = 10.0
        self.dash_damage_multiplier = 1.5
        self.dash_min_range = 100.0
        self.dash_max_range = 500.0

        self.shoot_cooldown = 2.5
        self.shot_speed = 260.0
        self.shot_damage = self.base_damage
        self.shot_lifetime = 2.0
        self.shoot_range = 520
        self.shoot_when_dashing = False

        self._dash_cooldown_timer = self.dash_cooldown
        self._dash_timer = 0.0
        self._is_dashing = False
        self._dash_direction = pygame.Vector2(0, 0)

        self._shoot_timer = self.shoot_cooldown
        self.projectiles = pygame.sprite.Group()


    def _dash(self, player_pos: pygame.Vector2) -> None:
        if self._is_dashing or self._dash_cooldown_timer > 0:
            return

        to_player = player_pos - self.position
        distance = to_player.length()
        if distance <= 0:
            return

        if not (self.dash_min_range <= distance <= self.dash_max_range):
            return

        self._is_dashing = True
        self._dash_timer = self.dash_duration
        self._dash_direction = to_player.normalize()
        self._dash_cooldown_timer = self.dash_cooldown

    def _shoot(self, player_pos: pygame.Vector2) -> None:
        if self._shoot_timer > 0:
            return

        if self._is_dashing and not self.shoot_when_dashing:
            return

        to_player = player_pos - self.position
        if to_player.length() > self.shoot_range or to_player.length_squared() == 0:
            return

        shot = Bullet(
            start_pos=self.position,
            direction=to_player,
            speed=self.shot_speed,
            damage=self.shot_damage,
            lifetime=self.shot_lifetime,
        )
        self.projectiles.add(shot)
        self._shoot_timer = self.shoot_cooldown

    def move(self, player_pos: pygame.Vector2, other_enemies: list, collision_rects: list) -> None:
        if self.dead:
            return

        if self._is_dashing:
            movement = self._dash_direction * self.speed * self.dash_speed_multiplier * 0.5
        else:
            direction = player_pos - self.position
            if direction.length_squared() == 0:
                return
            chase = direction.normalize()
            separation = self._get_separation_force(other_enemies)
            movement = (chase + (separation * 1.0)).normalize() * self.speed * 0.5

        moved = self._move_with_world_collision(movement, collision_rects)
        self.facing_left = movement.x < 0

        if not moved and self._is_dashing:
            self._is_dashing = False
            self._dash_timer = 0.0


    def update(self, dt: float, player: object, other_enemies: list, weapon_projectiles: pygame.sprite.Group, collision_rects: list) -> None:
        self._dash_cooldown_timer = self._dash_cooldown_timer - dt
        self._shoot_timer = self._shoot_timer - dt

        if not self.dead and not self.spawning:
            self._dash(player.position)
            self._shoot(player.position)

        if self._is_dashing:
            self._dash_timer -= dt
            if self._dash_timer <= 0:
                self._is_dashing = False
                self._dash_timer = 0.0

        self.damage = int(self.base_damage * self.dash_damage_multiplier) if self._is_dashing else self.base_damage

        super().update(dt, player, other_enemies, weapon_projectiles, collision_rects)

        self.projectiles.update(dt, collision_rects)
        for shot in pygame.sprite.spritecollide(player, self.projectiles, dokill=True):
            player.take_damage(shot.damage, self.position)

    def draw(self, surface: pygame.Surface, camera: object):
        for shot in self.projectiles:
            surface.blit(shot.image, camera.apply(shot.rect))
        super().draw(surface, camera)