import pygame
import pygame_gui
from pygame_gui.elements import UIButton
from src.core.utils import Animation, wrap_text, build_random_pitch_sounds
from src.gameplay.items.upgrades import loadUpgrades
import random
from config import FONT, NAME_TEXT_COLOR, LVL_TEXT_COLOR, DESC_TEXT_COLOR

class LevelUpUi:
    def __init__(self, window, width, height, player):
        self.window = window
        self.width = width
        self.height = height
        self.current_size = self.window.get_size()

        self.player = player
        self.upgrades = loadUpgrades()
        self.active = False
        self.font_size = 24
        self.font = pygame.font.Font(FONT, self.font_size)
        self.roll_cost = 15
        self.roll_amount = 1

        self.options = []
        self.option_levels = {}
        self.selected = None

        self.click_sound = pygame.mixer.Sound("src/assets/sounds/gui/click.wav")
        self.power_up_sound = pygame.mixer.Sound("src/assets/sounds/game/power_up.wav")
        self.power_up_sound.set_volume(0.1)
        _roll_sounds = build_random_pitch_sounds("src/assets/sounds/gui/roll.wav", volume=0.10)
        self.roll_sound = _roll_sounds

        self.manager = pygame_gui.UIManager(self.current_size, theme_path="src/assets/pygame_gui_styles/pause_theme.json")
        self.popup_rect = self._compute_popup_rect()
        self.popupSprite = Animation(pygame.image.load("src/assets/ui/lvlUpUi.png").convert_alpha(), 400,300,0, 2, 0.2)
        self.image = self.popupSprite.get_current_frame()

        self.close_button = UIButton(
            relative_rect=pygame.Rect(0, 0, 34, 34),
            text="X",
            manager=self.manager,
            object_id="#closeButton"
        )
        self.reroll_button = UIButton(
            relative_rect=pygame.Rect(0, 0, 150, 38),
            text="Reroll",
            manager=self.manager,
            object_id="#rerollButton"
        )
        self._set_ui_visible(False)
        self._responsive_ui(force=True)

        self.option_rects = [
            pygame.Rect(self.popup_rect.x + 40, self.popup_rect.y + 60, 320, 50),
            pygame.Rect(self.popup_rect.x + 40, self.popup_rect.y + 130, 320, 50),
            pygame.Rect(self.popup_rect.x + 40, self.popup_rect.y + 200, 320, 50)
        ]


    def _set_ui_visible(self, visible: bool) -> None:
        if visible:
            self.close_button.show()
            self.reroll_button.show()
        else:
            self.close_button.hide()
            self.reroll_button.hide()


    def _compute_popup_rect(self) -> pygame.Rect:
        width, height = self.current_size
        margin = max(12, int(min(width, height) * 0.05))
        popup_width = max(340, min(560, width - (2 * margin)))
        popup_height = max(260, min(430, height - (2 * margin)))
        return pygame.Rect((width - popup_width) // 2, (height - popup_height) // 2, popup_width, popup_height)


    def _responsive_ui(self, force: bool = False) -> None:
        new_size = self.window.get_size()
        if not force and new_size == self.current_size:
            return

        self.current_size = new_size
        self.width, self.height = new_size
        self.manager.set_window_resolution(self.current_size)
        self.popup_rect = self._compute_popup_rect()

        self.font_size = max(16, min(28, int(min(self.popup_rect.width, self.popup_rect.height) * 0.07)))
        self.font = pygame.font.Font(FONT, self.font_size)

        close_size = max(28, min(40, int(self.popup_rect.width * 0.08)))
        self.close_button.set_dimensions((close_size, close_size))
        self.close_button.set_relative_position((self.popup_rect.right - close_size - 16, self.popup_rect.top + 16))

        reroll_width = max(130, min(220, int(self.popup_rect.width * 0.42)))
        reroll_height = max(30, min(46, int(self.popup_rect.height * 0.12)))
        reroll_x = self.popup_rect.centerx - reroll_width // 2
        reroll_y = self.popup_rect.bottom - reroll_height - 20
        self.reroll_button.set_dimensions((reroll_width, reroll_height))
        self.reroll_button.set_relative_position((reroll_x, reroll_y))

    
    def show(self) -> None:
        self.active = True
        self.selected = None
        self.options = self._show_upgrades()
        self._set_ui_visible(True)

        self.option_levels = {
            upgrade.name: self.player.upgrade_levels.get(upgrade.name, 0)
            for upgrade in self.options
            }


    def _show_upgrades(self):
        available_upgrades = [upgrade for upgrade in self.upgrades if not upgrade.is_maxed(self.player)]
        if available_upgrades:
            upgrades = random.sample(available_upgrades, min(3, len(available_upgrades)))
            return upgrades
        return []


    def hide(self):
        self.active = False
        self.roll_amount = 1
        self._set_ui_visible(False)


    def _current_roll_cost(self) -> int:
        return self.roll_cost + 5 * self.roll_amount


    def reroll_items(self) -> None:
        roll_cost = self._current_roll_cost()
        if self.player.gold >= roll_cost:
            self.player.spend_gold(roll_cost)
            self.show()
            self.roll_amount += 1


    def handle_event(self, event: pygame.event.Event) -> int:
        self._responsive_ui()

        if not self.active:
            return None

        self.manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.close_button:
                self.click_sound.play()
                self.hide()
                return None
            if event.ui_element == self.reroll_button:
                random.choice(self.roll_sound).play()
                self.reroll_items()
                return None
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mx,my):
                    self.power_up_sound.play()
                    self.selected = i
                    self.roll_amount = 1
                    return i

        return None
    

    def update_animation(self, dt:float) -> None:
        self.image = self.popupSprite.get_current_frame()
        self.popupSprite.update(dt)

    
    def update(self, dt:float) -> None:
        self._responsive_ui()
        self.update_animation(dt)
        if self.active:
            self.manager.update(dt)
    

    def draw(self):
        if not self.active:
            return  

        self._responsive_ui()

        # darken background
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.window.blit(overlay, (0, 0))   

        # --- popup sprite ---
        frame = self.popupSprite.get_current_frame()
        frame = pygame.transform.scale(
            frame,
            (
                self.popup_rect.width,
                self.popup_rect.height
            )
        )   

        popup_x = self.popup_rect.centerx - frame.get_width() // 2
        popup_y = self.popup_rect.centery - frame.get_height() // 2 

        # draw animated popup
        self.window.blit(frame, (popup_x, popup_y)) 

        # ---- draw text + buttons ----
        base_positions = [0.2, 0.42, 0.64]
        self.option_rects = []

        for i, upgrade in enumerate(self.options):
            base_y = int(frame.get_height() * base_positions[i])

            rect = pygame.Rect(
                popup_x + int(frame.get_width() * 0.09),
                popup_y + base_y,
                int(frame.get_width() * 0.82),
                max(52, int(frame.get_height() * 0.17))
            )
            self.option_rects.append(rect)

            # Card background
            card_bg = (28, 38, 44)
            card_border = (194, 167, 97)
            pygame.draw.rect(self.window, card_bg, rect, border_radius=6)
            pygame.draw.rect(self.window, card_border, rect, 2, border_radius=6)

            #Upgrade image
            icon = pygame.transform.scale(
                upgrade.image,
                (max(26, int(rect.height * 0.66)), max(26, int(rect.height * 0.66)))
            )
            icon_x = rect.x + max(8, int(rect.width * 0.03))
            icon_y = rect.centery - icon.get_height() // 2
            self.window.blit(icon, (icon_x, icon_y))

            #Upgrade Name
            name_surface = self.font.render(upgrade.name + ":", True, NAME_TEXT_COLOR)
            name_x = icon_x + icon.get_width() + max(8, int(rect.width * 0.03))
            name_y = rect.y + max(6, int(rect.height * 0.1))
            self.window.blit(name_surface, (name_x, name_y))

            # Current upgrade level text
            current_level = self.option_levels.get(upgrade.name, 0)
            level_text = f"{current_level}/{upgrade.max_level}"
            level_surface = self.font.render(level_text, True, LVL_TEXT_COLOR)
            level_x = rect.right - level_surface.get_width() - max(8, int(rect.width * 0.03))
            level_y = name_y
            self.window.blit(level_surface, (level_x, level_y))

            #Upgrade Description
            desc_lines = wrap_text(
                upgrade.description,
                self.font,
                max(80, rect.width - (icon.get_width() + int(rect.width * 0.08)))
            )

            # Draw wrapped description
            line_y = name_y + name_surface.get_height()
            for line in desc_lines:
                desc_surface = self.font.render(line, True, DESC_TEXT_COLOR)
                self.window.blit(desc_surface, (name_x, line_y))
                line_y += desc_surface.get_height()

        lvl_up_text = self.font.render("Level Up!", True, NAME_TEXT_COLOR)
        self.window.blit(lvl_up_text, (popup_x + frame.get_width() // 2 - lvl_up_text.get_width() // 2, popup_y + max(18, int(frame.get_height() * 0.08))))

        # reroll button
        current_roll_cost = self._current_roll_cost()
        self.reroll_button.set_text(f"Reroll ({current_roll_cost}g)")

        gold_text = self.font.render(f"Gold: {self.player.gold}", True, NAME_TEXT_COLOR)
        self.window.blit(gold_text, (popup_x + max(14, int(frame.get_width() * 0.04)), popup_y + max(10, int(frame.get_height() * 0.03))))

        self.manager.draw_ui(self.window)
