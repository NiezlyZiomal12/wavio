import pygame
import pygame_gui
from pygame_gui.elements import UIButton

from config import FONT, NAME_TEXT_COLOR, DESC_TEXT_COLOR
from src.core import Animation, wrap_text
from src.core.audio import apply_sfx_volume
from src.gameplay.items.active_items.active_item import ACTIVE_ITEM_CONFIG, create_active_item


class ActiveItemSwapUi:
    def __init__(self, window: pygame.Surface, width: int, height: int, player: object) -> None:
        self.window = window
        self.width = width
        self.height = height
        self.current_size = self.window.get_size()
        self.player = player

        self.active = False
        self.pending_item_id = None
        self.pending_drop = None

        self.font_size = 24
        self.font = pygame.font.Font(FONT, self.font_size)
        self.icon_cache = {}

        self.click_sound = apply_sfx_volume(
            pygame.mixer.Sound("src/assets/sounds/gui/click.wav")
        )

        self.manager = pygame_gui.UIManager(
            self.current_size, theme_path="src/assets/pygame_gui_styles/pause_theme.json"
        )
        self.popup_rect = self._compute_popup_rect()
        self.popupSprite = Animation(
            pygame.image.load("src/assets/ui/lvlUpUi.png").convert_alpha(),
            400,
            300,
            0,
            2,
            0.2,
        )
        self.image = self.popupSprite.get_current_frame()

        self.pick_button = UIButton(
            relative_rect=pygame.Rect(0, 0, 150, 38),
            text="Pick",
            manager=self.manager,
            object_id="#button",
        )
        self.drop_button = UIButton(
            relative_rect=pygame.Rect(0, 0, 150, 38),
            text="Drop",
            manager=self.manager,
            object_id="#button",
        )

        self._set_ui_visible(False)
        self._responsive_ui(force=True)


    def _set_ui_visible(self, visible: bool) -> None:
        if visible:
            self.pick_button.show()
            self.drop_button.show()
        else:
            self.pick_button.hide()
            self.drop_button.hide()


    def _compute_popup_rect(self) -> pygame.Rect:
        width, height = self.current_size
        margin = max(12, int(min(width, height) * 0.05))
        popup_width = max(360, min(600, width - (2 * margin)))
        popup_height = max(260, min(420, height - (2 * margin)))
        return pygame.Rect(
            (width - popup_width) // 2,
            (height - popup_height) // 2,
            popup_width,
            popup_height,
        )


    def _responsive_ui(self, force: bool = False) -> None:
        new_size = self.window.get_size()
        if not force and new_size == self.current_size:
            return

        self.current_size = new_size
        self.width, self.height = new_size
        self.manager.set_window_resolution(self.current_size)
        self.popup_rect = self._compute_popup_rect()

        self.font_size = max(16, min(26, int(min(self.popup_rect.width, self.popup_rect.height) * 0.07)))
        self.font = pygame.font.Font(FONT, self.font_size)

        button_height = max(30, min(46, int(self.popup_rect.height * 0.12)))
        button_width = max(120, min(200, int(self.popup_rect.width * 0.35)))
        button_y = self.popup_rect.bottom - button_height - 20
        gap = max(10, int(self.popup_rect.width * 0.05))
        total_width = (button_width * 2) + gap
        start_x = self.popup_rect.centerx - total_width // 2

        self.pick_button.set_dimensions((button_width, button_height))
        self.pick_button.set_relative_position((start_x, button_y))

        self.drop_button.set_dimensions((button_width, button_height))
        self.drop_button.set_relative_position((start_x + button_width + gap, button_y))


    def show(self, item_id: str, drop_sprite: pygame.sprite.Sprite | None) -> None:
        self.active = True
        self.pending_item_id = item_id
        self.pending_drop = drop_sprite
        self._set_ui_visible(True)


    def hide(self) -> None:
        self.active = False
        self.pending_item_id = None
        self.pending_drop = None
        self._set_ui_visible(False)


    def _get_icon(self, item_id: str, target_size: int) -> pygame.Surface:
        if item_id not in self.icon_cache:
            icon_surface = None
            config = ACTIVE_ITEM_CONFIG.get(item_id)
            if config:
                try:
                    icon_surface = pygame.image.load(config["icon"]).convert_alpha()
                except (pygame.error, FileNotFoundError, KeyError):
                    icon_surface = None

            if icon_surface is None:
                icon_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
                pygame.draw.rect(icon_surface, (190, 155, 75), icon_surface.get_rect(), border_radius=4)

            self.icon_cache[item_id] = icon_surface

        base_icon = self.icon_cache[item_id]
        return pygame.transform.smoothscale(base_icon, (target_size, target_size))


    def _swap_item(self) -> None:
        if not self.pending_item_id:
            return
        new_item = create_active_item(self.pending_item_id)
        self.player.set_active_item(new_item)
        if self.pending_drop is not None:
            self.pending_drop.kill()


    def _drop_item(self) -> None:
        if self.pending_drop is not None:
            self.pending_drop.kill()


    def handle_event(self, event: pygame.event.Event) -> str | None:
        self._responsive_ui()

        if not self.active:
            return None

        self.manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.pick_button:
                self.click_sound.play()
                self._swap_item()
                self.hide()
                return "pick"
            if event.ui_element == self.drop_button:
                self.click_sound.play()
                self._drop_item()
                self.hide()
                return "drop"

        return None


    def update_animation(self, dt: float) -> None:
        self.image = self.popupSprite.get_current_frame()
        self.popupSprite.update(dt)


    def update(self, dt: float) -> None:
        self._responsive_ui()
        self.update_animation(dt)
        if self.active:
            self.manager.update(dt)


    def _draw_item_card(self, rect: pygame.Rect, label: str, item_id: str | None) -> None:
        card_bg = (28, 38, 44)
        card_border = (194, 167, 97)
        pygame.draw.rect(self.window, card_bg, rect, border_radius=6)
        pygame.draw.rect(self.window, card_border, rect, 2, border_radius=6)

        label_surface = self.font.render(label, True, NAME_TEXT_COLOR)
        label_x = rect.x + 12
        label_y = rect.y + 8
        self.window.blit(label_surface, (label_x, label_y))

        if not item_id:
            return

        config = ACTIVE_ITEM_CONFIG.get(item_id, {})
        icon_size = max(24, int(rect.height * 0.48))
        icon = self._get_icon(item_id, icon_size)
        icon_x = rect.x + 12
        top_padding = label_surface.get_height() + 14
        icon_y = rect.y + top_padding + max(0, (rect.height - top_padding - icon.get_height()) // 2)
        self.window.blit(icon, (icon_x, icon_y))

        name_text = config.get("name", item_id)
        name_surface = self.font.render(name_text, True, NAME_TEXT_COLOR)
        name_x = icon_x + icon.get_width() + 18
        name_y = icon_y - 2
        self.window.blit(name_surface, (name_x, name_y))

        desc_text = config.get("description", "")
        desc_lines = wrap_text(
            desc_text,
            self.font,
            max(80, rect.width - (icon.get_width() + 36)),
        )
        line_y = name_y + name_surface.get_height()
        for line in desc_lines:
            desc_surface = self.font.render(line, True, DESC_TEXT_COLOR)
            self.window.blit(desc_surface, (name_x, line_y))
            line_y += desc_surface.get_height()


    def draw(self) -> None:
        if not self.active:
            return

        self._responsive_ui()

        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.window.blit(overlay, (0, 0))

        frame = self.popupSprite.get_current_frame()
        frame = pygame.transform.scale(
            frame, (self.popup_rect.width, self.popup_rect.height)
        )

        popup_x = self.popup_rect.centerx - frame.get_width() // 2
        popup_y = self.popup_rect.centery - frame.get_height() // 2
        self.window.blit(frame, (popup_x, popup_y))

        title = self.font.render("Active Item", True, NAME_TEXT_COLOR)
        title_x = popup_x + frame.get_width() // 2 - title.get_width() // 2
        title_y = popup_y + max(16, int(frame.get_height() * 0.08))
        self.window.blit(title, (title_x, title_y))

        card_width = int(frame.get_width() * 0.82)
        card_height = max(70, int(frame.get_height() * 0.22))
        card_x = popup_x + int(frame.get_width() * 0.09)
        current_y = popup_y + int(frame.get_height() * 0.24)
        new_y = popup_y + int(frame.get_height() * 0.54)

        current_rect = pygame.Rect(card_x, current_y, card_width, card_height)
        new_rect = pygame.Rect(card_x, new_y, card_width, card_height)

        current_item_id = getattr(self.player.active_item, "item_id", None)
        self._draw_item_card(current_rect, "Current", current_item_id)
        self._draw_item_card(new_rect, "New", self.pending_item_id)

        self.manager.draw_ui(self.window)
