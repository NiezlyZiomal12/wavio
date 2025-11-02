import pygame
from src.utils import Animation, Flash
from src.xp import Xp
from config import ZOMBIE_SPEED, ZOMBIE_DMG, ZOMBIE_HP, ZOMBIE_XP, SPAWN_ANIMATION_DURATION


class Zombie(pygame.sprite.Sprite):
    def __init__(self, spriteSheet:pygame.Surface, start_x:int, start_y:int, spawnSheet:pygame.Surface) -> None:
        super().__init__()
        self.speed = ZOMBIE_SPEED
        self.position = pygame.math.Vector2(start_x, start_y)
        self.sprite_width = 32
        self.sprite_height = 32
        self.hp = ZOMBIE_HP
        self.xp_value = ZOMBIE_XP
        self.xp_sprite = None 
        self.xp_group = None

        #Animations
        self.idle_animation = Animation(spriteSheet, self.sprite_width, self.sprite_height , 1, 8 , 0.2)
        self.spawn_animation = Animation(spawnSheet, 32,32,0,3,0.1)
        self.dead_animation = Animation(spriteSheet,self.sprite_width, self.sprite_height, 4, 6, 0.5)
        self.hit_flash = Flash(duration=0.1, color=(255, 255, 255), max_alpha=128)
        self.current_animation = self.spawn_animation
        self.image = self.current_animation.get_current_frame()
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.facing_left = False
        self.spawning = True
        self.spawn_timer = 0.0
        self.spawn_duration = SPAWN_ANIMATION_DURATION
        self.dead = False
        self.death_timer = 0.0
        self.dead_duration = 1.0
        self.killed = False


    def move(self, player_pos: pygame.math.Vector2, other_enemies: list) -> None:
        if self.dead:
            return
        
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
                self.facing_left = direction.x < 0
                self.rect.center = (int(self.position.x), int(self.position.y))


    def take_damage(self, damage: int, fireball:object) -> None:
        if not self.spawning and not self.dead:
            self.hp -= damage
            fireball.kill()
            self.hit_flash.start()
        if self.hp <= 0:
            self.die()


    def die(self) -> None:
        self.dead = True
        self.current_animation = self.dead_animation
        self.death_timer = 0.0

        xp_orb = Xp(self.xp_sprite, int(self.position.x), int(self.position.y), self.xp_value)
        self.xp_group.add(xp_orb)


    def update_animation(self, dt: float) -> None:
        self.current_animation.update(dt)
        self.image = self.current_animation.get_current_frame(flip_x=self.facing_left)
        self.image = self.hit_flash.apply(self.image)    
        if self.spawning:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_duration:
                self.spawning = False
                self.current_animation = self.idle_animation
        elif self.dead:
            self.death_timer += dt
            if self.death_timer >= self.dead_duration:
                self.killed = True



    def update(self, dt: float, player: object, other_enemies: list, fireball_group:pygame.sprite.Group) -> None:
        if not self.dead:
            fireball_hits = pygame.sprite.spritecollide(self, fireball_group, False)
            for fireball in fireball_hits:
                self.take_damage(5,fireball)

        if not self.spawning and not self.dead:
            self.move(player.position, other_enemies)
        
        self.hit_flash.update(dt)
        self.update_animation(dt)

        if self.rect.colliderect(player.rect) and not self.dead and not self.spawning:
            player.take_damage(ZOMBIE_DMG, self.position)


    def draw(self, surface:pygame.Surface, camera: object):
        surface.blit(self.image, camera.apply(self.rect))