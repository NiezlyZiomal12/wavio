import pygame
import random


class _DamagePopup:
    def __init__(
        self,
        amount: int,
        world_pos: pygame.Vector2,
        base_surface: pygame.Surface,
        lifetime: float,
        velocity: pygame.Vector2,
    ) -> None:
        self.amount = amount
        self.world_pos = pygame.Vector2(world_pos)
        self.base_surface = base_surface
        self.lifetime = lifetime
        self.age = 0.0
        self.velocity = pygame.Vector2(velocity)

    @property
    def alive(self) -> bool:
        return self.age < self.lifetime

    @property
    def progress(self) -> float:
        if self.lifetime <= 0:
            return 1.0
        return min(1.0, self.age / self.lifetime)


class dmgIndicator:
    def __init__(
        self,
        font_path: str | None = None,
        font_size: int = 22,
        lifetime: float = 0.7,
        rise_speed: float = 78.0,
        drift_speed: float = 24.0,
    ) -> None:
        self.font = pygame.font.Font(font_path, font_size)
        self.lifetime = lifetime
        self.rise_speed = rise_speed
        self.drift_speed = drift_speed
        self.popups: list[_DamagePopup] = []

    def add(self, amount: int | float, world_pos: pygame.Vector2, crit: bool = False) -> None:
        text_color = (255, 95, 95)
        if crit:
            text_color = (255, 220, 90)

        display_amount = max(0, int(round(amount)))
        text = str(display_amount)
        base_surface = self.font.render(text, True, text_color).convert_alpha()

        jitter_x = random.uniform(-10.0, 10.0)
        velocity = pygame.Vector2(jitter_x * 0.3, -self.rise_speed)
        popup = _DamagePopup(
            amount=display_amount,
            world_pos=pygame.Vector2(world_pos.x + jitter_x, world_pos.y),
            base_surface=base_surface,
            lifetime=self.lifetime,
            velocity=velocity,
        )
        self.popups.append(popup)

    def update(self, dt: float) -> None:
        alive_popups: list[_DamagePopup] = []
        for popup in self.popups:
            popup.age += dt
            popup.world_pos += popup.velocity * dt
            popup.velocity.x *= 0.92
            popup.velocity.y -= self.drift_speed * dt

            if popup.alive:
                alive_popups.append(popup)

        self.popups = alive_popups

    def draw(self, surface: pygame.Surface, camera: object) -> None:
        for popup in self.popups:
            p = popup.progress
            alpha = int(255 * (1.0 - p))
            scale = 1.12 - (0.22 * p)

            source_w = popup.base_surface.get_width()
            source_h = popup.base_surface.get_height()
            target_w = max(1, int(source_w * scale))
            target_h = max(1, int(source_h * scale))

            text_surface = pygame.transform.smoothscale(popup.base_surface, (target_w, target_h)).convert_alpha()
            text_surface.set_alpha(alpha)

            world_rect = text_surface.get_rect(center=(int(popup.world_pos.x), int(popup.world_pos.y)))
            screen_rect = camera.apply(world_rect)
            surface.blit(text_surface, screen_rect)