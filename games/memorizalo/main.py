"""
Punto de entrada de FLIP IT.

El launcher 'enfocate' abre cada juego como un proceso independiente
(`python main.py` dentro de la carpeta del juego), asi que este archivo
tiene que poder correr solo. El sys.path se ajusta a mano para que las
importaciones funcionen aunque el launcher lo invoque desde otra carpeta
de trabajo.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.juego import MiJuego


if __name__ == "__main__":
    juego = MiJuego()
    juego.run_preview()
