import pygame
import random
import math
from src.core import Animation
from src.gameplay.weapons import WEAPON_CONFIG, Fireball, Boomerang, Sword, Spear, Sun, Meteor
from .weapon_slots import WeaponSlots
from .equippedWeapon import EquippedWeapon

class Player(pygame.sprite.Sprite):
    def __init__(self, spriteSheet:pygame.Surface, start_x:int, start_y:int) -> None:
        super().__init__()
        #Base stats
        self.speed = 5
        self.max_health = 100
        self.current_health = self.max_health
        self.xp_to_lvl_up = 20
        self.xp_gain = 1
        self.coin_gain = 1
        self.damage = 1
        self.projectile_count = 1
        self.luck = 1
        self.armor = 0.0
        self.crit_chance = 0.0
        self.reduce_cooldown = 0.0
        self.pickup_range = 0.0
        self.lifesteal = 0.0

        #mults
        self.hp_mult = 1
        self.armor_mult = 1
        self.cd_mult = 1
        self.dmg_mult = 1
        self.speed_mult = 1
        self.crit_mult = 1


        self.level = 1
        self.xp = 0
        self.position = pygame.math.Vector2(start_x, start_y)
        self.sprite_size = 64
        self.just_leveled_up = False
        self.gold = 200

        #Animations
        self.idle_animation = Animation(spriteSheet, self.sprite_size, self.sprite_size, 0, 2, 0.5)
        self.walk_animation = Animation(spriteSheet, self.sprite_size, self.sprite_size, 3, 8, 0.1)   
        self.hurt_animation = Animation(spriteSheet, self.sprite_size, self.sprite_size, 6, 3, 0.1)     
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

        #Weapons
        self.weapon_slots = WeaponSlots(6)
        self.active_projectiles = pygame.sprite.Group()
        self.equipped_weapons: dict[str, EquippedWeapon] = {}

        #Pickups
        self.prismat_active = False
        self.prismat_radius = 4000
        self.prismat_timer = 3.0
        self.pending_effect = None
        self.starting_weapon_name = None


    def move(self, keys: pygame.key.ScancodeWrapper, collision_rects= None) -> None:
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

        self.movement_with_collisions(movement, collision_rects)


    def movement_with_collisions(self, movement:pygame.Vector2, collision_rects):
        old_pos = self.position.copy()

        # Move X
        self.position.x += movement.x
        self.rect.centerx = int(self.position.x)

        for rect in collision_rects:
            if self.rect.colliderect(rect):
                self.position.x = old_pos.x
                self.rect.centerx = int(old_pos.x)
                break

        # Move Y
        self.position.y += movement.y
        self.rect.centery = int(self.position.y)

        for rect in collision_rects:
            if self.rect.colliderect(rect):
                self.position.y = old_pos.y
                self.rect.centery = int(old_pos.y)
                break


    def take_damage(self, amount:int, enemy_pos: pygame.math.Vector2) -> None:
        #Invisibility frames
        if not self.invicible:
            self.current_health -= (amount - amount * self.armor)
            self.current_health = max(0, self.current_health)
            self.invicible = True
            self.invicibility_timer = 0.0
            self.hurt = True
            self.hurt_animation.reset()
            self.current_animation = self.hurt_animation

            #Knockback
            direction = self.position - enemy_pos
            if direction.length() > 0:
                direction = direction.normalize()
            self.knockback_velocity = direction * 10


    def add_weapon(self, weapon_name: str) -> bool:

        added = self.weapon_slots.add_weapon(
            weapon_name,
            WEAPON_CONFIG[weapon_name],
        )
        if not added:
            return False

        self.equipped_weapons[weapon_name] = EquippedWeapon(
            name=weapon_name,
            weapon_class=eval(weapon_name),
        )

        return True


    @property
    def weapon_levels(self) -> dict[str, int]:
        return {name: weapon.level for name, weapon in self.equipped_weapons.items()}


    def add_gold(self, amount: int) -> None:
        self.gold += amount


    def spend_gold(self, cost: int) -> bool:
        if cost > self.gold:
            return False
        self.gold -= cost
        return True


    def buy_weapon(self, weapon_name: str, price: int = 0) -> tuple[bool, str]:
        if not self.spend_gold(price):
            return False, "not_enough_gold"

        if weapon_name in self.equipped_weapons:
            max_level = WEAPON_CONFIG[weapon_name]["shop"]["max_level"]
            weapon = self.equipped_weapons[weapon_name]
            if not weapon.can_upgrade(max_level):
                self.add_gold(price)
                return False, "max_level"

            weapon.upgrade()
            return True, "upgraded"

        added = self.add_weapon(weapon_name)
        if not added:
            self.add_gold(price)
            return False, "slots_full"
        
        return True, "bought"

    
    def shoot(self, dt:float, enemies: list) -> None:
        if not enemies:
            return
        #loading weapon from config
        for weapon_name in self.weapon_slots.get_weapons():
            weapon_state = self.equipped_weapons.get(weapon_name)
            if weapon_state is None:
                continue

            weapon_state.tick(dt)
            config = WEAPON_CONFIG[weapon_name]
            if weapon_state.ready():
                nearest_enemy = min(enemies, key=lambda e: (e.position - self.position).length())
                weapon_class = weapon_state.weapon_class

                total_projectiles = self.projectile_count
                volley_rotation = random.uniform(0, math.tau)
                projectile = None

                for i in range(total_projectiles):
                    start_pos = self._get_projectile_spawn_pos(i, total_projectiles, volley_rotation)
                    projectile = weapon_class(config, start_pos, nearest_enemy.position, self)
                    self.active_projectiles.add(projectile)

                weapon_state.trigger_cooldown(projectile.cooldown)


    def _get_projectile_spawn_pos(self, index: int, total: int, rotation: float) -> pygame.Vector2:
        """Spawn on a small ring around player to avoid projectile stacking."""
        ring_min = max(8, self.rect.width // 4)
        ring_max = max(ring_min + 4, self.rect.width // 2)

        if total <= 1:
            angle = random.uniform(0, math.tau)
        else:
            angle = rotation + (index / total) * math.tau + random.uniform(-0.12, 0.12)

        radius = random.uniform(ring_min, ring_max)
        return self.position + pygame.Vector2(math.cos(angle), math.sin(angle)) * radius


    def update_weapons(self, dt:float) -> None:
        self.active_projectiles.update(dt)


    def update_animation(self, dt: float) -> None:
        self.current_animation.update(dt)
        self.image = self.current_animation.get_current_frame(flip_x=self.facing_left)


    def update_lvl(self) -> None:
        if self.xp >= self.xp_to_lvl_up:
            self.level += 1
            self.xp = 0
            self.xp_to_lvl_up = int(self.xp_to_lvl_up * 1.2)
            self.just_leveled_up = True


    def update(self,dt:float, keys:pygame.key.ScancodeWrapper, enemies:list, collision_rects):
        self.move(keys, collision_rects)
        self.update_lvl()

        #Weapon update
        if enemies:
            self.shoot(dt, enemies)

        self.update_weapons(dt)

        #Knockback
        if self.knockback_velocity.length() > 0:
            self.movement_with_collisions(self.knockback_velocity, collision_rects)
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

        #Prismat
        if self.prismat_active:
            self.prismat_timer -= dt
            if self.prismat_timer <= 0:
                self.prismat_active = False
                self.prismat_timer = 3.0


    #Ui (might move it to another file)
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


    def draw_coins(self, surface:pygame.Surface) -> None:
        font = pygame.font.Font(None, 24)
        coin_text = font.render(f"Gold: {self.gold}", None, (252, 186, 3))
        surface.blit(coin_text, (10,70))


    def draw(self, surface:pygame.Surface, camera: object):
        for projectile in self.active_projectiles:
            projectile.draw(surface, camera)

        surface.blit(self.image, camera.apply(self.rect))
        self.draw_health_bar(surface)
        self.draw_xp_bar(surface)
        self.draw_coins(surface)
        self.weapon_slots.draw(surface)