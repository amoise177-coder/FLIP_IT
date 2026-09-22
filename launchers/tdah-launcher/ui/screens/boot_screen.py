import pygame
from core.settings import Settings


class BootScreen:
    def __init__(self) -> None:
        self.counter = 0

    def handle_events(self, events):
        pass

    def update(self, dt):
        self.counter += dt
        if self.counter > 1.5:
            return "MAIN_MENU"
        return None

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(Settings.BACKGROUND_COLOR)
        font = pygame.font.Font(None, 48)
        text = font.render("Cargando V-Sports...", True, Settings.HIGHLIGHT_COLOR)
        screen.blit(text, (Settings.S_WIDTH // 2 - text.get_width() // 2, Settings.S_HEIGHT // 2 - text.get_height() // 2))
