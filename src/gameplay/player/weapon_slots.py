import math
import pygame
from config import FONT, LVL_TEXT_COLOR


class WeaponSlots:
    def __init__(self, max_slots: int = 2, icon_size: int = 34):
        self.max_slots = max_slots
        self.icon_size = icon_size
        self.weapons: list[str] = []
        self.weapon_icons: dict[str, pygame.Surface] = {}
        self.slot_background = pygame.Surface((icon_size + 10, icon_size + 10), pygame.SRCALPHA)
        pygame.draw.rect(self.slot_background, (30, 30, 30), self.slot_background.get_rect(), border_radius=6)
        pygame.draw.rect(self.slot_background, (180, 180, 180), self.slot_background.get_rect(), 2, border_radius=6)
        self.active_slot_background = pygame.Surface((icon_size + 10, icon_size + 10), pygame.SRCALPHA)
        pygame.draw.rect(self.active_slot_background, (40, 35, 25), self.active_slot_background.get_rect(), border_radius=6)
        pygame.draw.rect(self.active_slot_background, (210, 190, 120), self.active_slot_background.get_rect(), 2, border_radius=6)
        self.active_icon_cache: dict[str, pygame.Surface] = {}


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


    def _get_active_icon(self, active_item: object) -> pygame.Surface:
        item_id = getattr(active_item, "item_id", None)
        if not item_id:
            return pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        if item_id not in self.active_icon_cache:
            icon = pygame.transform.smoothscale(active_item.icon, (self.icon_size, self.icon_size))
            self.active_icon_cache[item_id] = icon
        return self.active_icon_cache[item_id]


    def draw(self, surface: pygame.Surface, active_item: object = None, active_item_label: str = "SPACE") -> None:
        slot_size = self.slot_background.get_width()
        gap = 8
        y = 30

        total_slots = self.max_slots + 1
        total_width = total_slots * slot_size + (total_slots - 1) * gap
        x = surface.get_width() - total_width - 20

        active_rect = pygame.Rect(x, y, slot_size, slot_size)
        surface.blit(self.active_slot_background, active_rect.topleft)
        if active_item is not None:
            icon = self._get_active_icon(active_item)
            icon_rect = icon.get_rect(center=active_rect.center)
            surface.blit(icon, icon_rect.topleft)

            cooldown_total = float(getattr(active_item, "cooldown_total", 0.0) or 0.0)
            cooldown_timer = float(getattr(active_item, "cooldown_timer", 0.0) or 0.0)
            if cooldown_total > 0.0 and cooldown_timer > 0.0:
                ratio = max(0.0, min(1.0, cooldown_timer / cooldown_total))
                overlay_height = int(active_rect.height * ratio)
                overlay_rect = pygame.Rect(active_rect.left, active_rect.bottom - overlay_height, active_rect.width, overlay_height)
                overlay = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                surface.blit(overlay, overlay_rect.topleft)

                cd_font = pygame.font.Font(FONT, 16)
                cd_text = cd_font.render(str(int(math.ceil(cooldown_timer))), True, (230, 230, 230))
                cd_rect = cd_text.get_rect(center=active_rect.center)
                surface.blit(cd_text, cd_rect.topleft)

        if active_item_label:
            label_font = pygame.font.Font(FONT, 12)
            label_text = label_font.render(active_item_label, True, LVL_TEXT_COLOR)
            label_rect = label_text.get_rect(bottomright=(active_rect.right - 4, active_rect.bottom - 2))
            surface.blit(label_text, label_rect.topleft)

        for i in range(self.max_slots):
            slot_rect = pygame.Rect(x + (i + 1) * (slot_size + gap), y, slot_size, slot_size)
            surface.blit(self.slot_background, slot_rect.topleft)

            if i < len(self.weapons):
                weapon_name = self.weapons[i]
                icon = self.weapon_icons[weapon_name]
                icon_rect = icon.get_rect(center=slot_rect.center)
                surface.blit(icon, icon_rect.topleft)
