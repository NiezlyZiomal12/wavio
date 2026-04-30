from dataclasses import dataclass, field

import pygame


@dataclass(slots=True)
class ShopItem:
    item_id: str
    name: str
    category: str
    price: int
    description: str
    max_level: int = 1
    evolution_to: str | None = None
    icon_path: str | None = None
    effect: dict = field(default_factory=dict)

    def load_icon(self) -> pygame.Surface | None:
        if not self.icon_path:
            return None

        try:
            return pygame.image.load(self.icon_path).convert_alpha()
        except (pygame.error, FileNotFoundError):
            return None

    def is_maxed(self, current_level: int) -> bool:
        return current_level >= self.max_level

    @classmethod
    def from_weapon_config(cls, item_id: str, config: dict) -> "ShopItem":
        shop_data = config.get("shop", {})
        weapon_type = config.get("type")
        damage = config.get("damage")
        cooldown = config.get("cooldown")

        return cls(
            item_id=item_id,
            name=item_id,
            category="weapon",
            price=int(shop_data.get("price", 0)),
            max_level=int(shop_data.get("max_level", 1)),
            evolution_to=shop_data.get("evolution_to"),
            description=f"{weapon_type} | dmg {damage} | cd {cooldown}s",
            icon_path=config.get("sprite_path"),
        )

    @classmethod
    def from_shop_config(cls, item_id: str, config: dict) -> "ShopItem":
        return cls(
            item_id=item_id,
            name=config.get("name", item_id),
            category="shop_item",
            price=int(config.get("cost", 0)),
            max_level=int(config.get("max_level", 1)),
            description=config.get("description", ""),
            icon_path=config.get("image"),
            effect=dict(config.get("effect", {})),
        )