import pygame
from pathlib import Path

class Vehiculo:
    def __init__(self, posicion: tuple, image_path: Path, escala: tuple, sen: str):
        self.sen = sen  # 'h' (horizontal) o 'v' (vertical)
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, escala)
        self.forma = self.image.get_rect(center=posicion)

class Pj(Vehiculo):
    def __init__(self, posicion: tuple, image_path: Path, escala: tuple, sen: str, victoria_rect: pygame.Rect):
        super().__init__(posicion, image_path, escala, sen)
        self.victoria = victoria_rect