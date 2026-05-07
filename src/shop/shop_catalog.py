from src.gameplay.items.shop_upgrades.shop_item import ShopItem
from src.gameplay.items.shop_upgrades.shop_items_config import SHOP_ITEMS_CONFIG

def build_weapon_shop_items(weapon_config: dict) -> list[ShopItem]:
    items: list[ShopItem] = []

    for weapon_name, config in weapon_config.items():
        items.append(ShopItem.from_weapon_config(weapon_name, config))

    return items


def build_shop_items(weapon_config: dict, shop_item_config: dict | None = None) -> list[ShopItem]:
    items = build_weapon_shop_items(weapon_config)
    active_shop_config = shop_item_config or SHOP_ITEMS_CONFIG

    for item_id, config in active_shop_config.items():
        items.append(ShopItem.from_shop_config(item_id, config))

    return items
