
CHARACTERS = {
    "Warrior" : {
        "Starting_weapon" : "Sword",
        "Stats" : {
            "max_health" : 120,
            "damage" : 2,
            "armor" : 0.05,
            "speed" : 3
        },
        "Passive" : {
            "hp_mult" : 1.5,
            "armor_mult" : 1.5,
        }

    },
    "Mage" : {
        "Starting_weapon" : "Fireball",
        "Stats" : {
            "max_health" : 80,
            "reduce_cooldown" : 20,
            "projectile_count": 2
        },
        "Passive": {
            "cd_mult" : 1.5,
            "dmg_mult" : 1.5
        }

    },
    "Rogue" : {
        "Starting_weapon" : "Meteor",
        "Stats" : {
            "max_health" : 80,
            "speed" : 7,
            "crit_chance" : 20
        },
        "Passive" : {
            "speed_mult" : 1.5,
            "crit_mult" : 1.5
        }
    },
    "SoulCollector" : {
        "Starting_weapon" : "Typhoon",
        "Stats" : {
            "max_health" : 80,
            "speed" : 5,
            "pickup_range" : 2,
            "damage" : 0.5,
        },
        "Passive" : {
            "xp_gain_mult" : 1.5,
            "xp_damage_per_point" : 0.001,
            "item_stat_mult" : 0.5,
        }
    }

}