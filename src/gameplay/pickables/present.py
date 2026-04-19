import pygame
from src.core import Flash, Animation, dmgIndicator, build_random_pitch_sounds
from src.gameplay.pickables import Pickable
import random

class Present(pygame.sprite.Sprite):
    _hurt_sounds: list[pygame.mixer.Sound] = None
    
    def __init__(self, pos: pygame.Vector2, drop_image:pygame.Surface, drop_eff: str, pickables:pygame.sprite.Group, player: object):
        super().__init__()
        spawn_sheet = pygame.image.load('src/assets/items/pickable/item_spawn_animation_sheet.png').convert_alpha()
        self.present_image = pygame.image.load("src/assets/items/pickable/present.png").convert_alpha()
        self.spawn_animation = Animation(spawn_sheet, 64, 64, 0, 3, 0.1)
        self.current_animation = self.spawn_animation
        self.image = self.current_animation.get_current_frame()
        self.rect = self.image.get_rect(center=(int(pos.x), int(pos.y)))
        self.position = pygame.Vector2(pos)
        self.health = 5
        self.drop_image = drop_image
        self.drop_effect = drop_eff
        self.hit_flash = Flash(duration=0.1, color=(255, 255, 255), max_alpha=128)
        self.spawned_pickable = False
        self.spawning = True
        self.spawn_timer = 0.0
        self.spawn_duration = 0.3
        self.pickables = pickables
        self.player = player
        self.damage_indicator = dmgIndicator(font_size=24, lifetime=0.65)

        if Present._hurt_sounds is None:
            Present._pickup_sounds = build_random_pitch_sounds("src/assets/sounds/game/hurt.wav", volume=0.22)

        self.hurt_sound = Present._pickup_sounds
    
    def take_damage(self, weapon: object) -> None:
        if self.spawning:
            return

        if getattr(weapon, "should_destroy_on_hit", True):
            weapon.kill()
        if hasattr(weapon, "on_hit_enemy"):
            if weapon.on_hit_enemy(self) is False:
                return

        self.health -= 1
        random.choice(self.hurt_sound).play()
        self.hit_flash.start()
        popup_pos = pygame.Vector2(self.position.x, self.position.y - 16)
        self.damage_indicator.add(1, popup_pos)
        if self.health <= 0:
            if self.spawned_pickable == False:
                self.spawn_pickable()
                self.kill()
                self.spawned_pickable = True
    

    def spawn_pickable(self):
        pickable = Pickable(self.drop_image, self.position, self.drop_effect, self.player)
        self.pickables.add(pickable)


    def update(self,dt:float, weapon_projectiles: pygame.sprite.Group):
        if self.spawning:
            self.spawn_timer += dt
            self.current_animation.update(dt)
            self.image = self.current_animation.get_current_frame()
            self.rect = self.image.get_rect(center=(int(self.position.x), int(self.position.y)))
            if self.spawn_timer >= self.spawn_duration:
                self.spawning = False
                self.image = self.present_image
                self.rect = self.image.get_rect(center=(int(self.position.x), int(self.position.y)))
            return

        weapon_hits = pygame.sprite.spritecollide(self, weapon_projectiles, False)
        for weapon in weapon_hits:
            self.take_damage(weapon)
        
        self.hit_flash.update(dt)
        self.damage_indicator.update(dt)


    def draw(self, surface:pygame.Surface, camera:object) -> None:
        screen_rect = camera.apply(self.rect)
        if self.spawning:
            img = self.image
        else:
            img = self.hit_flash.apply(self.image)
        surface.blit(img, screen_rect)
        self.damage_indicator.draw(surface, camera)



def _can_spawn_present(x: int, y: int, width: int, height: int, present: pygame.sprite.Group,
                       player: object, collision_rects: list) -> bool:
    probe = pygame.Rect(0, 0, width, height)
    probe.center = (x, y)

    if any(probe.colliderect(rect) for rect in collision_rects):
        return False

    min_present_spacing = max(width, height)
    min_present_spacing_sq = min_present_spacing * min_present_spacing
    for existing in present:
        if (existing.position.x - x) ** 2 + (existing.position.y - y) ** 2 < min_present_spacing_sq:
            return False

    min_player_spacing = int(max(width, height) * 1.5)
    if (player.position.x - x) ** 2 + (player.position.y - y) ** 2 < min_player_spacing * min_player_spacing:
        return False

    return True


def spawn_random_presents(count: int, present:pygame.sprite.Group, pickables:pygame.sprite.Group,
                          width:int, heihgt:int, pickable_types: list, player:object,
                          collision_rects: list):
    """
    Spawns random presents in the world.
    - pickable_types must be a LIST like: [("bomb", bomb_img), ("prismat", prismat_img), ...]
    """
    sample_img = pygame.image.load("src/assets/items/pickable/present.png").convert_alpha()
    half_w = max(16, sample_img.get_width() // 2)
    half_h = max(16, sample_img.get_height() // 2)

    for i in range(count):
        spawn_pos = None

        for _ in range(40):
            x = random.randint(half_w, max(half_w, width - half_w))
            y = random.randint(half_h, max(half_h, heihgt - half_h))
            if _can_spawn_present(x, y, sample_img.get_width(), sample_img.get_height(), present, player, collision_rects):
                spawn_pos = pygame.Vector2(x, y)
                break

        if spawn_pos is None:
            continue

        effect, effect_image = random.choice(pickable_types)
        p = Present(spawn_pos, effect_image, effect, pickables, player)
        present.add(p)
