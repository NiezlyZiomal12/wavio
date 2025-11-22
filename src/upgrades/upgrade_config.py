import pygame

UPGRADE_CONFIG = {
    "Order": {
        "name" : "Order",
        "description" : "5% increased damage",
        "image" : "src/assets/upgrades/order.png",
        "effect" : {"damage": 0.05},
    },
    "Boots": {
        "name" : "Boots",
        "description": "5% increased movement speed",
        "image" : "src/assets/upgrades/boots.png",
        "effect" : {"speed": 0.05},
    },
    "Heart": {
        "name" : "Heart",
        "description" : "5% increased max hp",
        "image" : "src/assets/upgrades/heart.png",
        "effect" : {"max_health" : 0.05},
    },
    "Armor": {
        "name" : "Armor",
        "description": "5% increased armor",
        "image" : "src/assets/upgrades/armor.png",
        "effect" : {"armor" : 0.05},
    },
    "Pearl": {
        "name" : "Pearl",
        "description" : "Add one projectile per weapon",
        "image" : "src/assets/upgrades/pearl.png",
        "effect" : {"projectile_count" : 1},
    },
    "Scroll": {
        "name" : "Scroll",
        "description": "5% increased cooldown reduction",
        "image" : "src/assets/upgrades/scroll.png",
        "effect" : {"reduce_cooldown" : 0.05},
    },
    
}