"""Punto de entrada del juego. Ejecutar con: python main.py"""
import os
import sys

_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_dir)
if _dir not in sys.path:
    sys.path.insert(0, _dir)

import pygame
from app import GameApp


if __name__ == "__main__":
    try:
        GameApp().run()
    finally:
        pygame.quit()
        sys.exit()
