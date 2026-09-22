import os
import sys
import json
from pathlib import Path

_dir = str(Path(__file__).resolve().parent)
os.chdir(_dir)
if _dir not in sys.path:
    sys.path.insert(0, _dir)

import pygame

from Componentes.config import (
    Config,
    GAMEMETA_FILE,
    DEFAULT_GAMEMETA,
    CATEGORIAS_FILE
)
from Componentes.dictionary_checker import DictionaryChecker


class LetraALetraGame:
    """
    Clase principal que encapsula el ciclo de vida, preparación del entorno
    y ejecución autónoma del minijuego Letra a Letra.
    Garantiza que el launcher sea agnóstico y no requiera conocer la lógica interna.
    """

    def __init__(self) -> None:
        self._gamemeta_path: Path = GAMEMETA_FILE
        self._ui_manager = None

    def ensure_environment(self) -> None:
        """
        Verifica y genera dinámicamente con pathlib los archivos de configuración
        necesarios para el launcher (gamemeta.json) y el vocabulario del juego
        (assets/data/categorias.json) si no existen.
        """
        if not self._gamemeta_path.exists():
            try:
                with open(self._gamemeta_path, "w", encoding="utf-8") as f:
                    json.dump(DEFAULT_GAMEMETA, f, indent=4, ensure_ascii=False)
                print(f"[ENTORNO] Archivo '{self._gamemeta_path.name}' creado exitosamente para el launcher.")
            except Exception as err:
                print(f"[ERROR] No se pudo crear {self._gamemeta_path}: {err}")
        else:
            print(f"[ENTORNO] Archivo '{self._gamemeta_path.name}' verificado correctamente.")

        # El diccionario de categorías es indispensable: si falta, se regenera en
        # disco a partir del respaldo en memoria para que la selección de
        # categorías no quede desincronizada.
        DictionaryChecker.ensure_dictionary_file(CATEGORIAS_FILE)

    def run(self) -> None:
        """Inicializa Pygame, crea la ventana base (1280x720) y 
        arranca el ciclo de juego a 60 FPS."""
        self.ensure_environment()

        # 1. Inicialización explícita de Pygame y sus subsistemas
        pygame.init()
        pygame.font.init()

        # 2. Creación explícita de la ventana base a (1280x720)
        screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption(Config.WINDOW_TITLE)

        # 3. Importación desacoplada y arranque del ciclo de juego
        from Componentes.Ui import UIManager

        print(f"[INICIO] Ejecutando Letra a Letra a {Config.SCREEN_WIDTH}x{Config.SCREEN_HEIGHT} (60 FPS)...")
        self._ui_manager = UIManager(screen=screen)
        self._ui_manager.run()


def main() -> None:
    """Función de arranque estándar para el Launcher y ejecución autónoma."""
    game = LetraALetraGame()
    game.run()


if __name__ == "__main__":
    main()
