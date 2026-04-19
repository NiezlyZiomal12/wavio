import pygame
import pygame_gui
from pygame_gui.elements import UIButton


class StartMenuScene:
    def __init__(self, window: pygame.Surface):
        self.window = window
        self.running = True
        self.start_requested = False

        # Pixel-style fade-in state
        self.fade_time = 0.0
        self.fade_duration = 1.15
        self.ui_revealed = False

        self.current_size = self.window.get_size()
        self.manager = pygame_gui.UIManager(self.current_size, theme_path="src/assets/pygame_gui_styles/pause_theme.json")

        self.click_sound = pygame.mixer.Sound("src/assets/sounds/gui/click.wav")

        self.background = pygame.image.load("src/assets/ui/mainBackground.png").convert()
        self.background_image = pygame.transform.scale(self.background, self.current_size)

        self.start_button = UIButton(
            relative_rect=pygame.Rect(0, 0, 260, 64),
            text="Start Game",
            manager=self.manager,
            object_id="#button",
        )
        self.start_button.hide()
        self._responsive_ui()


    def _responsive_ui(self) -> None:
        width, height = self.current_size
        button_width = max(200, min(360, int(width * 0.32)))
        button_height = max(52, min(72, int(height * 0.1)))

        x = (width - button_width) // 2
        y = int(height * 0.45) - (button_height // 2)

        self.start_button.set_dimensions((button_width, button_height))
        self.start_button.set_relative_position((x, y))
        self.background_image = pygame.transform.scale(self.background, self.current_size)


    def _draw_pixel_fade_overlay(self) -> None:
        if self.fade_time >= self.fade_duration:
            return

        width, height = self.current_size
        progress = min(1.0, self.fade_time / self.fade_duration)

        # A tiny global fade keeps the first frames from looking too harsh.
        global_alpha = int(140 * (1.0 - progress) ** 1.1)
        if global_alpha > 0:
            shade = pygame.Surface((width, height), pygame.SRCALPHA)
            shade.fill((0, 0, 0, global_alpha))
            self.window.blit(shade, (0, 0))

        # Deterministic tiled reveal for a retro "pixel dissolve" look.
        tile_size = max(6, min(18, int(min(width, height) * 0.015)))
        for y in range(0, height, tile_size):
            cell_y = y // tile_size
            for x in range(0, width, tile_size):
                cell_x = x // tile_size

                # Stable pseudo-random threshold based on tile coordinates.
                hashed = (cell_x * 73856093) ^ (cell_y * 19349663)
                threshold = (hashed % 1000) / 1000.0
                if threshold > progress:
                    pygame.draw.rect(self.window, (0, 0, 0), (x, y, tile_size, tile_size))


    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.VIDEORESIZE:
                self.current_size = (event.w, event.h)
                self.manager.set_window_resolution(self.current_size)
                self._responsive_ui()

            self.manager.process_events(event)

            if not self.ui_revealed:
                continue

            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.start_button:
                self.click_sound.play()
                self.start_requested = True


    def update(self, dt: float) -> None:
        new_size = self.window.get_size()
        if new_size != self.current_size:
            self.current_size = new_size
            self.manager.set_window_resolution(self.current_size)
            self._responsive_ui()

        self.fade_time = min(self.fade_duration, self.fade_time + dt)
        if not self.ui_revealed and self.fade_time >= self.fade_duration:
            self.ui_revealed = True
            self.start_button.show()

        self.manager.update(dt)


    def render(self) -> None:
        self.window.blit(self.background_image, (0,0))
        self._draw_pixel_fade_overlay()
        self.manager.draw_ui(self.window)
        pygame.display.update()
