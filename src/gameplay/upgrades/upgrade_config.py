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
    
}