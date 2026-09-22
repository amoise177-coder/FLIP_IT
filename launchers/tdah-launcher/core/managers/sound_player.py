import os
import random
from typing import Optional

import pygame

from core.settings import Settings


class SoundPlayer:
    @staticmethod
    def _ensure_mixer() -> bool:
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except pygame.error:
                return False
        return True

    @staticmethod
    def stop_all() -> None:
        if pygame.mixer.get_init():
            pygame.mixer.stop()
            pygame.mixer.music.stop()

    @staticmethod
    def play_music(track_path: Optional[str] = None) -> Optional[str]:
        if not SoundPlayer._ensure_mixer():
            return None

        if track_path is None or track_path == "menu":
            available_tracks = [path for path in Settings.MUSIC_FILES if os.path.exists(path)]
            if not available_tracks:
                return None
            track_path = random.choice(available_tracks)

        if not os.path.exists(track_path):
            return None

        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play(-1)
            return track_path
        except Exception:
            return None

    @staticmethod
    def play_sound(sound) -> None:
        if not SoundPlayer._ensure_mixer():
            return
        sound.play()
