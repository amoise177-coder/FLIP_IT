import os
import sys

from core.managers.game_scanner import GameScanner
from launcher import Launcher


def main():
    """Punto de entrada principal del launcher."""
    try:
        # Se establece la ruta raíz del proyecto para que los módulos trabajen con rutas consistentes.
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        os.chdir(ROOT_DIR)
        if ROOT_DIR not in sys.path:
            sys.path.insert(0, ROOT_DIR)

        print("Iniciando Launcher...")

        # Se analiza la carpeta de juegos para construir el catálogo visible en el menú.
        games_folder = os.path.join(ROOT_DIR, "games")
        found_games = GameScanner.scan_and_load_metadata(games_folder)

        # Se instancia el launcher con el catálogo y la ruta base de los juegos.
        launcher = Launcher(found_games=found_games, games_path=games_folder)
        launcher.run()

    except Exception as e:
        import traceback

        print(f"Error crítico: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
