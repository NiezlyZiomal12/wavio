import pygame

class Pickable(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, pos : pygame.Vector2, effect, player:object):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(int(pos.x), int(pos.y)))
        self.position = pygame.Vector2(pos)
        self.effect = effect
        self.velocity = pygame.Vector2(0,0)
        self.speed = 100
        self.player = player
        self.collect_radius = 100
        self.collected = False


    def apply_effect(self):
        if self.effect == "bomb":
            self.player.pending_effect = "bomb"
        elif self.effect == "prismat":
            self.prismat_effect()
        elif self.effect == "stinky_fish":
            self.stinky_fish_effect()


    def prismat_effect(self):
        self.player.prismat_active = True


    def stinky_fish_effect(self):
        self.player.current_health = min(self.player.current_health + 25, self.player.max_health)


    def update(self, dt:float, player: object) -> None:
        if self.collected:
            return
        
        distance_to_player = self.position.distance_to(player.position)

        if distance_to_player < self.collect_radius:
            direction = (player.position - self.position).normalize()
            self.velocity = direction * self.speed
            
            speed_multiplier = 1 + (1 - distance_to_player / self.collect_radius) * 2
            self.velocity *= speed_multiplier
        else:
            self.velocity = pygame.Vector2(0, 0)
        
        self.position += self.velocity * dt
        self.rect.center = (int(self.position.x), int(self.position.y))
        
        if distance_to_player < 15:
            self.collected = True
            self.apply_effect()
            self.kill()


    def draw(self, surface:pygame.Surface, camera:object) -> None:
        screen_rect = camera.apply(self.rect)
        surface.blit(self.image, screen_rect)


def trigger_bomb(spawner:object, camera:object):
        BOMB_DAMAGE = 50

        for enemy in spawner.enemies:
            enemy.take_damage(BOMB_DAMAGE, None)

        camera.flash_timer = 0.2

        camera.shake_timer = 0.4
        camera.shake_strength = 8