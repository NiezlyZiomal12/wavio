"""
Static achievement definitions.


Fields:
    name         Display name shown in the UI / toast.
    description  Display description shown in the UI / toast.
    character    Character required, or None for "any character".
    level_id     Level id required (matches `selected_level["id"]`), or None
                 for "any level".
    difficulty   Difficulty required ("Normal"/"Hard"/"Nightmare"), or None
                 for "any difficulty".
    hidden       If True, name/description are replaced with "???" in the
                 achievement list UI until unlocked. Good for secret/joke
                 achievements. Steam supports this natively too.

All three of character/level_id/difficulty act as an AND - e.g. an entry
with character="Warrior" and difficulty="Nightmare" and level_id=None
requires the Warrior to win ANY level on Nightmare.

Replace the level_id values below with your actual level ids once your
levels are finalized - these are just placeholders/examples.
"""

ACHIEVEMENTS: dict[str, dict] = {
    "FIRST_WIN": {
        "name": "First Blood",
        "description": "Win your first run, on any character, level, or difficulty.",
        "character": None,
        "level_id": None,
        "difficulty": None,
        "hidden": False,
    },
    "WIN_WARRIOR_ANY": {
        "name": "Steel and Steadfast",
        "description": "Win a run as the Warrior.",
        "character": "Warrior",
        "level_id": None,
        "difficulty": None,
        "hidden": False,
    },
    "WIN_MAGE_ANY": {
        "name": "Arcane Victory",
        "description": "Win a run as the Mage.",
        "character": "Mage",
        "level_id": None,
        "difficulty": None,
        "hidden": False,
    },
    "WIN_ROGUE_ANY": {
        "name": "Shadow's Triumph",
        "description": "Win a run as the Rogue.",
        "character": "Rogue",
        "level_id": None,
        "difficulty": None,
        "hidden": False,
    },
    "WIN_SOULCOLLECTOR_ANY": {
        "name": "Collector of Souls",
        "description": "Win a run as the Soul Collector.",
        "character": "SoulCollector",
        "level_id": None,
        "difficulty": None,
        "hidden": False,
    },
    "WIN_ANY_NIGHTMARE": {
        "name": "Nightmare Slayer",
        "description": "Win a run on Nightmare difficulty.",
        "character": None,
        "level_id": None,
        "difficulty": "Nightmare",
        "hidden": False,
    },
    "WIN_ALL_CHARACTERS": {
        "name": "Master of All Trades",
        "description": "Win a run with every character at least once.",
        "character": None,
        "level_id": None,
        "difficulty": None,
        "hidden": True,
        "composite": "all_characters",
    },
}

# Ids listed here are treated as "composite" achievements - they aren't
# unlocked directly from a single completion event, but derived from the
# full completion history each time a run is won. See
# AchievementManager._check_composites for how "all_characters" is
# evaluated.
ALL_CHARACTER_IDS = ["Warrior", "Mage", "Rogue", "SoulCollector"]