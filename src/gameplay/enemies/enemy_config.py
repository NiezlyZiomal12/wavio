ENEMY_CONFIG = {
    "slime": {
        "class": "Slime",
        "speed": 30,
        "hp": 10,
        "damage": 10,
        "Dropable" : {
            "xp": 5,
            "coin": 5,
        },
        "Animation" : {
            "sprite_width": 64,
            "sprite_height": 50,
            "idle_row": 0,
            "idle_frames": 8,
            "idle_speed": 0.05,
            "death_row": 2,
            "death_frames": 5,
            "death_speed": 0.1,
            "spawn_duration": 1.0,
            "dead_duration": 0.5
        },

    },
    "zombie": {
        "class": "Zombie", 
        "speed": 20,
        "hp": 15,
        "damage": 20,
        "Dropable" : {
            "xp": 7,
            "coin": 7,
        },
        "Animation" : {
            "sprite_width": 64,
            "sprite_height": 64,
            "idle_row": 1,
            "idle_frames": 8,
            "idle_speed": 0.2,
            "death_row": 4,
            "death_frames": 6,
            "death_speed": 0.1,
            "spawn_duration": 1.0,
            "dead_duration": 0.5
        },
    },
    "bat" : {
        "class": "Bat", 
        "speed": 35,
        "hp": 10,
        "damage": 15,
        "Dropable" : {
            "xp": 10,
            "coin": 10,
        },
        "Animation" : {
            "sprite_width": 64,
            "sprite_height": 64,
            "idle_row": 1,
            "idle_frames": 4,
            "idle_speed": 0.1,
            "death_row": 2,
            "death_frames": 4,
            "death_speed": 0.1,
            "spawn_duration": 1.0,
            "dead_duration": 0.5
        },
    },
}