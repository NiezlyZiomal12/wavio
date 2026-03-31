from dataclasses import dataclass

@dataclass
class EquippedWeapon:
    name: str
    weapon_class: type
    cooldown_timer: float = 0.0
    level: int = 1

    def tick(self, dt: float) -> None:
        self.cooldown_timer -= dt

    def ready(self) -> bool:
        return self.cooldown_timer <= 0.0

    def trigger_cooldown(self, cooldown: float) -> None:
        self.cooldown_timer = cooldown

    def can_upgrade(self, max_level: int) -> bool:
        return self.level < max_level

    def upgrade(self) -> None:
        self.level += 1
