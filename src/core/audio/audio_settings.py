import json
import os
import pygame
import weakref


_DEFAULT_MUSIC_VOLUME = 0.7
_DEFAULT_SFX_VOLUME = 0.8

_music_volume = _DEFAULT_MUSIC_VOLUME
_sfx_volume = _DEFAULT_SFX_VOLUME
_sfx_registry: list[tuple[object, float]] = []


def _default_settings_path() -> str:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    return os.path.join(base_dir, "settings_data.json")


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def get_music_volume() -> float:
    return _music_volume


def get_sfx_volume() -> float:
    return _sfx_volume


def set_music_volume(value: float) -> None:
    global _music_volume
    _music_volume = _clamp(value)
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(_music_volume)


def set_sfx_volume(value: float) -> None:
    global _sfx_volume
    _sfx_volume = _clamp(value)
    if not pygame.mixer.get_init():
        return
    channel_count = pygame.mixer.get_num_channels()
    for channel_index in range(channel_count):
        pygame.mixer.Channel(channel_index).set_volume(_sfx_volume)
    _reapply_registered_sfx()


def apply_all() -> None:
    set_music_volume(_music_volume)
    set_sfx_volume(_sfx_volume)


def load_settings(path: str | None = None) -> None:
    global _music_volume, _sfx_volume
    settings_path = path or _default_settings_path()
    if not os.path.exists(settings_path):
        return

    try:
        with open(settings_path, "r", encoding="utf-8") as handle:
            parsed = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return

    if not isinstance(parsed, dict):
        return

    music_value = parsed.get("music_volume")
    sfx_value = parsed.get("sfx_volume")

    if isinstance(music_value, (int, float)):
        _music_volume = _clamp(music_value)
    if isinstance(sfx_value, (int, float)):
        _sfx_volume = _clamp(sfx_value)


def save_settings(path: str | None = None) -> None:
    settings_path = path or _default_settings_path()
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    payload = {
        "music_volume": _music_volume,
        "sfx_volume": _sfx_volume,
    }
    with open(settings_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def apply_sfx_volume(sound: pygame.mixer.Sound, base_volume: float = 1.0) -> pygame.mixer.Sound:
    _register_sfx_sound(sound, base_volume)
    sound.set_volume(_clamp(base_volume) * _sfx_volume)
    return sound


def _register_sfx_sound(sound: pygame.mixer.Sound, base_volume: float) -> None:
    try:
        _sfx_registry.append((weakref.ref(sound), base_volume))
    except TypeError:
        _sfx_registry.append((sound, base_volume))


def _reapply_registered_sfx() -> None:
    if not _sfx_registry:
        return
    refreshed: list[tuple[object, float]] = []
    for entry, base_volume in _sfx_registry:
        if isinstance(entry, weakref.ReferenceType):
            sound = entry()
            if sound is None:
                continue
            refreshed.append((entry, base_volume))
        else:
            sound = entry
            refreshed.append((entry, base_volume))
        sound.set_volume(_clamp(base_volume) * _sfx_volume)
    _sfx_registry[:] = refreshed
