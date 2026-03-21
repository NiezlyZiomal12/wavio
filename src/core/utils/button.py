import pygame


class Button:
    def __init__(
        self,
        rect: pygame.Rect,
        text: str = "",
        font: pygame.font.Font | None = None,
        on_click=None,
        image: pygame.Surface | None = None,
        bg_color: tuple[int, int, int] = (70, 70, 70),
        hover_color: tuple[int, int, int] = (95, 95, 95),
        text_color: tuple[int, int, int] = (255, 255, 255),
        border_color: tuple[int, int, int] = (200, 200, 200),
        border_width: int = 2,
        border_radius: int = 8,
        image_scale_to_button: bool = True,
        enabled: bool = True,
        visible: bool = True,
    ):
        self.rect = rect
        self.text = text
        self.font = font or pygame.font.Font(None, 24)
        self.on_click = on_click
        self.image = image

        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius
        self.image_scale_to_button = image_scale_to_button

        self.enabled = enabled
        self.visible = visible
        self.hovered = False
        self._pressed = False


    def set_text(self, text: str) -> None:
        self.text = text


    def set_image(self, image: pygame.Surface | None) -> None:
        self.image = image


    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled


    def update(self, mouse_pos: tuple[int, int] | None = None) -> None:
        if not self.visible:
            self.hovered = False
            return

        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.enabled and self.rect.collidepoint(mouse_pos)


    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.update(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._pressed = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            clicked = self._pressed and self.rect.collidepoint(event.pos)
            self._pressed = False
            if clicked:
                if self.on_click is not None:
                    self.on_click(self)
                return True

        return False


    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        if self.image is not None:
            if self.image_scale_to_button:
                image_surface = pygame.transform.smoothscale(self.image, self.rect.size)
                image_rect = self.rect
            else:
                image_surface = self.image
                image_rect = image_surface.get_rect(center=self.rect.center)
            surface.blit(image_surface, image_rect)
        else:
            fill_color = self.hover_color if self.hovered else self.bg_color
            pygame.draw.rect(surface, fill_color, self.rect, border_radius=self.border_radius)

        if self.border_width > 0:
            pygame.draw.rect(
                surface,
                self.border_color,
                self.rect,
                self.border_width,
                border_radius=self.border_radius,
            )

        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)