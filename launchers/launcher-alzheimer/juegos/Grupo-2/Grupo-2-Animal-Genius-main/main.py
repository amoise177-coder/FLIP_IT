import os
import sys

_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_dir)
if _dir not in sys.path:
    sys.path.insert(0, _dir)

import pygame
from engine import MotorJuego


def main():

    pygame.init()
    pygame.mixer.init()

    motor = MotorJuego()
    motor.ejecutar()

    pygame.mixer.quit()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

    
