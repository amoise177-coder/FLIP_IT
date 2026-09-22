"""Abstracción del fondo estático del menú principal.

La clase encapsula la carga del asset, el ajuste proporcional a la
resolución de la ventana y la entrega del resultado como Surface de
Pygame. No contiene lógica del juego.
"""

import os

import pygame


class FondoImagen:
    """Carga una imagen de fondo y la adapta al tamaño de la ventana."""

    def __init__(self, ruta, tamano_destino):
        self._ruta = ruta
        self._tamano_destino = tuple(tamano_destino)
        self._superficie = None
        self._disponible = False
        self._cargar()

    @property
    def disponible(self):
        return self._disponible

    def _cargar(self):
        if not os.path.isfile(self._ruta):
            return

        try:
            imagen = pygame.image.load(self._ruta).convert()
            self._superficie = self._ajustar_a_pantalla(imagen)
            self._disponible = True
        except (pygame.error, OSError, ValueError):
            self._superficie = None
            self._disponible = False

    def _ajustar_a_pantalla(self, imagen):
        """Escala sin deformar y recorta excedentes para cubrir la ventana."""
        ancho_destino, alto_destino = self._tamano_destino
        ancho_origen, alto_origen = imagen.get_size()

        if ancho_origen <= 0 or alto_origen <= 0:
            raise ValueError("La imagen de fondo tiene dimensiones inválidas")

        escala = max(
            ancho_destino / ancho_origen,
            alto_destino / alto_origen,
        )
        nuevo_tamano = (
            max(1, int(round(ancho_origen * escala))),
            max(1, int(round(alto_origen * escala))),
        )

        escalada = pygame.transform.smoothscale(imagen, nuevo_tamano)

        if nuevo_tamano == self._tamano_destino:
            return escalada

        izquierda = max(0, (nuevo_tamano[0] - ancho_destino) // 2)
        arriba = max(0, (nuevo_tamano[1] - alto_destino) // 2)
        rect_recorte = pygame.Rect(
            izquierda,
            arriba,
            ancho_destino,
            alto_destino,
        )
        return escalada.subsurface(rect_recorte).copy()

    def actualizar(self):
        """El fondo es estático: no necesita actualizarse cada fotograma."""
        pass

    def dibujar(self, superficie):
        if self._superficie is not None:
            superficie.blit(self._superficie, (0, 0))

    def al_cerrar(self):
        self._superficie = None
        self._disponible = False


__all__ = ["FondoImagen"]
