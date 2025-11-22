import pygame
from src.utils import Animation, Flash
from src.xp import Xp

class Enemy(pygame.sprite.Sprite):
    def __init__(self, sprite_sheet:pygame.Surface, x:int, y:int, spawn_sheet:pygame.Surface, config:dict, player:object):
        super().__init__()
        self.config = config
        self.player = player

        #loading props from config
        self.speed = int(config['speed'] * 0.05)
        self.position = pygame.Vector2(x,y)
        self.sprite_width = config.get('sprite_width')
        self.sprite_height = config.get("sprite_height")
        self.hp = config["hp"]
        self.max_hp = config["hp"]
        self.xp_value = config["xp"]
        self.damage = config["damage"]

        #Animations
        self.spawn_animation = Animation(spawn_sheet, 32, 32, 0, 3, 0.1)
        self.idle_animation = Animation(
            sprite_sheet,
            self.sprite_width,
            self.sprite_height,
            config["idle_row"],
            config["idle_frames"], 
            config["idle_speed"]
        )
        self.dead_animation = Animation(
            sprite_sheet,
            self.sprite_width,
            self.sprite_height,
            config["death_row"],
            config["death_frames"],
            config["death_speed"]
        )
        self.hit_flash = Flash(duration=0.1, color=(255, 255, 255), max_alpha=128)
        self.current_animation = self.spawn_animation
        self.image = self.current_animation.get_current_frame()
        self.rect = self.image.get_rect(center=(x, y))

        # State
        self.facing_left = False
        self.spawning = True
        self.spawn_timer = 0.0
        self.spawn_duration = config.get("spawn_duration", 1.0)
        self.dead = False
        self.death_timer = 0.0
        self.dead_duration = config.get("dead_duration", 1.0)
        self.killed = False
        
        # External references
        self.xp_sprite = None
        self.xp_group = None


    def move(self, player_pos: pygame.Vector2, other_enemies: list) -> None:
        """Base movement - can be overridden by subclasses"""
        if self.dead:
            return
        
        #Moving towards player and not overlapping with another enemies
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
                self.position = new_position
                self.facing_left = direction.x > 0
                self.rect.center = (int(self.position.x), int(self.position.y))


    def take_damage(self, damage: int, weapon: object) -> None:
        if self.spawning or self.dead:
            return
            
        #Check if actual weapon is single hit
        if getattr(weapon, "should_destroy_on_hit", True):
            weapon.kill()

        #Check if actual projectile is multihit (piercing)
        if hasattr(weapon, "on_hit_enemy"):
            if weapon.on_hit_enemy(self) is False:
                return

        self.hp -= damage
        self.hit_flash.start()
        
        #lifesteal for player
        heal = damage * self.player.lifesteal
        self.player.current_health = min(self.player.max_health, self.player.current_health + heal)

        if self.hp <= 0:
            self.die()


    def die(self) -> None:
        self.dead = True
        self.current_animation = self.dead_animation
        self.death_timer = 0.0
        xp_orb = Xp(self.xp_sprite, int(self.position.x), int(self.position.y), self.xp_value, self.player)
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


    def update(self, dt: float, player: object, other_enemies: list, weapon_projectiles: pygame.sprite.Group) -> None:
        #taking damage
        if not self.dead:
            weapon_hits = pygame.sprite.spritecollide(self, weapon_projectiles, False)
            for weapon in weapon_hits:
                self.take_damage(weapon.damage, weapon)

        if not self.spawning and not self.dead:
            self.move(player.position, other_enemies)
        
        self.hit_flash.update(dt)
        self.update_animation(dt)

        #Collision with other enemies
        if self.rect.colliderect(player.rect) and not self.dead and not self.spawning:
            player.take_damage(self.damage, self.position)


    def draw(self, surface: pygame.Surface, camera: object):
        surface.blit(self.image, camera.apply(self.rect))