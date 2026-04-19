import audioop
import pygame


def build_random_pitch_sounds(
    path: str,
    volume: float = 0.22,
    pitch_offsets: tuple[float, ...] = (0.97, 1.03),
) -> list[pygame.mixer.Sound]:
    """Build a small list of pitch-varied sounds from one source file."""
    base = pygame.mixer.Sound(path)
    clamped_volume = max(0.0, min(1.0, volume))
    base.set_volume(clamped_volume)

    mixer_info = pygame.mixer.get_init()
    if mixer_info is None:
        return [base]

    frequency, fmt, channels = mixer_info
    sample_width = abs(fmt) // 8
    raw = base.get_raw()
    sounds = [base]

    for pitch in pitch_offsets:
        try:
            target_rate = max(1000, int(frequency / pitch))
            shifted_raw, _ = audioop.ratecv(raw, sample_width, channels, frequency, target_rate, None)
            shifted = pygame.mixer.Sound(buffer=shifted_raw)
            shifted.set_volume(clamped_volume)
            sounds.append(shifted)
        except (pygame.error, audioop.error, ValueError, ZeroDivisionError):
            continue

    return sounds
