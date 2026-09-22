"""Gestor de efectos de sonido cargados desde assets externos.

Los efectos dejan de generarse proceduralmente. Cada sonido se carga
como un recurso independiente para que el equipo pueda sustituirlo sin
modificar la lógica del juego. El gestor encapsula la carga, volumen,
estado de activación y reproducción.
"""

import os

try:
    import pygame
except ImportError:  # pragma: no cover - pygame es dependencia obligatoria
    pygame = None

from .configuracion import (
    RUTA_EFECTO_CLIC,
    RUTA_EFECTO_CORRECTO,
    RUTA_EFECTO_INCORRECTO,
)


class GestorAudio:
    """Administra efectos de sonido reutilizables mediante composición."""

    _RUTAS = {
        "clic": RUTA_EFECTO_CLIC,
        "correcto": RUTA_EFECTO_CORRECTO,
        "incorrecto": RUTA_EFECTO_INCORRECTO,
    }

    def __init__(self, opciones):
        self._opciones = opciones
        self._disponible = False
        self._sonidos = {}
        self._cargar_assets()

    def _cargar_assets(self):
        if pygame is None:
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2)

            for nombre, ruta in self._RUTAS.items():
                if not os.path.isfile(ruta):
                    continue
                try:
                    self._sonidos[nombre] = pygame.mixer.Sound(ruta)
                except pygame.error:
                    # Un archivo incorrecto no debe impedir que el juego abra.
                    continue

            self._disponible = bool(self._sonidos)
        except pygame.error:
            self._disponible = False

    def _reproducir(self, nombre):
        if not self._disponible or not self._opciones.efectos_activos:
            return

        sonido = self._sonidos.get(nombre)
        if sonido is None:
            return

        sonido.set_volume(self._opciones.volumen_efectos)
        sonido.play()

    def reproducir_clic(self):
        self._reproducir("clic")

    def reproducir_correcto(self):
        self._reproducir("correcto")

    def reproducir_incorrecto(self):
        self._reproducir("incorrecto")


__all__ = ["GestorAudio"]
