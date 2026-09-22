"""Modelo del jugador: guarda su puntuación y progreso durante la partida."""

PUNTOS_POR_RESPUESTA_CORRECTA = 10


class Jugador:
    """Almacena la información del jugador y su puntuación.

    La puntuación solo puede modificarse mediante los métodos
    ``sumar_puntos`` y ``registrar_fallo`` (encapsulamiento): ningún otro
    objeto del juego escribe directamente sobre los atributos internos.
    """

    def __init__(self, nombre="Jugador"):
        self._nombre = nombre
        self._puntuacion = 0
        self._respuestas_correctas = 0
        self._respuestas_totales = 0

    @property
    def nombre(self):
        return self._nombre

    @property
    def puntuacion(self):
        return self._puntuacion

    @property
    def respuestas_correctas(self):
        return self._respuestas_correctas

    @property
    def respuestas_totales(self):
        return self._respuestas_totales

    def sumar_puntos(self, puntos=PUNTOS_POR_RESPUESTA_CORRECTA):
        """Registra una respuesta correcta y suma puntos. No se restan
        puntos por respuestas incorrectas: el juego evita transmitir que
        equivocarse es un fracaso."""
        self._puntuacion += puntos
        self._respuestas_correctas += 1
        self._respuestas_totales += 1

    def registrar_fallo(self):
        """Registra una respuesta incorrecta (0 puntos, sin penalización)."""
        self._respuestas_totales += 1

    def reiniciar(self):
        """Vuelve a dejar al jugador en su estado inicial para una nueva partida."""
        self._puntuacion = 0
        self._respuestas_correctas = 0
        self._respuestas_totales = 0
