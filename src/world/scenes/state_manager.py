import pygame

from config import WIDTH, HEIGHT, FPS
from .start_menu import StartMenuScene
from .game_scene import GameScene
from .character_select_scene import Character_select_scene
from .levels.level_select_scene import Level_select_scene
from src.core.shaders import ShaderRenderer


class StateManager:
    def __init__(self):
        pygame.init()
        self.info = pygame.display.Info()
        self.scr_w = self.info.current_w
        self.scr_h = self.info.current_h

        # ── OpenGL context (required for shaders) ─────────────────────────
        self.window = pygame.display.set_mode(
            (self.scr_w, self.scr_h),
            pygame.FULLSCREEN | pygame.OPENGL | pygame.DOUBLEBUF,
        )

        self.screen = pygame.Surface((self.scr_w, self.scr_h))

        # Post-processing renderer
        self.shader = ShaderRenderer(self.scr_w, self.scr_h)
        # ─────────────────────────────────────────────────────────────────

        pygame.display.set_caption("Wavio")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"
        self.elapsed = 0.0

        self.menu = StartMenuScene(self.screen)
        self.character_select_scene = Character_select_scene(self.screen)
        self.level_select_scene = Level_select_scene(self.screen)
        self.game = None

    def _present(self) -> None:
        """Upload the software surface through the shader and flip."""
        self.shader.blit(self.screen, self.elapsed)
        pygame.display.flip()


    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.elapsed += dt
            events = pygame.event.get()

            if self.state == "menu":
                self.menu.handle_events(events)
                if not self.menu.running:
                    self.running = False
                    break

                self.menu.update(dt)
                self.menu.render()
                self._present()                 # ← replaces pygame.display.update()

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
                self._present()

                if self.character_select_scene.start_game:
                    self.state = "level_select_scene"
                continue

            if self.state == "level_select_scene":
                self.level_select_scene.handle_events(events)
                if not self.level_select_scene.running:
                    self.running = False
                    break

                self.level_select_scene.update(dt)
                self.level_select_scene.render()
                self._present()

                if self.level_select_scene.start_game:
                    self.game = GameScene(
                        self.screen,                                          # ← screen, not window
                        self.character_select_scene.get_selected_character(),
                        self.level_select_scene.get_selected_level(),
                        self.level_select_scene.get_selected_difficulty(),
                    )
                    self.state = "game"
                continue

            if self.state == "game":
                if self.game is None:
                    self.game = GameScene(
                        self.screen,                                          # ← screen, not window
                        self.character_select_scene.get_selected_character(),
                        self.level_select_scene.get_selected_level(),
                        self.level_select_scene.get_selected_difficulty(),
                    )

                self.game.handle_events(events)
                if not self.game.running:
                    self.running = False
                    break

                self.game.update(dt)
                self.game.render()
                self._present()

        self.shader.destroy()
        pygame.quit()