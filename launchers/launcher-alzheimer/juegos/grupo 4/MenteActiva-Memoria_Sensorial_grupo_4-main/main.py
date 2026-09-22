"""
MenteActiva — Punto de Entrada
Juego de memoria sensorial para estimulación cognitiva.

Este archivo inicializa Pygame, crea la ventana del juego y ejecuta
el loop principal. Es compatible con el launcher del proyecto:
se ejecuta como proceso independiente con `python main.py`.
"""
import sys
import os

# Asegurar que el directorio del juego esté en el path
_game_dir = os.path.dirname(os.path.abspath(__file__))
if _game_dir not in sys.path:
    sys.path.insert(0, _game_dir)

import pygame

from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE, ScreenName
from core.gestor_sensorial import GestorSensorial
from core.game_manager import GameManager
from ui.pantalla_menu import PantallaMenu
from ui.pantalla_juego import PantallaJuego
from ui.pantalla_victoria import PantallaVictoria
from ui.renderer import reset_cursor


class MenteActivaApp:
    """
    Aplicación principal del juego MenteActiva.
    Gestiona el ciclo de vida de Pygame, las transiciones de pantalla
    y el loop principal de eventos.
    """

    def __init__(self):
        # ── Inicialización de Pygame ──
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        pygame.mixer.init()

        # ── Ventana ──
        self._screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)

        # ── Reloj ──
        self._clock = pygame.time.Clock()
        self._running = True

        # ── Gestor Sensorial (compartido entre pantallas) ──
        self._gestor_sensorial = GestorSensorial()
        self._gestor_sensorial.inicializar()

        # ── Pantallas ──
        self._pantalla_actual = None
        self._screen_name = None

        # ── Datos de partida (para repetir/transiciones) ──
        self._last_game_config = None

        # Empezar en el menú
        self._cambiar_pantalla(ScreenName.MENU)

    def _cambiar_pantalla(self, screen_name, data=None):
        """
        Cambia la pantalla activa.

        Args:
            screen_name (ScreenName): Pantalla destino.
            data: Datos opcionales para la nueva pantalla.
        """
        self._screen_name = screen_name
        reset_cursor()

        if screen_name == ScreenName.MENU:
            self._pantalla_actual = PantallaMenu()
            # Música de menú
            self._gestor_sensorial.reproducir_musica_menu()

        elif screen_name == ScreenName.GAME:
            if data == "repetir" and self._last_game_config:
                # Repetir la misma configuración
                cfg = self._last_game_config
            elif isinstance(data, dict):
                cfg = data
                self._last_game_config = cfg
            else:
                # Fallback
                from config import DifficultyLevel
                cfg = {
                    "dificultad": DifficultyLevel.EASY,
                    "tema": "naturaleza",
                }
                self._last_game_config = cfg

            gm = GameManager(
                dificultad=cfg["dificultad"],
                tema=cfg["tema"],
                gestor_sensorial=self._gestor_sensorial,
            )
            self._pantalla_actual = PantallaJuego(gm)
            # Música de juego
            self._gestor_sensorial.reproducir_musica_juego()

        elif screen_name == ScreenName.VICTORY:
            self._pantalla_actual = PantallaVictoria(data)
            # Mantener la música del juego durante victoria
            # (la fanfarria suena por encima)

        elif screen_name == ScreenName.QUIT:
            self._running = False
            return

    def run(self):
        """Loop principal del juego."""
        while self._running:
            dt = self._clock.tick(FPS) / 1000.0  # delta time en segundos
            dt = min(dt, 0.05)  # Limitar para evitar saltos grandes

            # ── Eventos ──
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                    break

                # Delegar al pantalla actual
                if self._pantalla_actual:
                    result = self._pantalla_actual.handle_event(event)
                    if result:
                        screen_name, data = result
                        self._cambiar_pantalla(screen_name, data)

            if not self._running:
                break

            # ── Update ──
            if self._pantalla_actual:
                result = self._pantalla_actual.update(dt)
                if result:
                    screen_name, data = result
                    self._cambiar_pantalla(screen_name, data)

            # ── Draw ──
            if self._pantalla_actual:
                self._pantalla_actual.draw(self._screen)

            pygame.display.flip()

        # ── Cleanup ──
        self._gestor_sensorial.detener_todo()
        pygame.quit()
        sys.exit()


def main():
    """Función principal — punto de entrada."""
    app = MenteActivaApp()
    app.run()


if __name__ == "__main__":
    main()
