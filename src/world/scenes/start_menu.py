import pygame
import pygame_gui
from pygame_gui.elements import UIButton


class StartMenuScene:
    def __init__(self, window: pygame.Surface):
        self.window = window
        self.running = True
        self.start_requested = False

        self.current_size = self.window.get_size()
        self.manager = pygame_gui.UIManager(self.current_size)

        self.start_button = UIButton(
            relative_rect=pygame.Rect(0, 0, 260, 64),
            text="Start Game",
            manager=self.manager,
        )
        self._responsive_ui()


    def _responsive_ui(self) -> None:
        width, height = self.current_size
        button_width = max(200, min(360, int(width * 0.32)))
        button_height = max(52, min(72, int(height * 0.1)))

        x = (width - button_width) // 2
        y = int(height * 0.45) - (button_height // 2)

        self.start_button.set_dimensions((button_width, button_height))
        self.start_button.set_relative_position((x, y))


    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.VIDEORESIZE:
                self.current_size = (event.w, event.h)
                self.manager.set_window_resolution(self.current_size)
                self._responsive_ui()

            self.manager.process_events(event)

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.start_button:
                self.start_requested = True


    def update(self, dt: float) -> None:
        new_size = self.window.get_size()
        if new_size != self.current_size:
            self.current_size = new_size
            self.manager.set_window_resolution(self.current_size)
            self._responsive_ui()

        self.manager.update(dt)


    def render(self) -> None:
        self.window.fill((15, 33, 40))
        self.manager.draw_ui(self.window)
        pygame.display.update()
