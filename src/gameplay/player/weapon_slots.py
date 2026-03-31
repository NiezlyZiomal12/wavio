import pygame


class WeaponSlots:
    def __init__(self, max_slots: int = 2, icon_size: int = 34):
        self.max_slots = max_slots
        self.icon_size = icon_size
        self.weapons: list[str] = []
        self.weapon_icons: dict[str, pygame.Surface] = {}
        self.slot_background = pygame.Surface((icon_size + 10, icon_size + 10), pygame.SRCALPHA)
        pygame.draw.rect(self.slot_background, (30, 30, 30), self.slot_background.get_rect(), border_radius=6)
        pygame.draw.rect(self.slot_background, (180, 180, 180), self.slot_background.get_rect(), 2, border_radius=6)


    def _build_weapon_icon(self, config: dict) -> pygame.Surface:
        width = config["animation"]["sprite_width"]
        height = config["animation"]["sprite_height"]
        row = config["animation"]["start_row"]
        sprite_sheet = pygame.image.load(config["sprite_path"]).convert_alpha()
        frame_rect = pygame.Rect(0, row * height, width, height)

        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        frame.blit(sprite_sheet, (0, 0), frame_rect)
        return pygame.transform.smoothscale(frame, (self.icon_size, self.icon_size))


    def can_add_weapon(self, weapon_name: str) -> bool:
        if weapon_name in self.weapons:
            return False
        return len(self.weapons) < self.max_slots


    def add_weapon(self, weapon_name: str, config: dict) -> bool:
        if not self.can_add_weapon(weapon_name):
            return False

        self.weapons.append(weapon_name)
        self.weapon_icons[weapon_name] = self._build_weapon_icon(config)
        return True


    def get_weapons(self) -> list[str]:
        return list(self.weapons)


    def draw(self, surface: pygame.Surface) -> None:
        slot_size = self.slot_background.get_width()
        gap = 8
        y = 30

        total_width = self.max_slots * slot_size + (self.max_slots - 1) * gap
        x = surface.get_width() - total_width - 20

        for i in range(self.max_slots):
            slot_rect = pygame.Rect(x + i * (slot_size + gap), y, slot_size, slot_size)
            surface.blit(self.slot_background, slot_rect.topleft)

            if i < len(self.weapons):
                weapon_name = self.weapons[i]
                icon = self.weapon_icons[weapon_name]
                icon_rect = icon.get_rect(center=slot_rect.center)
                surface.blit(icon, icon_rect.topleft)
