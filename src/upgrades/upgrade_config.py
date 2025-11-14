import pygame

UPGRADE_CONFIG = {
    "Order": {
        "name" : "Order",
        "description" : "5%' increased damage",
        "image" : pygame.image.load("src/assets/upgrades/order.png").convert_alpha(),
        "effect" : " ",
    },
    "Boots": {
        "name" : "Boots",
        "description": "5'%' increased movement speed",
        "image" : pygame.image.load("src/assets/upgrades/boots.png").convert_alpha(),
        "effect" : "",
    },
    "Heart": {
        "name" : "Heart",
        "description" : "5%' increased max hp",
        "image" : pygame.image.load("src/assets/upgrades/heart.png").convert_alpha(),
        "effect" : " ",
    },
    "Armor": {
        "name" : "Armor",
        "description": "5'%' increased armor",
        "image" : pygame.image.load("src/assets/upgrades/armor.png").convert_alpha(),
        "effect" : "",
    },
    "Pearl": {
        "name" : "Pearl",
        "description" : "Add one projectile per weapon",
        "image" : pygame.image.load("src/assets/upgrades/pearl.png").convert_alpha(),
        "effect" : " ",
    },
    "Scroll": {
        "name" : "Scroll",
        "description": "5'%' increased cooldown reduction",
        "image" : pygame.image.load("src/assets/upgrades/scroll.png").convert_alpha(),
        "effect" : "",
    },
    
}