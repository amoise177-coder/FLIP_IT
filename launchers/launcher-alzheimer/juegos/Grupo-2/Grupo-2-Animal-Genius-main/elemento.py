from abc import ABC, abstractmethod
import pygame


class Elemento(ABC):
    
    def __init__(self, pos_x: int = 0, pos_y: int = 0) -> None:
        self._pos_x: int = pos_x
        self._pos_y: int = pos_y

    @property
    def pos_x(self) -> int:
        return self._pos_x

    @pos_x.setter
    def pos_x(self, valor: int) -> None:
        self._pos_x = valor

    @property
    def pos_y(self) -> int:
        return self._pos_y

    @pos_y.setter
    def pos_y(self, valor: int) -> None:
        self._pos_y = valor

    @abstractmethod
    def renderizar(self, superficie: pygame.Surface) -> None:
        pass

