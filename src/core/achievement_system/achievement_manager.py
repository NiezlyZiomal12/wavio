from .backend import AchievementBackend
from .local_backend import LocalJsonAchievementBackend
from .achievement_config import ACHIEVEMENTS, ALL_CHARACTER_IDS


class AchievementManager:
    """
    Usage:
        ...
        newly_unlocked = achievements.check_level_completion(
            level_id, difficulty, character, save_data=self.save_data
        )
        for entry in newly_unlocked:
            toast_ui.push(entry)   # optional popup

    Swapping to Steam later is just:
        achievements = AchievementManager(backend=SteamAchievementBackend())
    Nothing else in the game needs to change, since GameScene only ever
    calls check_level_completion() / unlock() / is_unlocked() on this object.
    """

    def __init__(
        self,
        backend: AchievementBackend | None = None,
        definitions: dict | None = None,
    ) -> None:
        self.backend = backend or LocalJsonAchievementBackend()
        self.definitions = definitions or ACHIEVEMENTS
        self._listeners = []

    def on_unlock(self, callback) -> None:
        """Register a callback(achievement_id, definition_dict) for unlocks."""
        self._listeners.append(callback)

    def _notify(self, achievement_id: str, meta: dict) -> None:
        for callback in self._listeners:
            callback(achievement_id, meta)

    def is_unlocked(self, achievement_id: str) -> bool:
        return self.backend.is_unlocked(achievement_id)

    def unlock(self, achievement_id: str) -> dict | None:
        """
        Directly unlock an achievement by id (for non-level-completion
        triggers, e.g. "kill 1000 enemies" or "collect every weapon").
        Returns the definition dict if this call newly unlocked it, else None.
        """
        meta = self.definitions.get(achievement_id)
        if meta is None:
            return None
        if self.backend.unlock(achievement_id):
            self._notify(achievement_id, meta)
            return meta
        return None

    def check_level_completion(
        self,
        level_id: str,
        difficulty: str,
        character: str,
        save_data=None,
    ) -> list[dict]:
        """
        Call this once, right when a run is won. Evaluates every direct
        (non-composite) achievement definition against the run that was
        just completed, and unlocks any that match and aren't unlocked yet.

        `save_data` is optional - pass your SaveDataStore in if you want
        composite achievements (like "win with every character") to be
        evaluated too, since those need the full completion history rather
        than just this one run.

        Returns a list of {"id": ..., **definition} for every achievement
        newly unlocked by this call, in case you want to show popups.
        """
        newly_unlocked = []

        for achievement_id, meta in self.definitions.items():
            if meta.get("composite"):
                continue
            if self.backend.is_unlocked(achievement_id):
                continue
            if meta["character"] not in (None, character):
                continue
            if meta["level_id"] not in (None, level_id):
                continue
            if meta["difficulty"] not in (None, difficulty):
                continue

            if self.backend.unlock(achievement_id):
                entry = {"id": achievement_id, **meta}
                newly_unlocked.append(entry)
                self._notify(achievement_id, meta)

        if save_data is not None:
            newly_unlocked.extend(self._check_composites(save_data))

        return newly_unlocked

    def _check_composites(self, save_data) -> list[dict]:
        newly_unlocked = []
        completions = save_data.get_completions()
        won_characters = {entry.get("character") for entry in completions}

        for achievement_id, meta in self.definitions.items():
            if meta.get("composite") != "all_characters":
                continue
            if self.backend.is_unlocked(achievement_id):
                continue
            if won_characters.issuperset(ALL_CHARACTER_IDS):
                if self.backend.unlock(achievement_id):
                    entry = {"id": achievement_id, **meta}
                    newly_unlocked.append(entry)
                    self._notify(achievement_id, meta)

        return newly_unlocked

    def get_status_list(self) -> list[dict]:
        """
        For an in-game achievements/gallery screen: every achievement with
        its unlocked state, with hidden ones masked until unlocked.
        """
        status = []
        for achievement_id, meta in self.definitions.items():
            unlocked = self.backend.is_unlocked(achievement_id)
            if meta.get("hidden") and not unlocked:
                status.append(
                    {
                        "id": achievement_id,
                        "name": "???",
                        "description": "Hidden achievement",
                        "unlocked": False,
                    }
                )
            else:
                status.append(
                    {
                        "id": achievement_id,
                        "name": meta["name"],
                        "description": meta["description"],
                        "unlocked": unlocked,
                    }
                )
        return status