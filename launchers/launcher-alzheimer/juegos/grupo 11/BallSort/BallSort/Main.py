import sys
import pygame
from pathlib import Path
from menu import Menu
from gameLoop import GameLoop

class GameApp:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except Exception:
            pass
        
        self.WIDTH = 1280
        self.HEIGHT = 720
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Ball Sort - Puzzle")

        self.base_path = Path(__file__).resolve().parent
        icon_path = self.base_path / "assets" / "iconolauncher.png"
        if icon_path.exists():
            try:
                icon_surf = pygame.image.load(str(icon_path))
                pygame.display.set_icon(icon_surf)
            except Exception:
                pass
        
        self.clock = pygame.time.Clock()
        self.menu = Menu(self.screen, self.base_path)
        self.game_loop = GameLoop(self.screen, self.WIDTH, self.HEIGHT)
        self.state = "MENU"

    def run(self):
        while True:
            if self.state == "MENU":
                menu_result = self.menu.run(self.clock)
                if menu_result == "PLAY":
                    self.state = "GAME"
                elif menu_result == "EXIT":
                    self.close_app()

            elif self.state == "GAME":
                event_res = self.game_loop.handleEvents()
                if event_res == "GO_MENU":
                    self.state = "MENU"
                elif event_res == "EXIT_GAME":
                    self.close_app()
                else:
                    update_res = self.game_loop.update()
                    if update_res == "GO_MENU":
                        self.state = "MENU"

                self.clock.tick(60)

    def close_app(self):
        """Cierre seguro de la aplicación."""
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = GameApp()
    app.run()