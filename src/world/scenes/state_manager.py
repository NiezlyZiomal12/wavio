import pygame

from config import WIDTH, HEIGHT, FPS
from .start_menu import StartMenuScene
from .game_scene import GameScene


class StateManager:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Wavio")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"

        self.menu = StartMenuScene(self.window)
        self.game = None

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            events = pygame.event.get()

            if self.state == "menu":
                self.menu.handle_events(events)
                if not self.menu.running:
                    self.running = False
                    break

                self.menu.update(dt)
                self.menu.render()

                if self.menu.start_requested:
                    self.game = GameScene(self.window)
                    self.state = "game"
                continue

            if self.state == "game" and self.game is not None:
                self.game.handle_events(events)
                if not self.game.running:
                    self.running = False
                    break

                self.game.update(dt)
                self.game.render()

        pygame.quit()