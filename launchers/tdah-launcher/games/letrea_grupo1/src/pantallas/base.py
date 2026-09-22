"""Clase Base Abstracta para todas las pantallas del juego Letrea."""

from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
import pygame

if TYPE_CHECKING:
    from src.motor import JuegoLetrea

class Pantalla(ABC):
    """Interfaz base para el patrón State/Screen del juego."""
    def __init__(self, juego: JuegoLetrea):
        self.juego = juego

    @abstractmethod
    def manejar_evento(self, evento: pygame.event.Event) -> None:
        """Procesa entradas de teclado, ratón o sistema."""
        pass

    @abstractmethod
    def actualizar(self) -> None:
        """Actualiza la lógica interna, animaciones y estados de la pantalla."""
        pass

    @abstractmethod
    def dibujar(self, superficie: pygame.Surface) -> None:
        """Dibuja todos los componentes gráficos de la pantalla sobre la superficie."""
        pass
