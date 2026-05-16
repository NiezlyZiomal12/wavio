import pygame
import weakref


_DEFAULT_MUSIC_VOLUME = 0.7
_DEFAULT_SFX_VOLUME = 0.8

_music_volume = _DEFAULT_MUSIC_VOLUME
_sfx_volume = _DEFAULT_SFX_VOLUME
_sfx_registry: list[tuple[object, float]] = []


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
