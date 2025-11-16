import pygame
import time
from src.utils import Animation

class LevelUpUi:
    def __init__(self, window, width, height):
        self.window = window
        self.width = width
        self.height = height

        self.active = False
        self.font = pygame.font.Font(None , 24)

        #popup animation
        self.animation_time = 0.2
        self.animation_start = 0
        self.scale = 0

        self.options = ["UPGRADE A" , 'UPGRADE B', 'UPGRADE C']
        self.selected = None

        self.popup_rect = pygame.Rect(width // 2 - 200, height // 2 - 150, 400, 300)
        self.popupSprite = Animation(pygame.image.load("src/assets/ui/lvlUpUi.png").convert_alpha(), 400,300,0, 2, 0.2)
        self.image = self.popupSprite.get_current_frame()

        self.option_rects = [
            pygame.Rect(self.popup_rect.x + 40, self.popup_rect.y + 60, 320, 50),
            pygame.Rect(self.popup_rect.x + 40, self.popup_rect.y + 130, 320, 50),
            pygame.Rect(self.popup_rect.x + 40, self.popup_rect.y + 200, 320, 50)
        ]

    
    def show(self, options: list= None) -> None:
        self.active = True
        self.selected = None
        if options:
            self.options = options
        self.animation_start = time.time()
        self.scale = 0.5


    def hide(self):
        self.active = False


    def handle_event(self, event: pygame.event.Event) -> int:
        if not self.active:
            return None
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mx,my):
                    self.selected = i
                    return i
        return None
    

    def update_animation(self, dt:float) -> None:
        self.image = self.popupSprite.get_current_frame()
        self.popupSprite.update(dt)

    
    def update(self, dt:float) -> None:
        self.update_animation(dt)
    

    def draw(self):
        if not self.active:
            return  

        # darken background
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.window.blit(overlay, (0, 0))   

        # --- scale animation ---
        elapsed = time.time() - self.animation_start
        t = min(elapsed / self.animation_time, 1)
        eased = 1 - (1 - t)**3
        self.scale = 0.5 + (0.5 * eased)    

        # --- ANIMATED POPUP SPRITE ---
        frame = self.popupSprite.get_current_frame()
        frame = pygame.transform.scale(
            frame,
            (
                int(self.popup_rect.width * self.scale),
                int(self.popup_rect.height * self.scale)
            )
        )   

        popup_x = self.popup_rect.centerx - frame.get_width() // 2
        popup_y = self.popup_rect.centery - frame.get_height() // 2 

        # draw animated popup
        self.window.blit(frame, (popup_x, popup_y)) 

        # ---- draw text + buttons over the animated frame ----
        base_positions = [60, 130, 200]
        self.option_rects = []  

        for i, base_y in enumerate(base_positions):
            rect = pygame.Rect(
                popup_x + int(40 * self.scale),
                popup_y + int(base_y * self.scale),
                int(320 * self.scale),
                int(50 * self.scale)
            )
            self.option_rects.append(rect)  

            pygame.draw.rect(self.window, (70, 70, 70), rect)
            pygame.draw.rect(self.window, (200, 200, 200), rect, 2) 

            text = self.font.render(self.options[i], True, (255, 255, 255))
            self.window.blit(
                text,
                (rect.centerx - text.get_width() // 2,
                 rect.centery - text.get_height() // 2)
            )
