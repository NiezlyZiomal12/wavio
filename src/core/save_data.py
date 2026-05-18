import json
import os
from datetime import datetime


DEFAULT_DATA = {
    "version": 1,
    "completions": [],
}


def _default_save_path() -> str:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_dir, "save_data.json")


class SaveDataStore:
    def __init__(self, path: str | None = None) -> None:
        self.path = path or _default_save_path()
        self.data = {
            "version": DEFAULT_DATA["version"],
            "completions": [],
        }
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

        completions = parsed.get("completions")
        if isinstance(completions, list):
            self.data["completions"] = [item for item in completions if isinstance(item, dict)]

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(self.data, handle, indent=2)

    def _normalize(self, value: str) -> str:
        return value.strip()

    def _matches(self, entry: dict, level_id: str, difficulty: str, character: str) -> bool:
        return (
            entry.get("level_id") == level_id
            and entry.get("difficulty") == difficulty
            and entry.get("character") == character
        )

    def is_completed(self, level_id: str, difficulty: str, character: str) -> bool:
        level_id = self._normalize(level_id)
        difficulty = self._normalize(difficulty)
        character = self._normalize(character)
        return any(self._matches(entry, level_id, difficulty, character) for entry in self.data["completions"])

    def mark_completion(self, level_id: str, difficulty: str, character: str) -> None:
        level_id = self._normalize(level_id)
        difficulty = self._normalize(difficulty)
        character = self._normalize(character)

        if self.is_completed(level_id, difficulty, character):
            return

        self.data["completions"].append(
            {
                "level_id": level_id,
                "difficulty": difficulty,
                "character": character,
                "completed_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            }
        )
        self.save()

    def get_completions(self) -> list[dict]:
        return list(self.data["completions"])
