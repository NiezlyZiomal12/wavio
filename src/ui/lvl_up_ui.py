import pygame
import time
from src.utils import Animation, Button, wrap_text
from src.upgrades import loadUpgrades
import random

class LevelUpUi:
    def __init__(self, window, width, height, player):
        self.window = window
        self.width = width
        self.height = height

        self.player = player
        self.upgrades = loadUpgrades()
        self.active = False
        self.font = pygame.font.Font(None , 24)
        self.roll_cost = 15
        self.roll_amount = 1

        #popup animation
        self.animation_time = 0.2
        self.animation_start = 0
        self.scale = 0

        self.options = []
        self.option_levels = {}
        self.selected = None

        self.popup_rect = pygame.Rect(width // 2 - 200, height // 2 - 150, 400, 300)
        self.popupSprite = Animation(pygame.image.load("src/assets/ui/lvlUpUi.png").convert_alpha(), 400,300,0, 2, 0.2)
        self.image = self.popupSprite.get_current_frame()

        self.close_button_rect = pygame.Rect(self.popup_rect.right - 40, self.popup_rect.top + 10, 30, 30)
        self.close_button = Button(self.close_button_rect, "X", self.font, lambda _button: self.hide(), None,(194, 36, 21), (194, 36, 21), (255,255,255), (194, 36, 21), 2, 8)
        
        self.reroll_button_rect = pygame.Rect(self.popup_rect.centerx - 60, self.popup_rect.bottom - 40, 120, 30)
        self.reroll_button = Button(rect=self.reroll_button_rect, text="Reroll", font=self.font, on_click=lambda _button: self.reroll_items(), bg_color=(70, 70, 70), hover_color=(95, 95, 95), text_color=(255, 255, 255), border_color=(200, 200, 200), border_width=2, border_radius=6)

        self.option_rects = [
            pygame.Rect(self.popup_rect.x + 40, self.popup_rect.y + 60, 320, 50),
            pygame.Rect(self.popup_rect.x + 40, self.popup_rect.y + 130, 320, 50),
            pygame.Rect(self.popup_rect.x + 40, self.popup_rect.y + 200, 320, 50)
        ]

    
    def show(self) -> None:
        self.active = True
        self.selected = None
        self.options = self._show_upgrades()

        self.option_levels = {
            upgrade.name: self.player.upgrade_levels.get(upgrade.name, 0)
            for upgrade in self.options
            }
        self.animation_start = time.time()
        self.scale = 0.5


    def _show_upgrades(self):
        available_upgrades = [upgrade for upgrade in self.upgrades if not upgrade.is_maxed(self.player)]
        if available_upgrades:
                upgrades = random.sample(available_upgrades, min(3, len(available_upgrades)))
        return upgrades


    def hide(self):
        self.active = False
        self.roll_amount = 1


    def _current_roll_cost(self) -> int:
        return self.roll_cost + 5 * self.roll_amount


    def reroll_items(self) -> None:
        roll_cost = self._current_roll_cost()
        if self.player.gold >= roll_cost:
            self.player.spend_gold(roll_cost)
            self.show()
            self.roll_amount += 1


    def handle_event(self, event: pygame.event.Event) -> int:
        if not self.active:
            return None

        self.reroll_button.handle_event(event)
        self.close_button.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mx,my):
                    self.selected = i
                    self.roll_amount = 1
                    return i

        return None
    

    def update_animation(self, dt:float) -> None:
        self.image = self.popupSprite.get_current_frame()
        self.popupSprite.update(dt)

    
    def update(self, dt:float) -> None:
        self.update_animation(dt)
        self.reroll_button.update()
        self.close_button.update()
    

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

        # ---- draw text + buttons ----
        base_positions = [60, 130, 200]
        self.option_rects = []

        for i, upgrade in enumerate(self.options):
            base_y = base_positions[i]

            rect = pygame.Rect(
                popup_x + int(40 * self.scale),
                popup_y + int(base_y * self.scale),
                int(320 * self.scale),
                int(60 * self.scale)
            )
            self.option_rects.append(rect)

            # Card background
            pygame.draw.rect(self.window, (45, 45, 45), rect, border_radius=6)
            pygame.draw.rect(self.window, (180, 180, 180), rect, 2, border_radius=6)

            #Upgrade image
            icon = pygame.transform.scale(
                upgrade.image,
                (int(40 * self.scale), int(40 * self.scale))
            )
            icon_x = rect.x + int(10 * self.scale)
            icon_y = rect.centery - icon.get_height() // 2
            self.window.blit(icon, (icon_x, icon_y))

            #Upgrade Name
            name_surface = self.font.render(upgrade.name + ":", True, (255, 255, 255))
            name_x = icon_x + icon.get_width() + int(10 * self.scale)
            name_y = rect.y + int(10 * self.scale)
            self.window.blit(name_surface, (name_x, name_y))

            # Current upgrade level text
            current_level = self.option_levels.get(upgrade.name, 0)
            level_text = f"{current_level}/{upgrade.max_level}"
            level_surface = self.font.render(level_text, True, (255, 220, 140))
            level_x = rect.right - level_surface.get_width() - int(10 * self.scale)
            level_y = rect.y + int(10 * self.scale)
            self.window.blit(level_surface, (level_x, level_y))

            #Upgrade Description
            desc_lines = wrap_text(
                upgrade.description,
                self.font,
                rect.width - (icon.get_width() + int(25 * self.scale))
            )

            # Draw wrapped description
            line_y = name_y + name_surface.get_height()
            for line in desc_lines:
                desc_surface = self.font.render(line, True, (200, 200, 200))
                self.window.blit(desc_surface, (name_x, line_y))
                line_y += desc_surface.get_height()

        lvl_up_text = self.font.render("Level Up!", True, (255,255,255))
        self.window.blit(lvl_up_text, (self.popup_rect.centerx - lvl_up_text.get_width() // 2, popup_y - 20))
        
        # close button
        self.close_button.draw(self.window)

        # reroll button
        current_roll_cost = self._current_roll_cost()
        self.reroll_button.set_text(f"Reroll ({current_roll_cost}g)")
        self.reroll_button.draw(self.window)

        gold_text = self.font.render(f"Gold: {self.player.gold}", True, (255, 230, 120))
        self.window.blit(gold_text, (popup_x + 20, popup_y + 20))
