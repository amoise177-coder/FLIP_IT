import os
import sys
import pygame
import subprocess


class Engine:
    """Responsable de lanzar cada juego en un proceso independiente."""

    def __init__(self, games_path):
        # Ruta base donde se ubican las carpetas de los juegos.
        self.GAMES_FOLDER = games_path

    def launch_game(self, game_data):
        """
        Detiene temporalmente la interfaz del launcher, lanza el juego elegido
        y luego reinicia el entorno del launcher cuando el juego termina.
        """
        folder = game_data["folder"]
        title = game_data["title"]

        # Construye la ruta completa al archivo main.py del juego.
        main_path = os.path.join(self.GAMES_FOLDER, folder, "main.py")
        working_directory = os.path.dirname(main_path)

        print(f"Apagando el launcher para inicializar el juego '{title}'")

        # Pausa la música y cierra la ventana del launcher para dejar espacio al juego.
        if pygame.mixer.get_init():
            pygame.mixer.music.pause()

        pygame.display.quit()

        try:
            # El juego se ejecuta como subproceso independiente.
            self._invoke_game_subprocess(main_path, working_directory)
            return True
        except Exception as e:
            print(f"Error crítico de sistema al ejecutar subproceso: {e}")
            return False
        finally:
            print(f"Reinicializando el launcher")

            pygame.display.init()

            if pygame.mixer.get_init():
                pygame.mixer.music.unpause()

            # Limpia eventos pendientes para evitar que el retorno del juego genere acciones extrañas.
            pygame.event.clear()

    def _invoke_game_subprocess(self, main_path, working_directory):
        """Ejecuta el juego solicitado en un subproceso separado."""
        subprocess.run(
            [sys.executable, main_path],
            cwd=working_directory
        )
            