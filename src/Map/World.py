import pygame

class World:
    def __init__(self, width: int, height : int):
        self.width = width
        self.height = height

    def clamp_pos(self, vector : pygame.Vector2) -> pygame.Vector2:
        vector.x = max(0, min(vector.x, self.width))
        vector.y = max(0, min(vector.y, self.height))
        return vector
    
    def clamp_camera(self, offset: pygame.Vector2, screen_w : int, screen_h : int) -> pygame.Vector2:
        offset.x = max(0, min(offset.x, self.width - screen_w))
        offset.y = max(0, min(offset.y, self.height - screen_h))
        return offset