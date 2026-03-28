import pygame
from src.core import Animation

class Coin(pygame.sprite.Sprite):
    def __init__(self, sprite_sheet: pygame.sprite.Sprite, x:int, y:int, amount: int, player: object):
        super().__init__()
        self.player = player
        self.gold_amount = amount * self.player.coin_gain
        self.animation = Animation(
            sprite_sheet, 32,32, 0, 15, 0.08
        )
        self.image = self.animation.get_current_frame()
        self.rect = self.image.get_rect(center=(x,y))

        self.position = pygame.Vector2(x,y)
        self.velocity = pygame.Vector2(0,0)
        self.speed = 100
        self.collect_radius = 100 + 100 * self.player.pickup_range
        self.collected = False


    def update_animation(self, dt:float) -> None:
        self.animation.update(dt)
        self.image = self.animation.get_current_frame()


    def update(self, dt: float, player: object) -> None:
        if self.collected:
            return
        
        self.update_animation(dt)

        if self.player.prismat_active:
            distance_to_player = self.position.distance_to(player.position)
            direction = (self.player.position - self.position)
            if direction.length() != 0:
                direction = direction.normalize()
            self.velocity = direction * (self.speed * 5)
        else:
            distance_to_player = self.position.distance_to(player.position)

            if distance_to_player < self.collect_radius:
                direction = player.position - self.position
                if direction.length() != 0:
                    direction = direction.normalize()
                self.velocity = direction * self.speed
                
                speed_multiplier = 1 + (1 - distance_to_player / self.collect_radius) * 2
                self.velocity *= speed_multiplier
            else:
                self.velocity = pygame.Vector2(0, 0)
            
        self.position += self.velocity * dt
        self.rect.center = (int(self.position.x), int(self.position.y))
        
        if distance_to_player < 15:
            self.collected = True
            player.gold += self.gold_amount
            self.kill()

        
    def draw(self, surface: pygame.Surface, camera: object) -> None:
        draw_rect = self.rect.copy()
        draw_rect.center = camera.apply(self.rect).center
        surface.blit(self.image, draw_rect)

