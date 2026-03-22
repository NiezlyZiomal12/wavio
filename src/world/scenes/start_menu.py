import pygame
import pygame_gui
from pygame_gui.elements import UIButton

from config import WIDTH, HEIGHT


class StartMenuScene:
    def __init__(self, window: pygame.Surface):
        self.window = window
        self.running = True
        self.start_requested = False

        self.manager = pygame_gui.UIManager((WIDTH, HEIGHT))

        self.start_button = UIButton(
            relative_rect=pygame.Rect((WIDTH // 2) - 130, (HEIGHT // 2) - 200, 260, 64),
            text="Start Game",
            manager=self.manager,
        )


    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            self.manager.process_events(event)

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.start_button:
                self.start_requested = True


    def update(self, dt: float) -> None:
        self.manager.update(dt)


    def render(self) -> None:
        self.window.fill((15, 33, 40))
        self.manager.draw_ui(self.window)
        pygame.display.update()
