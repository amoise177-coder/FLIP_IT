import os
import sys

import pygame

from audio_manager import GestorAudio
from launcher_service import Launcher
from renderer import Renderer
from settings import ALTO, ANCHO, FPS
from states import StateManager

MODO_CAPTURAS = "--capturas" in sys.argv
if MODO_CAPTURAS:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def ejecutar():
    pygame.init()

    pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
    pygame.display.set_caption("Abre Tu Mente")
    reloj = pygame.time.Clock()

    # Módulo de audio especializado (alta cohesión)
    audio = GestorAudio(volumen=0.25)
    audio.reproducir_musica_fondo()

    # Servicio del Launcher para lanzar y gestionar juegos
    launcher = Launcher()

    renderer = Renderer(pantalla)
    state_manager = StateManager(renderer, launcher=launcher, audio=audio)

    tiempo = 0.0
    ejecutando = True

    while ejecutando:
        dt = reloj.tick(FPS) / 1000.0
        tiempo += dt

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    # ESC vuelve al menú si estamos en selección, si no cierra
                    if not state_manager.manejar_tecla(evento.key):
                        ejecutando = False
                else:
                    state_manager.manejar_tecla(evento.key)
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                state_manager.manejar_click(evento.pos)

        state_manager.actualizar(dt)
        state_manager.dibujar(pantalla, tiempo, pygame.mouse.get_pos())
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    ejecutar()
