import pygame

from config import WIDTH, HEIGHT, FPS
from .start_menu import StartMenuScene
from .game_scene import GameScene
from .character_select_scene import Character_select_scene


class StateManager:
    def __init__(self):
        pygame.init()
        self.info = pygame.display.Info()
        self.window = pygame.display.set_mode((self.info.current_w, self.info.current_h), pygame.FULLSCREEN)
        # self.window = pygame.display.set_mode((WIDTH, HEIGHT))

        pygame.display.set_caption("Wavio")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"

        self.menu = StartMenuScene(self.window)
        self.character_select_scene = Character_select_scene(self.window)
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
                    self.state = "character_select_scene"
                continue

            if self.state == "character_select_scene":
                self.character_select_scene.handle_events(events)
                if not self.character_select_scene.running:
                    self.running = False
                    break
                
                self.character_select_scene.update(dt)
                self.character_select_scene.render()

                if self.character_select_scene.start_game:
                    self.game = GameScene(
                        self.window,
                        self.character_select_scene.get_selected_character()
                    )
                    self.state = "game"
                continue

            if self.state == "game":
                if self.game is None:
                    self.game = GameScene(self.window)

                self.game.handle_events(events)
                if not self.game.running:
                    self.running = False
                    break

                self.game.update(dt)
                self.game.render()

        pygame.quit()