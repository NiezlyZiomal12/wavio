import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIPanel, UILabel
from src.gameplay.player.characters_config import CHARACTERS


class Character_select_scene:
    def __init__(self, window: pygame.Surface):
        self.window = window
        self.running = True
        self.start_game = False
        self.selected_character = "Mage"

        self.current_size = self.window.get_size()
        self.manager = pygame_gui.UIManager(self.current_size, theme_path="src/assets/pygame_gui_styles/pause_theme.json")

        self.title_label = UILabel(
            relative_rect=pygame.Rect(0,0, 440, 40),
            text="Choose Your Character",
            manager=self.manager,
            object_id="#label"
        )

        self.selected_label = UILabel(
            relative_rect=pygame.Rect(0,0, 360, 30),
            text=f"Selected: {self.selected_character}",
            manager=self.manager,
            object_id="#label"
        )

        self.container_panel = UIPanel(
            relative_rect=pygame.Rect(0,0, 600, 320),
            starting_height=1,
            manager=self.manager,
        )

        self.character_buttons = {}
        names = list(CHARACTERS.keys())
        for index, name in enumerate(names):
            button = UIButton(
                relative_rect=pygame.Rect(0, 0, 180, 210),
                text=name,
                manager=self.manager,
                container=self.container_panel,
                object_id="#button"
            )
            self.character_buttons[name] = button

        self.start_button = UIButton(
            relative_rect=pygame.Rect(0, 0, 160, 56),
            text="Battle",
            manager=self.manager,
            object_id="#button"
        )

        self._responsive_ui()
        self._refresh_character_button_texts()


    def get_selected_character(self):
        return self.selected_character


    def _responsive_ui(self) -> None:
        width, height = self.current_size

        title_width = max(280, min(480, int(width * 0.55)))
        title_height = 40
        self.title_label.set_dimensions((title_width, title_height))
        self.title_label.set_relative_position(((width - title_width) // 2, int(height * 0.06)))

        selected_width = max(240, min(420, int(width * 0.45)))
        selected_height = 30
        self.selected_label.set_dimensions((selected_width, selected_height))
        self.selected_label.set_relative_position(((width - selected_width) // 2, int(height * 0.12)))

        panel_width = max(340, min(width - 80, 920))
        panel_height = max(220, min(int(height * 0.52), 420))
        panel_x = (width - panel_width) // 2
        panel_y = int(height * 0.2)
        self.container_panel.set_dimensions((panel_width, panel_height))
        self.container_panel.set_relative_position((panel_x, panel_y))

        button_width = max(130, min(210, int(panel_width * 0.25)))
        button_height = max(110, min(230, int(panel_height * 0.72)))
        side_padding = max(12, int(panel_width * 0.05))
        available_width = panel_width - (2 * side_padding)
        count = max(1, len(self.character_buttons))
        spacing = max(8, (available_width - (count * button_width)) // (count - 1 if count > 1 else 1))
        start_x = side_padding
        y = max(12, (panel_height - button_height) // 2)

        for index, button in enumerate(self.character_buttons.values()):
            x = start_x + index * (button_width + spacing)
            button.set_dimensions((button_width, button_height))
            button.set_relative_position((x, y))

        start_button_width = max(140, min(220, int(width * 0.2)))
        start_button_height = max(50, min(64, int(height * 0.08)))
        self.start_button.set_dimensions((start_button_width, start_button_height))
        self.start_button.set_relative_position((width - start_button_width - 32, height - start_button_height - 28))


    def _refresh_character_button_texts(self) -> None:
        for name, button in self.character_buttons.items():
            if name == self.selected_character:
                button.set_text(f"> {name} <")
            else:
                button.set_text(name)

        self.selected_label.set_text(f"Selected: {self.selected_character}")


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

                for name, button in self.character_buttons.items():
                    if event.ui_element == button:
                        self.selected_character = name
                        self._refresh_character_button_texts()
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