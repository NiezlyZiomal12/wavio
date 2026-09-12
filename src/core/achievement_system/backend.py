"""
Backend interface for achievement persistence/reporting.

The whole point of this abstraction is that `AchievementManager` never talks
to a file or to Steam directly - it only talks to whatever object implements
`AchievementBackend`. Today that's `LocalJsonAchievementBackend`. When you're
ready for Steam, you write a `SteamAchievementBackend` that implements the
same three methods and wraps the Steamworks SDK calls, then swap it in with
one line at startup. Nothing else in the game needs to change.

Steam mapping (for when you get there):
    - is_unlocked(id)  -> SteamUserStats().GetAchievement(id)
    - unlock(id)       -> SteamUserStats().SetAchievement(id); StoreStats()
    - get_unlocked()   -> iterate your known achievement ids and check GetAchievement

Because of that mapping, achievement ids here should be short, stable,
UPPER_SNAKE_CASE strings (e.g. "WIN_FOREST_WARRIOR") - these are exactly the
"API Name" strings you'd register for each achievement in the Steamworks
dashboard, so keeping them stable now means zero renaming work later.
"""

from abc import ABC, abstractmethod


class AchievementBackend(ABC):
    @abstractmethod
    def is_unlocked(self, achievement_id: str) -> bool:
        """Return True if this achievement has already been unlocked."""
        raise NotImplementedError

    @abstractmethod
    def unlock(self, achievement_id: str) -> bool:
        """
        Unlock an achievement.

        Returns True if this call is what newly unlocked it (i.e. it was
        locked before), False if it was already unlocked (no-op). Callers
        use this return value to decide whether to show a "achievement
        unlocked" popup.
        """
        raise NotImplementedError

    @abstractmethod
    def get_unlocked(self) -> set[str]:
        """Return the set of every currently-unlocked achievement id."""
        raise NotImplementedError