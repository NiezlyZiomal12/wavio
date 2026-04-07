import pygame
from config import FONT

class Timer:
    def __init__(self, duration_seconds: float):
        self.duration = duration_seconds
        self.elapsed = 0.0
        self.hud_font = pygame.font.Font(FONT, 24)

    def update(self, dt: float) -> None:
        self.elapsed += dt

    @property
    def finished(self) -> bool:
        return self.elapsed >= self.duration

    def formatted(self) -> str:
        minutes = int(self.elapsed // 60)
        seconds = int(self.elapsed % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def draw(self, window:pygame.Surface):
        t_text = self.hud_font.render(self.formatted(), True, (255, 255, 255))
        window.blit(t_text, (window.get_width()//2 - 10, 30))