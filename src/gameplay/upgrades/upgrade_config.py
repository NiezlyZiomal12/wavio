import pygame

UPGRADE_CONFIG = {
    "Order": {
        "name" : "Order",
        "description" : "+1 damage",
        "image" : "src/assets/items/upgrades/order.png",
        "effect" : {"damage": 1},
        "max_level": 5,
    },
    "Boots": {
        "name" : "Boots",
        "description": "+1 movement speed",
        "image" : "src/assets/items/upgrades/boots.png",
        "effect" : {"speed": 1},
        "max_level": 5,
    },
    "Heart": {
        "name" : "Heart",
        "description" : "+20 max hp",
        "image" : "src/assets/items/upgrades/heart.png",
        "effect" : {"max_health" : 20},
        "max_level": 5,
    },
    "Armor": {
        "name" : "Armor",
        "description": "+5% armor",
        "image" : "src/assets/items/upgrades/armor.png",
        "effect" : {"armor" : 0.05},
        "max_level": 5,
    },
    "Pearl": {
        "name" : "Pearl",
        "description" : "Add one projectile per weapon",
        "image" : "src/assets/items/upgrades/pearl.png",
        "effect" : {"projectile_count" : 1},
        "max_level": 5,
    },
    "Scroll": {
        "name" : "Scroll",
        "description": "+5% cooldown reduction",
        "image" : "src/assets/items/upgrades/scroll.png",
        "effect" : {"reduce_cooldown" : 0.05},
        "max_level": 5,
    },
    "Nightstar": {
        "name" : "Nightstar",
        "description": "+5% xp gain",
        "image" : "src/assets/items/upgrades/nightstar.png",
        "effect" : {"xp_gain" : 0.05},
        "max_level": 5,
    },
    "Goldfish": {
        "name" : "Goldfish",
        "description": "+1 luck",
        "image" : "src/assets/items/upgrades/goldfish.png",
        "effect" : {"luck" : 1},
        "max_level": 5,
    },
    "Greed's eye": {
        "name" : "Greed's eye",
        "description": "+5% coin gain",
        "image" : "src/assets/items/upgrades/greeds_eye.png",
        "effect" : {"coin_gain" : 0.05},
        "max_level": 5,
    },
    "Sharpener": {
        "name" : "Sharpener",
        "description": "+5% crit chance",
        "image" : "src/assets/items/upgrades/sharpener.png",
        "effect" : {"crit_chance" : 0.05},
        "max_level": 10,
    },
    "Bloody_sword": {
        "name" : "Bloody sword",
        "description": "+5% lifesteal",
        "image" : "src/assets/items/upgrades/bloody_sword.png",
        "effect" : {"lifesteal" : 0.05},
        "max_level": 10,
    },
    
}