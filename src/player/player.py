import pygame
from config import PLAYER_SPEED, STARTING_HEALTH, SHOOT_COOLDOWN, XP_TO_LVL_UP
from ..utils.Animation import Animation
from ..weapons.fireball import Fireball


class Player(pygame.sprite.Sprite):
    def __init__(self, spriteSheet:pygame.Surface, start_x:int, start_y:int) -> None:
        super().__init__()
        #Base stats
        self.speed = PLAYER_SPEED
        self.max_health = STARTING_HEALTH
        self.current_health = self.max_health
        self.level = 1
        self.xp = 0
        self.xp_to_lvl_up = XP_TO_LVL_UP
        self.position = pygame.math.Vector2(start_x, start_y)
        self.sprite_size = 32

        #Animations
        self.idle_animation = Animation(spriteSheet, self.sprite_size, self.sprite_size, 0, 2, 0.5)
        self.walk_animation = Animation(spriteSheet, self.sprite_size, self.sprite_size, 3, 8, 0.1)   
        self.hurt_animation = Animation(spriteSheet, self.sprite_size, self.sprite_size, 6, 3, 0.2)     
        self.current_animation = self.idle_animation
        self.image = self.current_animation.get_current_frame()
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.facing_left = False

        #Taking dmg properties
        self.invicible = False
        self.invicibility_duriation = 1.0
        self.invicibility_timer = 0.0
        self.hurt = False        
        self.knockback_velocity = pygame.Vector2(0, 0)
        self.knockback_decay = 0.9

        #Shooting
        self.shoot_timer = 0.0
        self.shoot_cooldown = SHOOT_COOLDOWN


    def move(self, keys: pygame.key.ScancodeWrapper) -> None:
        # Create movement vector
        movement = pygame.math.Vector2(0, 0)
        
        if keys[pygame.K_w]: movement.y -= 1
        if keys[pygame.K_s]: movement.y += 1
        if keys[pygame.K_a]:
            movement.x -= 1
            self.facing_left = True
        if keys[pygame.K_d]:
            movement.x += 1
            self.facing_left = False
        
        if movement.length() > 0:
            movement = movement.normalize() * self.speed

            if not self.hurt:
                if self.current_animation != self.walk_animation:
                    self.walk_animation.reset()
                    self.current_animation = self.walk_animation
        else:
            if not self.hurt:
                if self.current_animation != self.idle_animation:
                    self.idle_animation.reset()
                    self.current_animation = self.idle_animation

        self.position += movement
        self.rect.center = (int(self.position.x), int(self.position.y))


    def take_damage(self, amount:int, enemy_pos: pygame.math.Vector2) -> None:
        if not self.invicible:
            self.current_health -= amount
            self.current_health = max(0, self.current_health)
            self.invicible = True
            self.invicibility_timer = 0.0
            self.hurt = True
            self.hurt_animation.reset()
            self.current_animation = self.hurt_animation

            direction = self.position - enemy_pos
            if direction.length() > 0:
                direction = direction.normalize()
            self.knockback_velocity = direction * 10


    def shoot(self,dt: float, fireball_group: pygame.sprite.Group, spriteSheet: pygame.Surface, enemies: list) -> None:
        self.shoot_timer += dt
        if self.shoot_timer >= self.shoot_cooldown and enemies:
            nearest_enemy = min(enemies, key=lambda e: (e.position -self.position).length())
            fireball = Fireball(spriteSheet, self.position, nearest_enemy.position)
            fireball_group.add(fireball)
            self.shoot_timer = 0.0


    def update_animation(self, dt: float) -> None:
        self.current_animation.update(dt)
        self.image = self.current_animation.get_current_frame(flip_x=self.facing_left)


    def update_lvl(self) -> None:
        if self.xp >= self.xp_to_lvl_up:
            self.level += 1
            self.xp = 0
            self.xp_to_lvl_up = int(self.xp_to_lvl_up * 1.2)


    def update(self,dt:float, keys:pygame.key.ScancodeWrapper):
        self.move(keys)
        self.update_lvl()

        #Knockback
        self.position += self.knockback_velocity
        self.knockback_velocity *= self.knockback_decay

        if self.invicible:
            self.invicibility_timer += dt
            if self.invicibility_timer >= self.invicibility_duriation:
                self.invicible = False
                self.hurt = False
        
        if not self.hurt:
            self.update_animation(dt)
        else:
            self.current_animation.update(dt)
            self.image = self.current_animation.get_current_frame(flip_x=self.facing_left)


    def draw_health_bar(self, surface:pygame.Surface) -> None:
        bar_width = 200
        bar_height = 20
        x, y = 10, 40

        pygame.draw.rect(surface, (50, 50, 50), (x, y, bar_width, bar_height))
        health_ratio = self.current_health / self.max_health
        pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_width * health_ratio, bar_height))
        pygame.draw.rect(surface, (255, 255, 255), (x, y, bar_width, bar_height), 2)

    
    def draw_xp_bar(self, surface:pygame.Surface) -> None:
        bar_width, _ =  pygame.display.get_window_size()
        bar_width -= 80
        bar_height = 10
        x, y = 60, 10

        pygame.draw.rect(surface, (50, 50, 50), (x, y, bar_width, bar_height))
        xp_ratio = self.xp / self.xp_to_lvl_up
        pygame.draw.rect(surface, (0, 200, 255), (x, y, bar_width * xp_ratio, bar_height))
        pygame.draw.rect(surface, (255, 255, 255), (x, y, bar_width, bar_height), 2)

        font = pygame.font.Font(None, 24)
        level_text = font.render(f"Lvl: {self.level}", True, (255,255,255))
        surface.blit(level_text, (10,8) )


    def draw(self, surface:pygame.Surface, camera: object):
        surface.blit(self.image, camera.apply(self.rect))
        self.draw_health_bar(surface)
        self.draw_xp_bar(surface)