import pygame
from config import WORLD_HEIGHT, WORLD_WIDTH


class Bullet(pygame.sprite.Sprite):
    def __init__(
        self,
        start_pos: pygame.Vector2,
        direction: pygame.Vector2,
        speed: float,
        damage: int,
        lifetime: float,
        size: int = 14,
        color: tuple = (247, 126, 60),
        core_color: tuple = (255, 220, 140),
    ) -> None:
        super().__init__()
        self.position = pygame.Vector2(start_pos)
        if direction.length_squared() > 0:
            self.velocity = direction.normalize() * speed
        else:
            self.velocity = pygame.Vector2(0, 0)

        self.damage = damage
        self.lifetime = lifetime
        self.time_alive = 0.0

        radius = max(2, size // 2)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        pygame.draw.circle(self.image, core_color, (radius, radius), max(1, radius // 2))
        self.rect = self.image.get_rect(center=(int(self.position.x), int(self.position.y)))

    def update(self, dt: float, collision_rects: list) -> None:
        self.position += self.velocity * dt
        self.rect.center = (int(self.position.x), int(self.position.y))

        self.time_alive += dt
        if self.time_alive >= self.lifetime:
            self.kill()
            return

        if not (0 <= self.position.x <= WORLD_WIDTH and 0 <= self.position.y <= WORLD_HEIGHT):
            self.kill()
            return

        for rect in collision_rects:
            if self.rect.colliderect(rect):
                self.kill()
                return

    def draw(self, surface: pygame.Surface, camera: object) -> None:
        surface.blit(self.image, camera.apply(self.rect))