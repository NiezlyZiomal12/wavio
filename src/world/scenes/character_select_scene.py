import pygame
import pygame_gui
from config import WIDTH, HEIGHT
from pygame_gui.elements import UIButton, UIPanel, UILabel
from src.gameplay.player.characters_config import CHARACTERS


class Character_select_scene:
    def __init__(self, window: pygame.Surface):
        self.window = window
        self.running = True
        self.start_game = False
        self.selected_character = "Mage"

        self.manager = pygame_gui.UIManager((WIDTH, HEIGHT), theme_path="src/assets/pygame_gui_styles/pause_theme.json")

        self.title_label = UILabel(
            relative_rect=pygame.Rect((WIDTH // 2) - 220, 45, 440, 40),
            text="Choose Your Character",
            manager=self.manager,
        )

        self.selected_label = UILabel(
            relative_rect=pygame.Rect((WIDTH // 2) - 180, 88, 360, 30),
            text=f"Selected: {self.selected_character}",
            manager=self.manager,
        )

        self.container_panel = UIPanel(
            relative_rect=pygame.Rect(40, 130, WIDTH - 80, HEIGHT - 260),
            starting_height=1,
            manager=self.manager,
        )

        card_width = 180
        card_height = 210
        spacing = 40
        start_x = 50
        card_y = 50

        self.character_buttons = {}
        names = CHARACTERS.keys()
        for index, name in enumerate(names):
            button = UIButton(
                relative_rect=pygame.Rect(start_x + index * (card_width + spacing), card_y, card_width, card_height),
                text=name,
                manager=self.manager,
                container=self.container_panel,
            )
            self.character_buttons[name] = button

        self.start_button = UIButton(
            relative_rect=pygame.Rect(WIDTH - 200, HEIGHT - 100, 160, 56),
            text="Battle",
            manager=self.manager,
        )

        self._refresh_character_button_texts()


    def get_selected_character(self):
        return self.selected_character


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
        self.manager.update(dt)

    
    def render(self) -> None:
        self.window.fill((15, 33, 40))

        self.manager.draw_ui(self.window)
        pygame.display.update()