
SHOP_ITEMS_CONFIG = {
    # ── Simple stat items ────────────────────────────────────────────────────
    # effect dict is used directly by _apply_stat_effect in item_applier.py

    "Assasins_robe": {
        "name": "Assassin's Robe",
        "description": "+20% damage, -10% max HP",
        "image": "src/assets/items/upgrades/shop_items/assasins_robe.png",
        "effect": {"damage_pct": 20, "hp_pct": -10},
        "cost": 40,
        "max_level": 3,
    },

    # ── Passive / conditional items ──────────────────────────────────────────
    # effect is empty – logic handled in item_applier.py

    "Bloodbath": {
        "name": "Bloodbath",
        "description": "+1% lifesteal per 5 base damage",
        "image": "src/assets/items/upgrades/shop_items/bloodbath.png",
        "effect": {},
        "cost": 40,
        "max_level": 3,
    },
    "Blood_glyph": {
        "name": "Blood Glyph",
        "description": "-10 max HP → +10% damage",
        "image": "src/assets/items/upgrades/shop_items/blood_glyph.png",
        "effect": {},
        "cost": 40,
        "max_level": 5,
    },
    "Heavy_armor": {
        "name": "Heavy Armor",
        "description": "+10% armor, -5% speed; bonus damage scales with speed lost",
        "image": "src/assets/items/upgrades/shop_items/heavy_armor.png",
        "effect": {},
        "cost": 40,
        "max_level": 5,
    },
    "Lucky_coin": {
        "name": "Lucky Coin",
        "description": "+3 luck; crit chance scales with luck",
        "image": "src/assets/items/upgrades/shop_items/lucky_coin.png",
        "effect": {},
        "cost": 40,
        "max_level": 5,
    },
    "Spiders_venom": {
        "name": "Spider's Venom",
        "description": "Attacks apply poison (damage over time); stacks per level",
        "image": "src/assets/items/upgrades/shop_items/spiders_venom.png",
        "effect": {},
        "cost": 40,
        "max_level": 5,
    },
    "Time_amulet": {
        "name": "Time Amulet",
        "description": "+10% CDR; +5% move speed per 5% CDR accumulated",
        "image": "src/assets/items/upgrades/shop_items/time_amulet.png",
        "effect": {},
        "cost": 40,
        "max_level": 5,
    },
}