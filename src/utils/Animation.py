import pygame
from typing import List


class Animation:
    def __init__(self, spritesheet: pygame.Surface, frame_width: int, frame_height: int, row: int, frame_count: int, speed: float):
        self.frames: List[pygame.Surface] = self.load_frames(spritesheet, frame_width, frame_height, row, frame_count)
        self.frame_index: int = 0
        self.timer: float = 0.0
        self.speed: float = speed

    def load_frames(self, spritesheet: pygame.Surface, frame_width: int, frame_height: int, row: int, count: int) -> List[pygame.Surface]:
        frames = []
        for col in range(count):
            frame = spritesheet.subsurface(
                pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
            )
            frames.append(frame)
        return frames

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.timer >= self.speed:
            self.timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def get_current_frame(self, flip_x: bool = False) -> pygame.Surface:
        frame = self.frames[self.frame_index]
        if flip_x:
            return pygame.transform.flip(frame, True, False)
        return self.frames[self.frame_index]

    def reset(self) -> None:
        self.frame_index = 0
        self.timer = 0.0
