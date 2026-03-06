from dataclasses import dataclass


@dataclass
class ShopItem:
    item_id: str
    name: str
    category: str
    price: int
    max_level: int
    evolution_to: str | None
    description: str


def build_weapon_shop_items(weapon_config: dict) -> list[ShopItem]:
    items: list[ShopItem] = []

    for weapon_name, config in weapon_config.items():
        shop_data = config.get("shop")
        price = int(shop_data.get("price"))
        max_level = int(shop_data.get("max_level"))
        evolution_to = shop_data.get("evolution_to")
        weapon_type = config.get("type")
        damage = config.get("damage")
        cooldown = config.get("cooldown")

        items.append(
            ShopItem(
                item_id=weapon_name,
                name=weapon_name,
                category="weapon",
                price=price,
                max_level=max_level,
                evolution_to=evolution_to,
                description=f"{weapon_type} | dmg {damage} | cd {cooldown}s",
            )
        )

    return items
