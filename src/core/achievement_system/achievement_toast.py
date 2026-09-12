import pygame
from collections import deque

from config import FONT


class AchievementToastUi:

    def __init__(
        self,
        window: pygame.Surface,
        display_duration: float = 3.5,
        fade_duration: float = 0.6,
    ) -> None:
        self.window = window
        self.display_duration = display_duration
        self.fade_duration = fade_duration
        self.queue: deque[dict] = deque()
        self.current: dict | None = None
        self.timer = 0.0

        self.title_font = pygame.font.Font(FONT, 20)
        self.body_font = pygame.font.Font(FONT, 16)

    def push(self, achievement: dict) -> None:
        self.queue.append(achievement)

    def update(self, dt: float) -> None:
        if self.current is None:
            if self.queue:
                self.current = self.queue.popleft()
                self.timer = 0.0
            return

        self.timer += dt
        total = self.display_duration + self.fade_duration
        if self.timer >= total:
            self.current = None

    def draw(self) -> None:
        if self.current is None:
            return

        width, height = 320, 70
        win_w, _ = self.window.get_size()
        x = win_w - width - 20
        y = 20

        # Slide-in for the first fraction of a second, fade-out at the end.
        slide_duration = 0.25
        total = self.display_duration + self.fade_duration
        if self.timer < slide_duration:
            progress = self.timer / slide_duration
            x += int((1 - progress) * (width + 40))
            alpha = 255
        elif self.timer > self.display_duration:
            fade_progress = (self.timer - self.display_duration) / self.fade_duration
            alpha = max(0, int(255 * (1 - fade_progress)))
        else:
            alpha = 255

        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        panel.fill((20, 20, 20, min(220, alpha)))
        pygame.draw.rect(panel, (255, 215, 0, alpha), panel.get_rect(), 2)

        header = self.title_font.render("Achievement Unlocked", True, (255, 215, 0))
        header.set_alpha(alpha)
        name = self.body_font.render(self.current.get("name", ""), True, (255, 255, 255))
        name.set_alpha(alpha)

        panel.blit(header, (10, 8))
        panel.blit(name, (10, 34))

        self.window.blit(panel, (x, y))