"""Clase base abstracta para todas las pantallas del juego."""

from abc import ABC, abstractmethod


class Pantalla(ABC):
    """Contrato común de todas las pantallas (polimorfismo)."""

    def __init__(self, juego):
        self._juego = juego

    def al_entrar(self):
        """Se ejecuta al activar la pantalla."""
        pass

    def al_cerrar(self):
        """Permite liberar recursos exclusivos de una pantalla."""
        pass

    @abstractmethod
    def procesar_evento(self, evento):
        raise NotImplementedError

    @abstractmethod
    def actualizar(self):
        raise NotImplementedError

    @abstractmethod
    def dibujar(self, superficie):
        raise NotImplementedError
