import os
import random
import pygame


class SoundtrackManager:
    SUPPORTED_EXT = (".mp3")

    def __init__(self, menu_dir="src/assets/soundtracks/menu", game_dir="src/assets/soundtracks/game", volume=1):
        self.menu_dir = menu_dir
        self.game_dir = game_dir
        self.volume = volume

        pygame.mixer.init()

        self.disabled = False
        self.MUSIC_END = pygame.event.custom_type()
        pygame.mixer.music.set_endevent(self.MUSIC_END)
        pygame.mixer.music.set_volume(self.volume)

        self.playlists = {
            "menu": self._scan_dir(self.menu_dir),
            "game": self._scan_dir(self.game_dir),
        }

        self._indices = {"menu": [], "game": []}
        self._current = {"menu": None, "game": None}
        self._kind = None

        # prepare orders
        for k in self.playlists:
            self._reset_order(k)

    def _scan_dir(self, d):
        if not os.path.isdir(d):
            return []
        files = []
        for fn in os.listdir(d):
            if fn.startswith("."):
                continue
            if os.path.splitext(fn)[1].lower() in self.SUPPORTED_EXT:
                files.append(os.path.join(d, fn))
        return files

    def _reset_order(self, kind):
        tracks = list(self.playlists.get(kind, []))
        random.shuffle(tracks)
        self._indices[kind] = tracks

    def start_playlist(self, kind: str):
        if self.disabled:
            return
        if kind not in self.playlists:
            return
        if self._kind == kind:
            if pygame.mixer.music.get_busy():
                return
        self._kind = kind
        if not self._indices[kind]:
            self._reset_order(kind)
        self.next_track()

    def stop(self):
        if self.disabled:
            return
        pygame.mixer.music.stop()
        self._kind = None

    def next_track(self):
        if self.disabled:
            return
        if not self._kind:
            return
        order = self._indices.get(self._kind, [])
        if not order:
            return
        track = order.pop(0)
        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.play()
            self._current[self._kind] = track
        except Exception:
            # skip on error and try next
            if order:
                self.next_track()
            else:
                # exhausted, reset and stop
                self._reset_order(self._kind)

    def handle_music_end_event(self, event):
        if self.disabled:
            return False
        if event.type == self.MUSIC_END:
            self.next_track()
            return True
        return False
