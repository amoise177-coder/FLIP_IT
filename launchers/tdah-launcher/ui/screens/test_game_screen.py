import pygame

from core.managers.asset_manager import AssetManager
from core.settings import Settings
from ui.visuals import COLORS, get_font, make_background


class TestGameScreen:
    """Pantalla falsa para probar la selección de un juego y su sonido."""

    def __init__(self) -> None:
        self.background = make_background()
        self.title_font = get_font(64)
        self.instruction_font = get_font(26)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "MAIN_MENU"
        return None

    def update(self, dt):
        return None

    def draw(self, screen: pygame.Surface) -> None:
        test_background = AssetManager.get_asset("selection_background")
        screen.blit(test_background if test_background else self.background, (0, 0))

        overlay = pygame.Surface((Settings.S_WIDTH, Settings.S_HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 18, 42, 120))
        screen.blit(overlay, (0, 0))

        title = self.title_font.render("JUEGO DE PRUEBA", True, COLORS["text"])
        screen.blit(title, title.get_rect(center=(Settings.S_WIDTH // 2, 300)))

        instruction = self.instruction_font.render("Presiona ESC para salir", True, COLORS["muted"])
        screen.blit(instruction, instruction.get_rect(center=(Settings.S_WIDTH // 2, 390)))
