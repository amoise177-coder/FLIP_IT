"""Punto de entrada del juego "¿Quién es quién?"."""

import os
import sys

RUTA_PROYECTO = os.path.dirname(os.path.abspath(__file__))
if RUTA_PROYECTO not in sys.path:
    sys.path.insert(0, RUTA_PROYECTO)

import pygame  # noqa: E402

from juego.configuracion import ALTO_VENTANA, ANCHO_VENTANA, TITULO_VENTANA  # noqa: E402
from juego.juego import Juego  # noqa: E402


def main():
    # Stereo permite conservar la calidad espacial de los assets de audio.
    # Los recursos recomendados para el proyecto deben estar a 44100 Hz y
    # 16 bits para minimizar conversiones del mixer.
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.init()

    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption(TITULO_VENTANA)

    juego = Juego(pantalla)
    juego.ejecutar()


if __name__ == "__main__":
    main()
