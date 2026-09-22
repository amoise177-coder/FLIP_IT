import pygame
from core.settings import Settings
from core.managers.asset_manager import AssetManager
from core.managers.sound_player import SoundPlayer
from ui.screens import BootScreen, MainMenu, StartScreen, TestGameScreen
from engine import Engine


class Launcher:
    """Controla la interfaz del launcher y el cambio entre pantallas."""

    def __init__(self, found_games, games_path):
        # Inicializa Pygame y prepara el entorno visual del launcher.
        pygame.init()

        if pygame.mixer.get_init():
            pygame.mixer.stop()
            pygame.mixer.music.stop()

        pygame.display.set_caption(Settings.TITLE)
        self.screen = pygame.display.set_mode((Settings.S_WIDTH, Settings.S_HEIGHT))
        self.clock = pygame.time.Clock()

        # Carga recursos globales y portadas de los juegos detectados.
        AssetManager.load_all_assets()
        AssetManager.load_game_covers(found_games)

        # Reproduce la música del menú al iniciar.
        self.menu_music_path = SoundPlayer.play_music()

        # Guarda el catálogo de juegos y la ruta base de la carpeta games.
        self.games_list = found_games
        self.GAMES_FOLDER = games_path

        # El motor es el responsable de lanzar cada juego de forma independiente.
        self.engine = Engine(self.GAMES_FOLDER)

        # Registra las pantallas del launcher.
        self.screens = {
            "BOOT": BootScreen(),
            "START": StartScreen(),
            "MAIN_MENU": MainMenu(self.games_list),
            "TEST_GAME": TestGameScreen(),
        }

        self.current_state = "START"
        self.running = True

    def handle_events(self):
        """Recoge eventos de Pygame y los delega a la pantalla activa."""
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return

        result = self.screens[self.current_state].handle_events(events)
        if result:
            self._process_screen_result(result)

    def _process_screen_result(self, result):
        """Convierte las respuestas de una pantalla en cambios de estado o acciones."""
        if result == "QUIT":
            self.running = False
        elif isinstance(result, dict) and result.get("action") == "LAUNCH":
            self._request_game_start(result.get("game_data"))
        elif result in self.screens:
            self.current_state = result

    def update(self, dt):
        """Actualiza la pantalla activa y reacciona a resultados de transición."""
        result = self.screens[self.current_state].update(dt)

        if result:
            if result == "QUIT":
                self.running = False
            elif isinstance(result, dict) and result.get("action") == "LAUNCH":
                self._request_game_start(result.get("game_data"))
            elif result in self.screens:
                self.current_state = result

    def _request_game_start(self, game_data):
        """Solicita al motor lanzar un juego y vuelve al menú cuando finaliza."""
        self.engine.launch_game(game_data)

        # Al regresar del juego, se limpia el audio y se restablece la interfaz.
        if pygame.mixer.get_init():
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        SoundPlayer.stop_all()
        pygame.mouse.set_visible(True)

        self.current_state = "MAIN_MENU"
        self.screen = pygame.display.set_mode((Settings.S_WIDTH, Settings.S_HEIGHT))
        pygame.display.set_caption(Settings.TITLE)
        if self.menu_music_path:
            SoundPlayer.play_music(self.menu_music_path)
        else:
            SoundPlayer.play_music()

    def draw(self):
        """Dibuja la pantalla actual en la ventana principal."""
        self.screens[self.current_state].draw(self.screen)
        pygame.display.flip()

    def run(self):
        """Bucle principal del launcher."""
        while self.running:
            dt = self.clock.tick(Settings.FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
