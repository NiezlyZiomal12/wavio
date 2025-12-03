import pygame
from src.utils import Flash
from src.pickables import Pickable
import random

class Present(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, pos: pygame.Vector2, drop_image:pygame.Surface, drop_eff: str, pickables:pygame.sprite.Group):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(int(pos.x), int(pos.y)))
        self.position = pygame.Vector2(pos)
        self.health = 5
        self.drop_image = drop_image
        self.drop_effect = drop_eff
        self.hit_flash = Flash(duration=0.1, color=(255, 255, 255), max_alpha=128)
        self.spawned_pickable = False
        self.pickables = pickables

    
    def take_damage(self, weapon: object) -> None:
        if getattr(weapon, "should_destroy_on_hit", True):
            weapon.kill()
        if hasattr(weapon, "on_hit_enemy"):
            if weapon.on_hit_enemy(self) is False:
                return

        self.health -= 1
        self.hit_flash.start()
        if self.health <= 0:
            if self.spawned_pickable == False:
                self.spawn_pickable()
                self.kill()
                self.spawned_pickable = True
    

    def spawn_pickable(self):
        pickable = Pickable(self.drop_image, self.position, self.drop_effect)
        self.pickables.add(pickable)
    

    def update(self,dt:float, weapon_projectiles: pygame.sprite.Group):
        weapon_hits = pygame.sprite.spritecollide(self, weapon_projectiles, False)
        for weapon in weapon_hits:
            self.take_damage(weapon)
        
        self.hit_flash.update(dt)


    def draw(self, surface:pygame.Surface, camera:object) -> None:
        screen_rect = camera.apply(self.rect)
        img = self.hit_flash.apply(self.image)
        surface.blit(img, screen_rect)



def spawn_random_presents(count: int, present:pygame.sprite.Group, pickables:pygame.sprite.Group, width:int, heihgt:int, present_image: pygame.Surface, pickable_types: list):
    """
    Spawns random presents in the world.
    - pickable_types must be a LIST like: [("bomb", bomb_img), ("prismat", prismat_img), ...]
    """
    for i in range(count):
        x = random.randint(0, width)
        y = random.randint(0, heihgt)
        pos = pygame.Vector2(x,y)
        effect, effect_image = random.choice(pickable_types)

        p = Present(present_image, pos, effect_image, effect, pickables)
        present.add(p)
