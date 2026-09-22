import pygame

from core.managers.sound_player import SoundPlayer
from core.settings import Settings
from core.managers.asset_manager import AssetManager
from ui.visuals import make_background


class StartScreen:
    def __init__(self) -> None:
        self.background = make_background()
        self.start_sound = self._load_sound("SOUND_START", "assets/sounds/start.wav")

    def _load_sound(self, settings_key, default_path):
        path = getattr(Settings, settings_key, default_path)
        try:
            return pygame.mixer.Sound(path) if path else None
        except (pygame.error, FileNotFoundError):
            return None

    def _play_sound(self, sound):
        SoundPlayer.play_sound(sound)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._play_sound(self.start_sound)
                return "MAIN_MENU"
        return None

    def update(self, dt):
        return None

    def draw(self, screen: pygame.Surface) -> None:
        start_background = AssetManager.get_asset("start_background")
        if start_background:
            screen.blit(start_background, (0, 0))
        else:
            screen.blit(self.background, (0, 0))

