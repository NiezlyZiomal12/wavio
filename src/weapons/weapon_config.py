WEAPON_CONFIG = {
    "Fireball" : {
        "type" : "ranged",
        "damage" : 5,
        "speed" : 300,
        "cooldown" : 1.0,
        "projectile_count" : 2,
        "animation" : {
            "sprite_width" : 51,
            "sprite_height": 32,
            "start_row" : 0,
            "start_frames": 4,
            "animation_speed" : 0.1,
        },
        "special" : {
            "lifetime" : 3.0,
        },
        "shop": {
            "price": 10,
            "max_level": 5,
            "evolution_to": None,
        },
    },
    "Sword" : {
        "type" : "mele",
        "damage" : 3,
        "cooldown" : 1,
        "speed" : 0,
        "projectile_count" : 3,
        "animation" : {
            "sprite_height": 64,
            "start_row" : 0,
            "start_frames": 3,
            "animation_speed" : 0.1,
            "sprite_width" : 64,
        },
        "special" : {
            "attack_duration" : 0.3,
            "attack_radius" : 80,
        },
        "shop": {
            "price": 10,
            "max_level": 5,
            "evolution_to": None,
        },
    },
    "Boomerang" : {
        "type" : "ranged",
        "damage" : 2,
        "speed" : 400,
        "cooldown" : 1.5,
        "projectile_count" : 3,
        "animation" : {
            "sprite_width" : 32,
            "sprite_height": 32,
            "start_row" : 0,
            "start_frames": 4,
            "animation_speed" : 0.05,
        },
        "special" : {
            "pierce_count" : 3,
            "return_speed" : 450,
            "lifetime" : 1.3,
        },
        "shop": {
            "price": 10,
            "max_level": 5,
            "evolution_to": None,
        },
    },
}