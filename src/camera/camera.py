import pygame

class Camera:
    def __init__(self, height: int, width: int, world:object) -> None:
        self.offset = pygame.Vector2(0,0)
        self.height = height
        self.width = width
        self.lerp_speed = 0.1
        self.world = world


    def follow(self, target: pygame.sprite.Sprite) -> None:
        
        target_center = pygame.Vector2(target.rect.center)
        desired_offset = pygame.Vector2(
            target_center.x - self.width // 2,
            target_center.y - self.height // 2
        )
        self.offset += (desired_offset - self.offset) * self.lerp_speed
        self.offset = self.world.clamp_camera(
            self.offset, 
            self.width,
            self.height
        )


    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        return rect.move(-self.offset.x, -self.offset.y)