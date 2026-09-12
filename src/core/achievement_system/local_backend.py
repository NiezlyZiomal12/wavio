import json
import os

from .backend import AchievementBackend


def _default_path() -> str:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    return os.path.join(base_dir, "achievements_data.json")


class LocalJsonAchievementBackend(AchievementBackend):
    """
    Stores unlocked achievement ids in a small local JSON file.

    This is the backend used for offline/non-Steam builds (and for
    development). Kept deliberately dumb: a version number, a list of
    unlocked ids, and nothing else.
    """

    def __init__(self, path: str | None = None) -> None:
        self.path = path or _default_path()
        self._unlocked: set[str] = set()
        self.load()

    def load(self) -> None:
        if not os.path.exists(self.path):
            return

        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                parsed = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return

        if not isinstance(parsed, dict):
            return

        unlocked = parsed.get("unlocked")
        if isinstance(unlocked, list):
            self._unlocked = {item for item in unlocked if isinstance(item, str)}

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump({"version": 1, "unlocked": sorted(self._unlocked)}, handle, indent=2)

    def is_unlocked(self, achievement_id: str) -> bool:
        return achievement_id in self._unlocked

    def unlock(self, achievement_id: str) -> bool:
        if achievement_id in self._unlocked:
            return False
        self._unlocked.add(achievement_id)
        self.save()
        return True

    def get_unlocked(self) -> set[str]:
        return set(self._unlocked)