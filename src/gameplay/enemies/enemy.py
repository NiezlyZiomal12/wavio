import pygame
import random
from src.core import Animation, Flash, dmgIndicator, build_random_pitch_sounds
from src.gameplay.dropable import Xp, Coin
from src.gameplay.items.upgrades.item_applier import on_hit

class Enemy(pygame.sprite.Sprite):
    _hurt_sounds: list[pygame.mixer.Sound] = None
    HP_SCALING_PER_MINUTE = 2.0
    DAMAGE_SCALING_PER_MINUTE = 0.2
    SPEED_SCALING_PER_MINUTE = 0.03

    def __init__(self, sprite_sheet:pygame.Surface, x:int, y:int, spawn_sheet:pygame.Surface, config:dict, player:object):
        super().__init__()
        self.config = config
        self.player = player

        #loading props from config
        self.speed = int(config['speed'] * 0.05)
        self.position = pygame.Vector2(x,y)
        self.sprite_width = config["Animation"]["sprite_width"]
        self.sprite_height = config["Animation"]["sprite_height"]
        self.hp = config["hp"]
        self.max_hp = config["hp"]
        self.xp_value = config["Dropable"]["xp"]
        self.coin_value = config["Dropable"]["coin"]
        self.damage = config["damage"]
        self.initial_speed = self.speed
        self.initial_hp = self.max_hp
        self.initial_damage = self.damage
        self.base_speed = self.speed
        self.base_hp = self.max_hp
        self.base_damage = self.damage

        #Animations
        self.spawn_animation = Animation(spawn_sheet, 64, 64, 0, 3, 0.1)
        self.idle_animation = Animation(
            sprite_sheet,
            self.sprite_width,
            self.sprite_height,
            config["Animation"]["idle_row"],
            config["Animation"]["idle_frames"], 
            config["Animation"]["idle_speed"]
        )
        self.dead_animation = Animation(
            sprite_sheet,
            self.sprite_width,
            self.sprite_height,
            config["Animation"]["death_row"],
            config["Animation"]["death_frames"],
            config["Animation"]["death_speed"]
        )
        self.hit_flash = Flash(duration=0.1, color=(255, 255, 255), max_alpha=128)
        self.current_animation = self.spawn_animation
        self.image = self.current_animation.get_current_frame()
        self.rect = self.image.get_rect(center=(x, y))

        # State
        self.facing_left = False
        self.spawning = True
        self.spawn_timer = 0.0
        self.spawn_duration = config["Animation"]["spawn_duration"]
        self.dead = False
        self.death_timer = 0.0
        self.dead_duration = config["Animation"]["dead_duration"]
        self.killed = False
        # External references
        self.xp_sprite = None
        self.xp_group = None
        self.coin_sprite = None
        self.coin_group = None
        self.damage_indicator = dmgIndicator(font_size=24, lifetime=0.65)

        if Enemy._hurt_sounds is None:
            Enemy._pickup_sounds = build_random_pitch_sounds("src/assets/sounds/game/hurt.wav", volume=0.22)

        self.hurt_sound = Enemy._pickup_sounds


    def apply_time_scaling(
        self,
        elapsed_time: float,
        hp_multiplier: float,
        damage_multiplier: float,
        speed_multiplier: float,
    ) -> None:
        """Scale enemy HP, damage, and speed based on elapsed game time."""
        minutes = max(0.0, elapsed_time) / 60.0
        time_hp_multiplier = 1.0 + (minutes * self.HP_SCALING_PER_MINUTE)
        time_damage_multiplier = 1.0 + (minutes * self.DAMAGE_SCALING_PER_MINUTE)
        time_speed_multiplier = 1.0 + (minutes * self.SPEED_SCALING_PER_MINUTE)

        scaled_max_hp = max(1, int(round(self.initial_hp * time_hp_multiplier * max(0.1, hp_multiplier))))
        hp_ratio = self.hp / self.max_hp if self.max_hp > 0 else 1.0
        scaled_damage = max(1, int(round(self.initial_damage * time_damage_multiplier * max(0.1, damage_multiplier))))
        scaled_speed = max(1, int(round(self.initial_speed * time_speed_multiplier * max(0.1, speed_multiplier))))

        self.max_hp = scaled_max_hp
        self.hp = max(1, int(round(self.max_hp * hp_ratio)))
        self.base_speed = scaled_speed
        self.speed = scaled_speed
        self.base_hp = self.max_hp
        self.base_damage = scaled_damage
        self.damage = scaled_damage

        # Keep boss-specific combat logic in sync with scaled base damage.
        if hasattr(self, "shot_damage"):
            self.shot_damage = self.damage


    def _get_separation_force(self, other_enemies: list) -> pygame.Vector2:
        """Push enemies apart softly instead of hard-stopping movement."""
        force = pygame.Vector2()
        personal_space = max(self.sprite_width, self.sprite_height) * 0.8

        for enemy in other_enemies:
            if enemy == self or enemy.dead:
                continue

            offset = self.position - enemy.position
            distance = offset.length()

            if distance <= 0:
                continue

            if distance < personal_space:
                weight = (personal_space - distance) / personal_space
                force += offset.normalize() * weight

        return force


    def _move_with_world_collision(self, movement: pygame.Vector2, collision_rects: list) -> bool:
        """Move on each axis separately so enemies can slide along obstacles."""
        moved = False

        if movement.x != 0:
            next_pos_x = pygame.Vector2(self.position.x + movement.x, self.position.y)
            next_rect_x = self.rect.copy()
            next_rect_x.center = (int(next_pos_x.x), int(next_pos_x.y))

            blocked_x = any(next_rect_x.colliderect(rect) for rect in collision_rects)
            if not blocked_x:
                self.position.x = next_pos_x.x
                moved = True

        if movement.y != 0:
            next_pos_y = pygame.Vector2(self.position.x, self.position.y + movement.y)
            next_rect_y = self.rect.copy()
            next_rect_y.center = (int(next_pos_y.x), int(next_pos_y.y))

            blocked_y = any(next_rect_y.colliderect(rect) for rect in collision_rects)
            if not blocked_y:
                self.position.y = next_pos_y.y
                moved = True

        self.rect.center = (int(self.position.x), int(self.position.y))
        return moved


    def move(self, player_pos: pygame.Vector2, other_enemies: list, collision_rects: list) -> None:
        """Base movement - can be overridden by subclasses"""
        if self.dead:
            return
        
        # Blend chase direction with separation, so enemies spread naturally.
        direction = player_pos - self.position
        if direction.length() > 1:
            chase = direction.normalize()
            separation = self._get_separation_force(other_enemies)
            movement = chase + (separation * 1.2)

            if movement.length_squared() == 0:
                return

            movement = movement.normalize() * self.speed * 0.5
            self._move_with_world_collision(movement, collision_rects)

            self.facing_left = movement.x > 0


    def take_damage(self, damage: int, weapon: object) -> None:
        if self.spawning or self.dead:
            return
            
        #Check if actual weapon is single hit
        if weapon is not None:
            if getattr(weapon, "should_destroy_on_hit", True):
                weapon.kill()

            #Check if actual projectile is multihit (piercing)
            if hasattr(weapon, "on_hit_enemy"):
                if weapon.on_hit_enemy(self) is False:
                    return

        self.hp -= damage
        random.choice(self.hurt_sound).play()
        self.hit_flash.start()
        popup_pos = pygame.Vector2(self.position.x, self.position.y - (self.sprite_height * 0.45))
        self.damage_indicator.add(damage, popup_pos)
        
        on_hit(self.player, self, damage)
        if self.hp <= 0:
            self.die()


    def die(self) -> None:
        self.dead = True
        self.current_animation = self.dead_animation
        self.death_timer = 0.0

        xp_orb = Xp(self.xp_sprite, int(self.position.x), int(self.position.y), self.xp_value, self.player)
        self.xp_group.add(xp_orb)

        # Coins drop.
        if random.random() < 0.3:
            coin = Coin(self.coin_sprite, int(self.position.x), int(self.position.y), self.coin_value, self.player)
            self.coin_group.add(coin)
            

    def apply_poison(self, stacks: int, damage: float, duration: float, tick_rate: float) -> None:
        if not hasattr(self, "_poison_stacks"):
            self._poison_stacks = 0
            self._poison_damage = 0
            self._poison_timer = 0.0
            self._poison_tick_timer = 0.0
            self._poison_tick_rate = tick_rate

        self._poison_stacks += stacks
        self._poison_damage = damage  # damage per tick per stack
        self._poison_timer = max(self._poison_timer, duration)  # refresh duration
        self._poison_tick_timer = 0.0        


    def _update_poison(self, dt: float) -> None:
        if not hasattr(self, "_poison_stacks") or self._poison_stacks <= 0 or self.dead:
            return

        self._poison_timer -= dt
        if self._poison_timer <= 0:
            self._poison_stacks = 0
            return

        self._poison_tick_timer += dt
        if self._poison_tick_timer >= self._poison_tick_rate:
            self._poison_tick_timer = 0.0
            tick_damage = self._poison_damage * self._poison_stacks
            self.hp -= tick_damage
            random.choice(self.hurt_sound).play()
            popup_pos = pygame.Vector2(self.position.x, self.position.y - (self.sprite_height * 0.45))
            self.damage_indicator.add(int(tick_damage), popup_pos)
            if self.hp <= 0:
                self.die()


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


    def update(self, dt: float, player: object, other_enemies: list, weapon_projectiles: pygame.sprite.Group, collision_rects: list) -> None:
        #taking damage
        if not self.dead:
            weapon_hits = pygame.sprite.spritecollide(self, weapon_projectiles, False)
            for weapon in weapon_hits:
                self.take_damage(weapon.damage, weapon)

        if not self.spawning and not self.dead:
            self.move(player.position, other_enemies, collision_rects)
        
        self.hit_flash.update(dt)
        self.damage_indicator.update(dt)
        self._update_poison(dt)
        self.update_animation(dt)

        #Collision with other enemies
        if self.rect.colliderect(player.rect) and not self.dead and not self.spawning:
            player.take_damage(self.damage, self.position)


    def draw(self, surface: pygame.Surface, camera: object):
        surface.blit(self.image, camera.apply(self.rect))
        self.damage_indicator.draw(surface, camera)