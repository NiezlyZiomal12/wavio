import pygame

class Xp(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, x:int, y:int, amount: int, player: object):
        super().__init__()
        self.player = player
        self.xp_amount = amount * self.player.xp_gain
        self.image = image
        self.rect = self.image.get_rect(center=(x,y))

        self.position = pygame.Vector2(x,y)
        self.velocity = pygame.Vector2(0,0)
        self.speed = 100
        self.collect_radius = 100 + 100 * self.player.pickup_range
        self.collected = False


    def update(self, dt: float, player: object) -> None:
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
            player.xp += self.xp_amount
            self.kill()

        
    def draw(self, surface: pygame.Surface, camera: object) -> None:
        draw_rect = self.rect.copy()
        draw_rect.center = camera.apply(self.rect).center
        surface.blit(self.image, draw_rect)

