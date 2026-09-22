"""Gestor de música de fondo basada en assets externos.

La música se carga desde archivos que el equipo puede sustituir sin tocar
la lógica del juego. Se aceptan tanto MP3 como OGG: el gestor busca primero
la versión MP3 y, si no existe, utiliza la versión OGG.

La clase mantiene la abstracción del sistema de audio: las pantallas y la
clase Juego solo indican el estado actual; este gestor decide qué archivo
reproducir, cómo aplicar el volumen y cómo mantenerlo en bucle.
"""

import os

try:
    import pygame
except ImportError:  # pragma: no cover - pygame es dependencia obligatoria
    pygame = None

from .configuracion import (
    RUTA_MUSICA_MENU,
    RUTA_MUSICA_PARTIDA,
    RUTA_MUSICA_RESULTADO,
)

MOOD_POR_ESTADO = {
    "menu": "menu",
    "opciones": "menu",
    "creditos": "menu",
    "personajes": "partida",
    "pregunta": "partida",
    "resultado": "resultado",
}

RUTA_PISTA_POR_MOOD = {
    "menu": RUTA_MUSICA_MENU,
    "partida": RUTA_MUSICA_PARTIDA,
    "resultado": RUTA_MUSICA_RESULTADO,
}

# Extensiones soportadas por el gestor. MP3 tiene prioridad para que los
# archivos que ya tenga el equipo funcionen sin necesidad de conversión.
EXTENSIONES_MUSICA = (".mp3", ".ogg")

VOLUMEN_BASE_MUSICA = 0.80


class GestorMusica:
    """Controla carga, reproducción en bucle y volumen de la música."""

    def __init__(self, opciones):
        self._opciones = opciones
        self._disponible = False
        self._animo_actual = None
        self._ruta_actual = None
        self._inicializar()

    def _inicializar(self):
        if pygame is None:
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2)
            self._disponible = True
        except pygame.error:
            self._disponible = False

    @staticmethod
    def _buscar_archivo(ruta_base):
        """Devuelve la primera variante existente de una pista.

        ``ruta_base`` no contiene extensión. Se busca primero MP3 y luego
        OGG. Esto permite que el equipo use directamente cualquiera de los
        dos formatos sin modificar el código.
        """
        for extension in EXTENSIONES_MUSICA:
            ruta = ruta_base + extension
            if os.path.isfile(ruta):
                return ruta
        return None

    def _volumen_efectivo(self):
        if not self._opciones.musica_activa:
            return 0.0
        return VOLUMEN_BASE_MUSICA * self._opciones.volumen_musica

    def reproducir_para_estado(self, nombre_estado):
        """Selecciona el asset correspondiente al estado y lo deja en bucle.

        Si no existe ni el MP3 ni el OGG de una pista, la aplicación continúa
        normalmente; simplemente se conserva la reproducción anterior o el
        silencio.
        """
        if not self._disponible:
            return

        animo = MOOD_POR_ESTADO.get(nombre_estado, "menu")
        ruta_base = RUTA_PISTA_POR_MOOD.get(animo)
        if ruta_base is None:
            return

        ruta = self._buscar_archivo(ruta_base)
        if ruta is None:
            return

        if (
            animo == self._animo_actual
            and ruta == self._ruta_actual
            and pygame.mixer.music.get_busy()
        ):
            return

        try:
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.set_volume(self._volumen_efectivo())
            pygame.mixer.music.play(loops=-1, fade_ms=250)
            self._animo_actual = animo
            self._ruta_actual = ruta
        except (pygame.error, FileNotFoundError):
            # Un asset de música defectuoso no rompe la partida.
            self._animo_actual = None
            self._ruta_actual = None

    def actualizar(self):
        """Aplica inmediatamente volumen y estado de activación."""
        if not self._disponible:
            return
        try:
            pygame.mixer.music.set_volume(self._volumen_efectivo())
        except pygame.error:
            pass

    def detener(self):
        if not self._disponible:
            return
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except pygame.error:
            pass


__all__ = ["GestorMusica"]
