import pygame
import pygame_gui
from pygame_gui.elements import UIButton
from src.core.utils import Animation
from config import FONT, NAME_TEXT_COLOR, DESC_TEXT_COLOR

class WinUi:
    def __init__(self, window, width, height, player, elapsed_time):
        self.window = window
        self.width = width
        self.height = height
        self.current_size = self.window.get_size()

        self.player = player
        self.elapsed_time = elapsed_time
        self.active = False
        self.font_size = 24
        self.font = pygame.font.Font(FONT, self.font_size)
        self.title_font_size = 32
        self.title_font = pygame.font.Font(FONT, self.title_font_size)
        self.small_font_size = 18
        self.small_font = pygame.font.Font(FONT, self.small_font_size)

        self.click_sound = pygame.mixer.Sound("src/assets/sounds/gui/click.wav")
        self.victory_sound = pygame.mixer.Sound("src/assets/sounds/game/power_up.wav")
        self.victory_sound.set_volume(0.2)

        self.manager = pygame_gui.UIManager(self.current_size, theme_path="src/assets/pygame_gui_styles/pause_theme.json")
        self.popup_rect = self._compute_popup_rect()
        self.popupSprite = Animation(pygame.image.load("src/assets/ui/winUI.png").convert_alpha(), 1000, 1000, 0, 1, 0.2)
        self.image = self.popupSprite.get_current_frame()

        self.continue_button = UIButton(
            relative_rect=pygame.Rect(0, 0, 150, 38),
            text="Continue",
            manager=self.manager,
            object_id="#rerollButton"
        )
        self._set_ui_visible(False)
        self._responsive_ui(force=True)

    def _set_ui_visible(self, visible: bool) -> None:
        if visible:
            self.continue_button.show()
        else:
            self.continue_button.hide()

    def _compute_popup_rect(self) -> pygame.Rect:
        width, height = self.current_size
        margin = max(10, int(min(width, height) * 0.035))
        popup_width = max(520, min(900, width - (2 * margin)))
        popup_height = max(520, min(900, height - (2 * margin)))
        return pygame.Rect((width - popup_width) // 2, (height - popup_height) // 2, popup_width, popup_height)

    def _responsive_ui(self, force: bool = False) -> None:
        new_size = self.window.get_size()
        if not force and new_size == self.current_size:
            return

        self.current_size = new_size
        self.width, self.height = new_size
        self.manager.set_window_resolution(self.current_size)
        self.popup_rect = self._compute_popup_rect()

        self.title_font_size = max(24, min(40, int(min(self.popup_rect.width, self.popup_rect.height) * 0.12)))
        self.title_font = pygame.font.Font(FONT, self.title_font_size)
        
        self.font_size = max(16, min(28, int(min(self.popup_rect.width, self.popup_rect.height) * 0.07)))
        self.font = pygame.font.Font(FONT, self.font_size)
        
        self.small_font_size = max(14, min(22, int(min(self.popup_rect.width, self.popup_rect.height) * 0.05)))
        self.small_font = pygame.font.Font(FONT, self.small_font_size)

        continue_width = max(130, min(220, int(self.popup_rect.width * 0.42)))
        continue_height = max(30, min(46, int(self.popup_rect.height * 0.12)))
        continue_x = self.popup_rect.centerx - continue_width // 2
        continue_y = self.popup_rect.bottom - continue_height - 20
        self.continue_button.set_dimensions((continue_width, continue_height))
        self.continue_button.set_relative_position((continue_x, continue_y))

    def show(self) -> None:
        self.active = True
        self._set_ui_visible(True)
        self.victory_sound.play()

    def hide(self) -> None:
        self.active = False
        self._set_ui_visible(False)

    def handle_event(self, event: pygame.event.Event) -> bool:
        self._responsive_ui()

        if not self.active:
            return False

        self.manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.continue_button:
                self.click_sound.play()
                self.hide()
                return True  # Signal to return to main menu

        return False

    def update_animation(self, dt: float) -> None:
        self.image = self.popupSprite.get_current_frame()
        self.popupSprite.update(dt)

    def update(self, dt: float) -> None:
        self._responsive_ui()
        self.update_animation(dt)
        if self.active:
            self.manager.update(dt)

    def _format_time(self, seconds: float) -> str:
        """Format elapsed time as MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

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

        # ---- draw text ----
        # Stats section
        line_spacing = max(5, int(frame.get_height() * 0.05))
        num_lines = 4
        total_block_height = line_spacing * (num_lines - 1) + self.font_size

        bottom_section_top = popup_y + int(frame.get_height() * 0.62)
        stats_start_y = bottom_section_top + (600 - bottom_section_top - total_block_height) // 2

        block_width = int(frame.get_width() * 0.55)
        stats_x = popup_x + (frame.get_width() - block_width) // 2
        stats_right_x = stats_x + block_width

        # Time Survived
        time_str = self._format_time(self.elapsed_time)
        time_label = self.font.render("Time Survived:", True, DESC_TEXT_COLOR)
        time_value = self.font.render(time_str, True, NAME_TEXT_COLOR)
        self.window.blit(time_label, (stats_x, stats_start_y))
        self.window.blit(time_value, (stats_right_x - time_value.get_width(), stats_start_y))

        # Level
        level_str = str(self.player.level)
        level_label = self.font.render("Final Level:", True, DESC_TEXT_COLOR)
        level_value = self.font.render(level_str, True, NAME_TEXT_COLOR)
        self.window.blit(level_label, (stats_x, stats_start_y + line_spacing))
        self.window.blit(level_value, (stats_right_x - level_value.get_width(), stats_start_y + line_spacing))

        # Experience
        xp_str = str(self.player.xp)
        xp_label = self.font.render("Experience:", True, DESC_TEXT_COLOR)
        xp_value = self.font.render(xp_str, True, NAME_TEXT_COLOR)
        self.window.blit(xp_label, (stats_x, stats_start_y + line_spacing * 2))
        self.window.blit(xp_value, (stats_right_x - xp_value.get_width(), stats_start_y + line_spacing * 2))

        # Gold
        gold_str = str(self.player.gold)
        gold_label = self.font.render("Gold Collected:", True, DESC_TEXT_COLOR)
        gold_value = self.font.render(gold_str, True, NAME_TEXT_COLOR)
        self.window.blit(gold_label, (stats_x, stats_start_y + line_spacing * 3))
        self.window.blit(gold_value, (stats_right_x - gold_value.get_width(), stats_start_y + line_spacing * 3))

        self.manager.draw_ui(self.window)