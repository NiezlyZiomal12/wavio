import pygame
from ..utils.Animation import Animation
from config import SLIME_SPEED, SPAWN_ANIMATION_DURATION, SLIME_DMG

class Slime(pygame.sprite.Sprite):
    def __init__(self, spriteSheet:pygame.Surface, start_x:int, start_y:int, spawnSheet:pygame.Surface) -> None:
        super().__init__()
        self.speed = SLIME_SPEED
        self.position = pygame.math.Vector2(start_x, start_y)
        self.sprite_width = 32
        self.sprite_height = 25

        #Animations
        self.idle_animation = Animation(spriteSheet, self.sprite_width, self.sprite_height , 0, 8 , 0.05)
        self.spawn_animation = Animation(spawnSheet, 32,32,0,3,0.1)
        self.current_animation = self.spawn_animation
        self.image = self.current_animation.get_current_frame()
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.facing_left = False
        self.spawning = True
        self.spawn_timer = 0.0
        self.spawn_duration = SPAWN_ANIMATION_DURATION



    def move(self, player_pos: pygame.math.Vector2, other_enemies: list) -> None:
        direction = player_pos - self.position
        if direction.length() > 1:
            direction = direction.normalize() * self.speed
            new_position = self.position + direction
            new_rect = self.rect.copy()
            new_rect.center = (int(new_position.x), int(new_position.y))

            can_move = True
            for enemy in other_enemies:
                if enemy != self:
                    overlap_rect = new_rect.clip(enemy.rect)
                    if overlap_rect.width > self.sprite_width // 2 and overlap_rect.height > self.sprite_height // 2:
                        can_move = False
                        break

            if can_move:
                self.position = new_position
                self.facing_left = direction.x > 0
                self.rect.center = (int(self.position.x), int(self.position.y))



    def update_animation(self, dt: float) -> None:
        self.current_animation.update(dt)
        self.image = self.current_animation.get_current_frame(flip_x=self.facing_left)        
        if self.spawning:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_duration:
                self.spawning = False
                self.current_animation = self.idle_animation



    def update(self, dt: float, player: object, other_enemies: list) -> None:
        if not self.spawning:
            self.move(player.position, other_enemies)
        self.update_animation(dt)

        if self.rect.colliderect(player.rect):
            player.take_damage(SLIME_DMG, self.position)


    def draw(self, surface:pygame.Surface, camera: object):
        surface.blit(self.image, camera.apply(self.rect))