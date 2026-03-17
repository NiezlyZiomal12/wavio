import pygame

from src.utils import Button


class PauseMenuUi:
    def __init__(self, window, width: int, height: int):
        self.window = window
        self.width = width
        self.height = height
        self.active = False

        self.title_font = pygame.font.Font(None, 54)
        self.font = pygame.font.Font(None, 30)
        self.subtitle_font = pygame.font.Font(None, 24)

        self.popup_rect = pygame.Rect(0, 0, 720, 420)
        self.popup_rect.center = (width // 2, height // 2)

        self.left_panel = pygame.Rect(
            self.popup_rect.x + 28,
            self.popup_rect.y + 28,
            290,
            self.popup_rect.height - 56,
        )
        self.right_panel = pygame.Rect(
            self.left_panel.right + 22,
            self.popup_rect.y + 28,
            self.popup_rect.width - self.left_panel.width - 78,
            self.popup_rect.height - 56,
        )

        button_width = self.left_panel.width - 40
        button_height = 46
        start_y = self.left_panel.y + 108
        gap = 14

        common_button_kwargs = {
            "font": self.font,
            "on_click": None,
            "bg_color": (52, 62, 74),
            "hover_color": (76, 89, 104),
            "text_color": (245, 245, 245),
            "border_color": (175, 194, 217),
            "border_width": 2,
            "border_radius": 8,
        }

        self.resume_button = Button(
            rect=pygame.Rect(self.left_panel.x + 20, start_y, button_width, button_height),
            text="Resume",
            **common_button_kwargs,
        )
        self.restart_button = Button(
            rect=pygame.Rect(self.left_panel.x + 20, start_y + (button_height + gap), button_width, button_height),
            text="Restart",
            **common_button_kwargs,
        )
        self.options_button = Button(
            rect=pygame.Rect(self.left_panel.x + 20, start_y + 2 * (button_height + gap), button_width, button_height),
            text="Options",
            **common_button_kwargs,
        )
        self.menu_button = Button(
            rect=pygame.Rect(self.left_panel.x + 20, start_y + 3 * (button_height + gap), button_width, button_height),
            text="Menu",
            **common_button_kwargs,
        )

    def show(self) -> None:
        self.active = True

    def hide(self) -> None:
        self.active = False

    def toggle(self) -> None:
        self.active = not self.active

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.active:
            return

        self.resume_button.handle_event(event)
        self.restart_button.handle_event(event)
        self.options_button.handle_event(event)
        self.menu_button.handle_event(event)

    def update(self, dt: float) -> None:
        if not self.active:
            return

        self.resume_button.update()
        self.restart_button.update()
        self.options_button.update()
        self.menu_button.update()

    def draw(self) -> None:
        if not self.active:
            return

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((8, 12, 18, 175))
        self.window.blit(overlay, (0, 0))

        pygame.draw.rect(self.window, (28, 34, 44), self.popup_rect, border_radius=12)
        pygame.draw.rect(self.window, (156, 178, 205), self.popup_rect, 2, border_radius=12)

        pygame.draw.rect(self.window, (35, 43, 54), self.left_panel, border_radius=10)
        pygame.draw.rect(self.window, (128, 148, 170), self.left_panel, 1, border_radius=10)

        pygame.draw.rect(self.window, (25, 31, 40), self.right_panel, border_radius=10)
        pygame.draw.rect(self.window, (90, 108, 128), self.right_panel, 1, border_radius=10)

        title_surface = self.title_font.render("Paused", True, (240, 244, 250))
        self.window.blit(title_surface, (self.left_panel.x + 20, self.left_panel.y + 24))

        self.resume_button.draw(self.window)
        self.restart_button.draw(self.window)
        self.options_button.draw(self.window)
        self.menu_button.draw(self.window)

        stats_title = self.font.render("Stats Dashboard", True, (215, 225, 238))
        stats_hint = self.subtitle_font.render("Reserved area for future stats UI", True, (148, 164, 184))
        self.window.blit(stats_title, (self.right_panel.x + 16, self.right_panel.y + 16))
        self.window.blit(stats_hint, (self.right_panel.x + 16, self.right_panel.y + 46))