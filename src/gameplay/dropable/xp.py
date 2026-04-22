import pygame
import random
from src.core import build_random_pitch_sounds

class Xp(pygame.sprite.Sprite):
    _pickup_sounds: list[pygame.mixer.Sound] | None = None

    def __init__(self, image: pygame.Surface, x:int, y:int, amount: int, player: object):
        super().__init__()
        self.player = player
        self.xp_amount = max(1, int(round(amount * self.player.xp_gain)))
        self.image = image
        self.rect = self.image.get_rect(center=(x,y))

        if Xp._pickup_sounds is None:
            Xp._pickup_sounds = build_random_pitch_sounds("src/assets/sounds/game/pickupCoin.wav", volume=0.10)

        self.pickup_sounds = Xp._pickup_sounds

        self.position = pygame.Vector2(x,y)
        self.velocity = pygame.Vector2(0,0)
        self.speed = 150
        self.collect_radius = 150 + 100 * self.player.pickup_range
        self.collected = False


    def update(self, dt: float, player: object) -> None:
        if self.collected:
            return
        
        if self.player.prismat_active:
            distance_to_player = self.position.distance_to(player.position)
            direction = (self.player.position - self.position)
            if direction.length != 0:
                direction = direction.normalize()
            self.velocity = direction * (self.speed * 5)
        else:
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
            random.choice(self.pickup_sounds).play()
            self.collected = True
            player.xp += self.xp_amount
            self.kill()

        
    def draw(self, surface: pygame.Surface, camera: object) -> None:
        draw_rect = self.rect.copy()
        draw_rect.center = camera.apply(self.rect).center
        surface.blit(self.image, draw_rect)

