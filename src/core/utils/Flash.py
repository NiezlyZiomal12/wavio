import pygame

class Flash:
    """Class that does flashing on sprite"""
    def __init__(self, duration: float = 0.1, color: tuple = (255, 255, 255), max_alpha: int = 128):
        self.duration = duration
        self.color = color
        self.max_alpha = max_alpha
        self.timer = 0.0
        self.is_active = False
    
    def start(self):
        """Start the flash effect"""
        self.is_active = True
        self.timer = 0.0
    
    def update(self, dt: float):
        """Update the flash timer"""
        if self.is_active:
            self.timer += dt
            if self.timer >= self.duration:
                self.is_active = False
    
    def apply(self, image: pygame.Surface) -> pygame.Surface:
        """Apply flash effect to the image if active"""
        if not self.is_active:
            return image
        
        flash_alpha = int(self.max_alpha * (1 - self.timer / self.duration))

        mask = pygame.mask.from_surface(image, threshold=1)
        flash_surface = mask.to_surface(
            setcolor=(*self.color, flash_alpha),
            unsetcolor=(0, 0, 0, 0),
        )
        
        flashed_image = image.copy()
        flashed_image.blit(flash_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return flashed_image
    
    @property
    def active(self) -> bool:
        return self.is_active