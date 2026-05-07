"""
item_applier.py
---------------
Applies shop item effects to the player.

Items fall into two tiers:

  STAT items  – driven purely by the effect dict in SHOP_ITEMS_CONFIG.
                Keys map directly to player attributes via STAT_MAP.

  PASSIVE items – have special/conditional logic that cannot be expressed
                  as a flat stat delta.  Each gets its own apply_* function
                  AND a corresponding runtime hook that other systems call
                  (e.g. on_hit, on_damage_dealt, on_level_up …).
"""

# ---------------------------------------------------------------------------
# STAT MAP  –  effect-dict key → player attribute that gets modified
# ---------------------------------------------------------------------------
# Values are (attribute_name, mode)
#   mode "add"  → player.attr += value
#   mode "mult" → player.attr *= (1 + value / 100)   (value is a %)
#
STAT_MAP: dict[str, tuple[str, str]] = {
    "damage":     ("damage",          "add"),
    "damage_pct": ("dmg_mult",        "mult"),
    "hp":         ("max_health",      "add"),
    "hp_pct":     ("hp_mult",         "mult"),
    "speed":      ("speed",           "add"),
    "speed_pct":  ("speed_mult",      "mult"),
    "armor":      ("armor",           "add"),
    "armor_pct":  ("armor_mult",      "mult"),
    "crit":       ("crit_chance",     "add"),
    "luck":       ("luck",            "add"),
    "lifesteal":  ("lifesteal",       "add"),
    "cdr":        ("reduce_cooldown", "add"),
    "pickup":     ("pickup_range",    "add"),
    "xp_gain":    ("xp_gain",         "add"),
    "coin_gain":  ("coin_gain",       "add"),
}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def apply_shop_item_effects(player: "Player", item_id: str, levels_gained: int = 1) -> None:
    """
    Called by player.buy_shop_item() every time the item is purchased / upgraded.
    `levels_gained` is almost always 1; pass a higher value only for bulk init.
    """
    handler = _ITEM_HANDLERS.get(item_id)
    if handler:
        for _ in range(levels_gained):
            handler(player)


# ---------------------------------------------------------------------------
# Generic helper used by simple stat items
# ---------------------------------------------------------------------------

def _apply_stat_effect(player: "Player", effect: dict) -> None:
    """Apply a flat effect dict to the player using STAT_MAP rules."""
    for key, value in effect.items():
        mapping = STAT_MAP.get(key)
        attr, mode = mapping
        if mode == "add":
            setattr(player, attr, getattr(player, attr) + value)
        elif mode == "mult":
            setattr(player, attr, getattr(player, attr) * (1 + value / 100))
            
# ---------------------------------------------------------------------------
# Per-item handlers
# ---------------------------------------------------------------------------

# ── Assassin's Robe ──────────────────────────────────────────────────────────
# +20 % damage, -10 % max HP (applied per level purchased)

def _apply_assasins_robe(player: "Player") -> None:
    player.dmg_mult   *= 1.20
    player.max_health *= 0.90
    player.current_health = min(player.current_health, player.max_health)


# ── Bloodbath ────────────────────────────────────────────────────────────────
# +1 % lifesteal for every 5 points of base damage the player has AT BUY TIME.
# Re-evaluated on each level purchase, so buying it twice gives diminishing
# returns if damage hasn't grown.

def _apply_bloodbath(player: "Player") -> None:
    bonus = (player.damage // 5) * 1.0
    player.lifesteal += bonus


# ── Blood Glyph ──────────────────────────────────────────────────────────────
# Permanently sacrifices 10 max HP in exchange for +10 % damage multiplier.

def _apply_blood_glyph(player: "Player") -> None:
    player.max_health -= 10
    player.max_health  = max(10, player.max_health)
    player.current_health = min(player.current_health, player.max_health)
    player.dmg_mult += 0.10


# ── Heavy Armor ──────────────────────────────────────────────────────────────
# +10 armor, -5 speed.
# Bonus damage = 1 for every full percent of speed that's been sacrificed

def _apply_heavy_armor(player: "Player") -> None:
    if not hasattr(player, "heavy_armor_levels"):
        player.heavy_armor_levels = 0

    player.armor  +=  10 * player.armor_mult
    player.armor = min(player.max_armor, player.armor)
    player.speed  -= 5 * player.speed_mult
    player.speed = max(1, player.speed)

    player.heavy_armor_levels += 1
    # Each level: the 5 % speed penalty translates into +1 flat damage.
    # Recalculate from scratch to avoid drift.
    player.damage = _base_stat(player, "damage") + player.heavy_armor_levels


def _base_stat(player: "Player", stat: str) -> int:
    """Return the base value of a stat before heavy_armor stacking."""
    return getattr(player, f"_base_{stat}", getattr(player, stat))


# ── Lucky Coin ───────────────────────────────────────────────────────────────
# +3 luck.  Crit chance = base_crit + luck * 0.5  (recomputed after every buy).

def _apply_lucky_coin(player: "Player") -> None:

    player.luck += 3
    player.crit_chance += player.luck / 2 * player.crit_mult
    player.crit_chance = min(100, player.crit_chance)


# ── Spider's Venom ───────────────────────────────────────────────────────────
# Unlocks poison on hit.  Each level adds one poison stack on hit.
# The actual damage-over-time is applied by the combat system via
# player.poison_stacks_per_hit.

def _apply_spiders_venom(player: "Player") -> None:
    if not hasattr(player, "poison_stacks_per_hit"):
        player.poison_stacks_per_hit = 0
        player.poison_damage   = 2       # dmg per tick
        player.poison_duration = 3.0     # seconds
        player.poison_tick_rate = 0.5    # seconds between ticks

    player.poison_stacks_per_hit += 1


# ── Time Amulet ──────────────────────────────────────────────────────────────
# +10 CDR per level.  +5 % movement speed for each 5 % CDR accumulated.

def _apply_time_amulet(player: "Player") -> None:
    added_cdr = 10 * player.cd_mult
    player.reduce_cooldown += added_cdr
    player.reduce_cooldown = min(player.max_cd, player.reduce_cooldown)
    player.speed += added_cdr * player.speed_mult / 20
    player.speed = min(player.max_speed, player.speed)

# ---------------------------------------------------------------------------
# Runtime HOOKS  (call these from combat / pickup code, not from buy logic)
# ---------------------------------------------------------------------------

def on_hit(player: "Player", target, damage_dealt: float) -> None:
    """
    Call this whenever the player's projectile hits an enemy.
    Handles: lifesteal, poison application.
    """
    # Lifesteal
    if player.lifesteal > 0:
        heal = damage_dealt * (player.lifesteal / 100)
        player.current_health = min(player.max_health, player.current_health + heal)

    # Poison
    if getattr(player, "poison_stacks_per_hit", 0) > 0:
        if hasattr(target, "apply_poison"):
            target.apply_poison(
                stacks      = player.poison_stacks_per_hit,
                damage      = player.poison_damage,
                duration    = player.poison_duration,
                tick_rate   = player.poison_tick_rate,
            )


def on_kill(player: "Player", enemy) -> None:
    """
    Call this when an enemy dies.
    Placeholder – add kill-triggered item logic here later.
    """
    pass


# ---------------------------------------------------------------------------
# Handler registry  –  add new item IDs here
# ---------------------------------------------------------------------------

_ITEM_HANDLERS: dict[str, callable] = {
    "Assasins_robe":   _apply_assasins_robe,
    "Bloodbath":       _apply_bloodbath,
    "Blood_glyph":     _apply_blood_glyph,
    "Heavy_armor":     _apply_heavy_armor,
    "Lucky_coin":      _apply_lucky_coin,
    "Spiders_venom":   _apply_spiders_venom,
    "Time_amulet":     _apply_time_amulet,
}