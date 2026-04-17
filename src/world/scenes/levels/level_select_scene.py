import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIPanel, UILabel
from .level_config import LEVELS

DIFFICULTIES = ["Easy", "Normal", "Hard"]


class Level_select_scene:
    def __init__(self, window: pygame.Surface):
        self.window = window
        self.running = True
        self.start_game = False
        self.current_size = self.window.get_size()

        self.selected_level = LEVELS[0]
        self.selected_difficulty = "Normal"

        self.manager = pygame_gui.UIManager(
            self.current_size,
            theme_path="src/assets/pygame_gui_styles/pause_theme.json",
        )

        self.title_label = UILabel(
            relative_rect=pygame.Rect(0, 0, 460, 42),
            text="Choose Your Level",
            manager=self.manager,
            object_id="#pause_title",
        )

        self.left_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, 320, 540),
            starting_height=1,
            manager=self.manager,
            object_id="#pause_left_panel",
        )

        self.right_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, 740, 540),
            starting_height=1,
            manager=self.manager,
            object_id="#pause_right_panel",
        )

        self.levels_label = UILabel(
            relative_rect=pygame.Rect(0, 0, 180, 32),
            text="Levels",
            manager=self.manager,
            container=self.left_panel,
            object_id="#label",
        )

        self.level_buttons: dict[str, UIButton] = {}
        for level in LEVELS:
            button = UIButton(
                relative_rect=pygame.Rect(0, 0, 180, 62),
                text=level["title"],
                manager=self.manager,
                container=self.left_panel,
                object_id="#button",
            )
            self.level_buttons[level["id"]] = button

        self.preview_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, 640, 280),
            starting_height=1,
            manager=self.manager,
            container=self.right_panel,
            object_id="#pause_left_panel",
        )

        self.preview_title = UILabel(
            relative_rect=pygame.Rect(0, 0, 360, 34),
            text=self.selected_level["title"],
            manager=self.manager,
            container=self.preview_panel,
            object_id="#label",
        )

        self.preview_placeholder = UILabel(
            relative_rect=pygame.Rect(0, 0, 560, 130),
            text="[ Level Preview Placeholder ]",
            manager=self.manager,
            container=self.preview_panel,
            object_id="#label",
        )

        self.preview_description = UILabel(
            relative_rect=pygame.Rect(0, 0, 600, 30),
            text=self.selected_level["description"],
            manager=self.manager,
            container=self.preview_panel,
            object_id="#label",
        )

        self.difficulty_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, 640, 180),
            starting_height=1,
            manager=self.manager,
            container=self.right_panel,
            object_id="#pause_left_panel",
        )

        self.difficulty_label = UILabel(
            relative_rect=pygame.Rect(0, 0, 280, 32),
            text="Difficulty",
            manager=self.manager,
            container=self.difficulty_panel,
            object_id="#label",
        )

        self.difficulty_buttons: dict[str, UIButton] = {}
        for difficulty in DIFFICULTIES:
            button = UIButton(
                relative_rect=pygame.Rect(0, 0, 160, 56),
                text=difficulty,
                manager=self.manager,
                container=self.difficulty_panel,
                object_id="#button",
            )
            self.difficulty_buttons[difficulty] = button

        self.start_button = UIButton(
            relative_rect=pygame.Rect(0, 0, 170, 58),
            text="Start",
            manager=self.manager,
            object_id="#button",
        )

        self._layout_ui()
        self._refresh_level_buttons()
        self._refresh_difficulty_buttons()


    def get_selected_level(self) -> dict:
        return self.selected_level


    def get_selected_difficulty(self) -> str:
        return self.selected_difficulty


    def _layout_ui(self) -> None:
        width, height = self.current_size

        title_width = max(300, min(520, int(width * 0.4)))
        self.title_label.set_dimensions((title_width, 42))
        self.title_label.set_relative_position(((width - title_width) // 2, int(height * 0.04)))

        content_top = int(height * 0.12)
        content_height = max(360, min(height - content_top - 110, 680))
        content_width = max(760, min(width - 60, 1440))
        content_x = (width - content_width) // 2

        gap = max(14, int(content_width * 0.02))
        left_width = max(220, min(360, int(content_width * 0.28)))
        right_width = content_width - left_width - gap

        self.left_panel.set_dimensions((left_width, content_height))
        self.left_panel.set_relative_position((content_x, content_top))

        self.right_panel.set_dimensions((right_width, content_height))
        self.right_panel.set_relative_position((content_x + left_width + gap, content_top))

        self.levels_label.set_relative_position((16, 12))
        self.levels_label.set_dimensions((left_width - 32, 32))

        level_button_width = left_width - 32
        level_button_height = max(56, min(74, int(content_height * 0.11)))
        level_gap = max(10, int(content_height * 0.02))
        level_y = 54
        for button in self.level_buttons.values():
            button.set_dimensions((level_button_width, level_button_height))
            button.set_relative_position((16, level_y))
            level_y += level_button_height + level_gap

        right_inner_width = right_width - 24
        preview_height = max(220, min(int(content_height * 0.58), content_height - 180))
        self.preview_panel.set_dimensions((right_inner_width, preview_height))
        self.preview_panel.set_relative_position((12, 12))

        self.preview_title.set_dimensions((right_inner_width - 24, 34))
        self.preview_title.set_relative_position((12, 10))

        placeholder_height = max(90, preview_height - 110)
        self.preview_placeholder.set_dimensions((right_inner_width - 24, placeholder_height))
        self.preview_placeholder.set_relative_position((12, 46))

        self.preview_description.set_dimensions((right_inner_width - 24, 28))
        self.preview_description.set_relative_position((12, preview_height - 34))

        diff_y = preview_height + 24
        diff_height = content_height - diff_y - 12
        self.difficulty_panel.set_dimensions((right_inner_width, diff_height))
        self.difficulty_panel.set_relative_position((12, diff_y))

        self.difficulty_label.set_dimensions((right_inner_width - 24, 32))
        self.difficulty_label.set_relative_position((12, 12))

        diff_button_width = max(120, min(220, int((right_inner_width - 60) / 3)))
        diff_button_height = max(48, min(64, int(diff_height * 0.4)))
        diff_spacing = max(8, int((right_inner_width - 24 - 3 * diff_button_width) / 2))
        diff_button_y = max(52, (diff_height - diff_button_height) // 2)

        for index, difficulty in enumerate(DIFFICULTIES):
            button = self.difficulty_buttons[difficulty]
            diff_x = 12 + index * (diff_button_width + diff_spacing)
            button.set_dimensions((diff_button_width, diff_button_height))
            button.set_relative_position((diff_x, diff_button_y))

        start_button_width = max(150, min(220, int(width * 0.14)))
        start_button_height = max(50, min(64, int(height * 0.08)))
        self.start_button.set_dimensions((start_button_width, start_button_height))
        self.start_button.set_relative_position((width - start_button_width - 28, height - start_button_height - 24))


    def _refresh_level_buttons(self) -> None:
        self.preview_title.set_text(self.selected_level["title"])
        self.preview_description.set_text(self.selected_level["description"])

        for level in LEVELS:
            button = self.level_buttons[level["id"]]
            if level["id"] == self.selected_level["id"]:
                button.set_text(f"> {level['title']} <")
            else:
                button.set_text(level["title"])


    def _refresh_difficulty_buttons(self) -> None:
        for difficulty in DIFFICULTIES:
            button = self.difficulty_buttons[difficulty]
            if difficulty == self.selected_difficulty:
                button.set_text(f"> {difficulty} <")
            else:
                button.set_text(difficulty)


    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.VIDEORESIZE:
                self.current_size = (event.w, event.h)
                self.manager.set_window_resolution(self.current_size)
                self._layout_ui()

            self.manager.process_events(event)

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.start_button:
                    self.start_game = True
                    continue

                for level in LEVELS:
                    if event.ui_element == self.level_buttons[level["id"]]:
                        self.selected_level = level
                        self._refresh_level_buttons()
                        break

                for difficulty in DIFFICULTIES:
                    if event.ui_element == self.difficulty_buttons[difficulty]:
                        self.selected_difficulty = difficulty
                        self._refresh_difficulty_buttons()
                        break


    def update(self, dt: float) -> None:
        new_size = self.window.get_size()
        if new_size != self.current_size:
            self.current_size = new_size
            self.manager.set_window_resolution(self.current_size)
            self._layout_ui()

        self.manager.update(dt)


    def render(self) -> None:
        self.window.fill((26, 37, 37))
        self.manager.draw_ui(self.window)
        pygame.display.update()