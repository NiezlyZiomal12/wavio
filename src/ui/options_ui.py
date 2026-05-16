import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UIPanel, UIHorizontalSlider
from src.core.audio import (
    apply_sfx_volume,
    get_music_volume,
    get_sfx_volume,
    set_music_volume,
    set_sfx_volume,
)


class OptionsMenuUi:
    def __init__(self, window: pygame.Surface):
        self.window = window
        self.active = False
        self.current_size = self.window.get_size()
        self.manager = pygame_gui.UIManager(
            self.current_size,
            theme_path="src/assets/pygame_gui_styles/pause_theme.json",
        )
        self.click_sound = apply_sfx_volume(
            pygame.mixer.Sound("src/assets/sounds/gui/click.wav")
        )
        self.open_sound = apply_sfx_volume(
            pygame.mixer.Sound("src/assets/sounds/gui/open.wav")
        )

        layout = self._compute_layout()
        self.popup_rect = layout["popup"]

        self.popup_panel = UIPanel(
            relative_rect=self.popup_rect,
            manager=self.manager,
            object_id="#pause_popup",
        )

        self.left_panel = UIPanel(
            relative_rect=layout["left_panel"],
            manager=self.manager,
            container=self.popup_panel,
            object_id="#pause_left_panel",
        )

        self.right_panel = UIPanel(
            relative_rect=layout["right_panel"],
            manager=self.manager,
            container=self.popup_panel,
            object_id="#pause_right_panel",
        )

        self.title_label = UILabel(
            relative_rect=layout["title_label"],
            text="Options",
            manager=self.manager,
            container=self.left_panel,
            object_id="#pause_title",
        )

        self.sound_tab_button = UIButton(
            relative_rect=layout["sound_tab"],
            text="Sound",
            manager=self.manager,
            container=self.left_panel,
            object_id="#button",
        )
        self.graphics_tab_button = UIButton(
            relative_rect=layout["graphics_tab"],
            text="Graphics",
            manager=self.manager,
            container=self.left_panel,
            object_id="#button",
        )
        self.controls_tab_button = UIButton(
            relative_rect=layout["controls_tab"],
            text="Controls",
            manager=self.manager,
            container=self.left_panel,
            object_id="#button",
        )
        self.back_button = UIButton(
            relative_rect=layout["back_button"],
            text="Back",
            manager=self.manager,
            container=self.left_panel,
            object_id="#button",
        )

        self.sound_panel = UIPanel(
            relative_rect=layout["content_panel"],
            manager=self.manager,
            container=self.right_panel,
            object_id="#pause_left_panel",
        )
        self.graphics_panel = UIPanel(
            relative_rect=layout["content_panel"],
            manager=self.manager,
            container=self.right_panel,
            object_id="#pause_left_panel",
        )
        self.controls_panel = UIPanel(
            relative_rect=layout["content_panel"],
            manager=self.manager,
            container=self.right_panel,
            object_id="#pause_left_panel",
        )

        self.sound_title = UILabel(
            relative_rect=layout["tab_title"],
            text="Sound",
            manager=self.manager,
            container=self.sound_panel,
            object_id="#label",
        )
        self.music_label = UILabel(
            relative_rect=layout["music_label"],
            text="Music Volume",
            manager=self.manager,
            container=self.sound_panel,
            object_id="#label",
        )
        music_start = int(round(get_music_volume() * 100))
        self.music_slider = UIHorizontalSlider(
            relative_rect=layout["music_slider"],
            start_value=music_start,
            value_range=(0, 100),
            manager=self.manager,
            container=self.sound_panel,
            object_id="#options_slider",
        )
        self.music_value_label = UILabel(
            relative_rect=layout["music_value"],
            text=f"{music_start}%",
            manager=self.manager,
            container=self.sound_panel,
            object_id="#label",
        )

        self.sfx_label = UILabel(
            relative_rect=layout["sfx_label"],
            text="SFX Volume",
            manager=self.manager,
            container=self.sound_panel,
            object_id="#label",
        )
        sfx_start = int(round(get_sfx_volume() * 100))
        self.sfx_slider = UIHorizontalSlider(
            relative_rect=layout["sfx_slider"],
            start_value=sfx_start,
            value_range=(0, 100),
            manager=self.manager,
            container=self.sound_panel,
            object_id="#options_slider",
        )
        self.sfx_value_label = UILabel(
            relative_rect=layout["sfx_value"],
            text=f"{sfx_start}%",
            manager=self.manager,
            container=self.sound_panel,
            object_id="#label",
        )

        self.graphics_title = UILabel(
            relative_rect=layout["tab_title"],
            text="Graphics",
            manager=self.manager,
            container=self.graphics_panel,
            object_id="#label",
        )
        self.graphics_hint = UILabel(
            relative_rect=layout["tab_hint"],
            text="No settings yet",
            manager=self.manager,
            container=self.graphics_panel,
            object_id="#label",
        )

        self.controls_title = UILabel(
            relative_rect=layout["tab_title"],
            text="Controls",
            manager=self.manager,
            container=self.controls_panel,
            object_id="#label",
        )
        self.controls_hint = UILabel(
            relative_rect=layout["tab_hint"],
            text="No settings yet",
            manager=self.manager,
            container=self.controls_panel,
            object_id="#label",
        )

        self.ui_elements = [
            self.popup_panel,
            self.left_panel,
            self.right_panel,
            self.title_label,
            self.sound_tab_button,
            self.graphics_tab_button,
            self.controls_tab_button,
            self.back_button,
            self.sound_panel,
            self.graphics_panel,
            self.controls_panel,
            self.sound_title,
            self.music_label,
            self.music_slider,
            self.music_value_label,
            self.sfx_label,
            self.sfx_slider,
            self.sfx_value_label,
            self.graphics_title,
            self.graphics_hint,
            self.controls_title,
            self.controls_hint,
        ]

        self.active_tab = "sound"
        self._set_tab(self.active_tab)
        self._set_visible(False)

    def show(self) -> None:
        self.active = True
        self.open_sound.play()
        self._set_visible(True)
        self._set_tab(self.active_tab)

    def hide(self) -> None:
        self.open_sound.play()
        self.active = False
        self._set_visible(False)

    def _set_visible(self, visible: bool) -> None:
        for element in self.ui_elements:
            if visible:
                element.show()
            else:
                element.hide()

    def _set_tab(self, tab: str) -> None:
        self.active_tab = tab
        if tab == "sound":
            self.sound_panel.show()
            self.graphics_panel.hide()
            self.controls_panel.hide()
        elif tab == "graphics":
            self.sound_panel.hide()
            self.graphics_panel.show()
            self.controls_panel.hide()
        else:
            self.sound_panel.hide()
            self.graphics_panel.hide()
            self.controls_panel.show()

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.active:
            return

        self.manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self.click_sound.play()
            if event.ui_element == self.sound_tab_button:
                self._set_tab("sound")
            elif event.ui_element == self.graphics_tab_button:
                self._set_tab("graphics")
            elif event.ui_element == self.controls_tab_button:
                self._set_tab("controls")
            elif event.ui_element == self.back_button:
                self.hide()

        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.music_slider:
                new_value = int(event.value)
                self.music_value_label.set_text(f"{new_value}%")
                set_music_volume(new_value / 100)
            elif event.ui_element == self.sfx_slider:
                new_value = int(event.value)
                self.sfx_value_label.set_text(f"{new_value}%")
                set_sfx_volume(new_value / 100)

    def update(self, dt: float) -> None:
        self._sync_to_window_size()
        if not self.active:
            return
        self.manager.update(dt)

    def draw(self) -> None:
        if not self.active:
            return

        overlay = pygame.Surface(self.current_size, pygame.SRCALPHA)
        overlay.fill((8, 12, 18, 175))
        self.window.blit(overlay, (0, 0))
        self.manager.draw_ui(self.window)

    def _sync_to_window_size(self) -> None:
        new_size = self.window.get_size()
        if new_size == self.current_size:
            return

        self.current_size = new_size
        self.manager.set_window_resolution(self.current_size)
        self._apply_layout()

    def _compute_layout(self) -> dict[str, pygame.Rect]:
        width, height = self.current_size

        margin = max(18, int(min(width, height) * 0.04))
        popup_width = max(560, min(980, width - (2 * margin)))
        popup_height = max(360, min(660, height - (2 * margin)))
        popup_rect = pygame.Rect(
            (width - popup_width) // 2,
            (height - popup_height) // 2,
            popup_width,
            popup_height,
        )

        inner_pad = max(14, int(popup_width * 0.03))
        column_gap = max(12, int(popup_width * 0.025))

        left_width = max(230, int(popup_width * 0.32))
        max_left_width = popup_width - (2 * inner_pad) - column_gap - 220
        left_width = min(left_width, max_left_width)

        left_panel = pygame.Rect(
            inner_pad,
            inner_pad,
            left_width,
            popup_height - (2 * inner_pad),
        )
        right_x = left_panel.right + column_gap
        right_panel = pygame.Rect(
            right_x,
            inner_pad,
            popup_width - right_x - inner_pad,
            popup_height - (2 * inner_pad),
        )

        left_content_pad = max(14, int(left_panel.width * 0.07))
        title_height = max(36, int(left_panel.height * 0.14))
        title_y = max(14, int(left_panel.height * 0.06))
        title_label = pygame.Rect(
            left_content_pad,
            title_y,
            left_panel.width - (2 * left_content_pad),
            title_height,
        )

        button_width = left_panel.width - (2 * left_content_pad)
        button_height = max(36, min(56, int(left_panel.height * 0.12)))
        buttons_start_y = title_label.bottom + max(14, int(left_panel.height * 0.06))
        gap = max(10, int(left_panel.height * 0.035))

        sound_tab = pygame.Rect(left_content_pad, buttons_start_y, button_width, button_height)
        graphics_tab = pygame.Rect(
            left_content_pad,
            buttons_start_y + (button_height + gap),
            button_width,
            button_height,
        )
        controls_tab = pygame.Rect(
            left_content_pad,
            buttons_start_y + 2 * (button_height + gap),
            button_width,
            button_height,
        )

        back_button = pygame.Rect(
            left_content_pad,
            left_panel.height - button_height - left_content_pad,
            button_width,
            button_height,
        )

        right_pad = max(12, int(right_panel.width * 0.06))
        content_panel = pygame.Rect(
            right_pad,
            right_pad,
            right_panel.width - (2 * right_pad),
            right_panel.height - (2 * right_pad),
        )

        tab_title = pygame.Rect(12, 10, content_panel.width - 24, 32)
        tab_hint = pygame.Rect(12, 60, content_panel.width - 24, 32)

        row_label_width = max(160, int(content_panel.width * 0.32))
        value_width = max(64, int(content_panel.width * 0.15))
        slider_width = content_panel.width - row_label_width - value_width - 48
        row_height = max(32, int(content_panel.height * 0.12))
        slider_height = max(18, int(row_height * 0.5))
        row_start_y = tab_title.bottom + max(20, int(content_panel.height * 0.08))
        row_gap = max(18, int(content_panel.height * 0.06))

        music_label = pygame.Rect(12, row_start_y, row_label_width, row_height)
        music_slider = pygame.Rect(
            music_label.right + 12,
            row_start_y + (row_height - slider_height) // 2,
            slider_width,
            slider_height,
        )
        music_value = pygame.Rect(music_slider.right + 12, row_start_y, value_width, row_height)

        sfx_y = row_start_y + row_height + row_gap
        sfx_label = pygame.Rect(12, sfx_y, row_label_width, row_height)
        sfx_slider = pygame.Rect(
            sfx_label.right + 12,
            sfx_y + (row_height - slider_height) // 2,
            slider_width,
            slider_height,
        )
        sfx_value = pygame.Rect(sfx_slider.right + 12, sfx_y, value_width, row_height)

        return {
            "popup": popup_rect,
            "left_panel": left_panel,
            "right_panel": right_panel,
            "title_label": title_label,
            "sound_tab": sound_tab,
            "graphics_tab": graphics_tab,
            "controls_tab": controls_tab,
            "back_button": back_button,
            "content_panel": content_panel,
            "tab_title": tab_title,
            "tab_hint": tab_hint,
            "music_label": music_label,
            "music_slider": music_slider,
            "music_value": music_value,
            "sfx_label": sfx_label,
            "sfx_slider": sfx_slider,
            "sfx_value": sfx_value,
        }

    def _apply_layout(self) -> None:
        layout = self._compute_layout()
        self.popup_rect = layout["popup"]

        self.popup_panel.set_dimensions((self.popup_rect.width, self.popup_rect.height))
        self.popup_panel.set_relative_position((self.popup_rect.x, self.popup_rect.y))

        self.left_panel.set_dimensions((layout["left_panel"].width, layout["left_panel"].height))
        self.left_panel.set_relative_position((layout["left_panel"].x, layout["left_panel"].y))

        self.right_panel.set_dimensions((layout["right_panel"].width, layout["right_panel"].height))
        self.right_panel.set_relative_position((layout["right_panel"].x, layout["right_panel"].y))

        self.title_label.set_dimensions((layout["title_label"].width, layout["title_label"].height))
        self.title_label.set_relative_position((layout["title_label"].x, layout["title_label"].y))

        self.sound_tab_button.set_dimensions((layout["sound_tab"].width, layout["sound_tab"].height))
        self.sound_tab_button.set_relative_position((layout["sound_tab"].x, layout["sound_tab"].y))

        self.graphics_tab_button.set_dimensions((layout["graphics_tab"].width, layout["graphics_tab"].height))
        self.graphics_tab_button.set_relative_position((layout["graphics_tab"].x, layout["graphics_tab"].y))

        self.controls_tab_button.set_dimensions((layout["controls_tab"].width, layout["controls_tab"].height))
        self.controls_tab_button.set_relative_position((layout["controls_tab"].x, layout["controls_tab"].y))

        self.back_button.set_dimensions((layout["back_button"].width, layout["back_button"].height))
        self.back_button.set_relative_position((layout["back_button"].x, layout["back_button"].y))

        self.sound_panel.set_dimensions((layout["content_panel"].width, layout["content_panel"].height))
        self.sound_panel.set_relative_position((layout["content_panel"].x, layout["content_panel"].y))

        self.graphics_panel.set_dimensions((layout["content_panel"].width, layout["content_panel"].height))
        self.graphics_panel.set_relative_position((layout["content_panel"].x, layout["content_panel"].y))

        self.controls_panel.set_dimensions((layout["content_panel"].width, layout["content_panel"].height))
        self.controls_panel.set_relative_position((layout["content_panel"].x, layout["content_panel"].y))

        self.sound_title.set_dimensions((layout["tab_title"].width, layout["tab_title"].height))
        self.sound_title.set_relative_position((layout["tab_title"].x, layout["tab_title"].y))

        self.graphics_title.set_dimensions((layout["tab_title"].width, layout["tab_title"].height))
        self.graphics_title.set_relative_position((layout["tab_title"].x, layout["tab_title"].y))

        self.controls_title.set_dimensions((layout["tab_title"].width, layout["tab_title"].height))
        self.controls_title.set_relative_position((layout["tab_title"].x, layout["tab_title"].y))

        self.graphics_hint.set_dimensions((layout["tab_hint"].width, layout["tab_hint"].height))
        self.graphics_hint.set_relative_position((layout["tab_hint"].x, layout["tab_hint"].y))

        self.controls_hint.set_dimensions((layout["tab_hint"].width, layout["tab_hint"].height))
        self.controls_hint.set_relative_position((layout["tab_hint"].x, layout["tab_hint"].y))

        self.music_label.set_dimensions((layout["music_label"].width, layout["music_label"].height))
        self.music_label.set_relative_position((layout["music_label"].x, layout["music_label"].y))

        self.music_slider.set_dimensions((layout["music_slider"].width, layout["music_slider"].height))
        self.music_slider.set_relative_position((layout["music_slider"].x, layout["music_slider"].y))

        self.music_value_label.set_dimensions((layout["music_value"].width, layout["music_value"].height))
        self.music_value_label.set_relative_position((layout["music_value"].x, layout["music_value"].y))

        self.sfx_label.set_dimensions((layout["sfx_label"].width, layout["sfx_label"].height))
        self.sfx_label.set_relative_position((layout["sfx_label"].x, layout["sfx_label"].y))

        self.sfx_slider.set_dimensions((layout["sfx_slider"].width, layout["sfx_slider"].height))
        self.sfx_slider.set_relative_position((layout["sfx_slider"].x, layout["sfx_slider"].y))

        self.sfx_value_label.set_dimensions((layout["sfx_value"].width, layout["sfx_value"].height))
        self.sfx_value_label.set_relative_position((layout["sfx_value"].x, layout["sfx_value"].y))
