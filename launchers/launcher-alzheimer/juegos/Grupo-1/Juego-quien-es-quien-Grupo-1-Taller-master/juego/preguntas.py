"""Jerarquía de preguntas del juego.

``Pregunta`` es la clase abstracta que define lo que TODAS las preguntas
tienen en común (abstracción): un enunciado, un conjunto de opciones y una
respuesta correcta, además del comportamiento para comprobarla.

Cada subclase (``PreguntaIdentificacion``, ``PreguntaCaracteristica``,
``PreguntaRelacion`` y ``PreguntaVisual``) hereda ese comportamiento común
y lo especializa (herencia + polimorfismo): el juego puede guardar
preguntas de distintos tipos en una misma lista y llamar siempre a los
mismos métodos (``comprobar_respuesta``, ``obtener_tipo``,
``usa_opciones_visuales``) sin preocuparse por la clase concreta de cada
una.
"""

from abc import ABC, abstractmethod


class Pregunta(ABC):
    """Clase base abstracta para cualquier tipo de pregunta del juego."""

    def __init__(self, enunciado, opciones, respuesta_correcta):
        self._enunciado = enunciado
        self._opciones = list(opciones)
        self._respuesta_correcta = respuesta_correcta

    @property
    def enunciado(self):
        return self._enunciado

    @property
    def opciones(self):
        return list(self._opciones)

    @property
    def respuesta_correcta(self):
        return self._respuesta_correcta

    def comprobar_respuesta(self, opcion_seleccionada):
        """Devuelve True si la opción elegida es la respuesta correcta.

        Es el comportamiento por defecto (igual para todas las preguntas);
        las subclases pueden extenderlo si necesitan una regla especial.
        """
        return opcion_seleccionada == self._respuesta_correcta

    def imagen_personaje(self):
        """Nombre del personaje cuya imagen debe mostrarse junto a la
        pregunta, o None si esta pregunta no muestra ninguna imagen
        principal. Cada subclase decide si aplica."""
        return None

    def usa_opciones_visuales(self):
        """Indica si las opciones deben mostrarse como imágenes de
        personajes (True) o como botones de texto (False). Por defecto,
        texto."""
        return False

    @abstractmethod
    def obtener_tipo(self):
        """Nombre legible del tipo de pregunta (para depuración/créditos)."""
        raise NotImplementedError


class PreguntaIdentificacion(Pregunta):
    """"¿Cómo se llama esta persona?" — se muestra una imagen y el
    jugador debe reconocer el nombre."""

    def __init__(self, enunciado, opciones, respuesta_correcta, personaje_imagen):
        super().__init__(enunciado, opciones, respuesta_correcta)
        self._personaje_imagen = personaje_imagen

    def imagen_personaje(self):
        return self._personaje_imagen

    def obtener_tipo(self):
        return "Identificación por nombre"


class PreguntaCaracteristica(Pregunta):
    """"¿A quién le gusta cocinar?" — el jugador asocia una característica
    con un personaje."""

    def obtener_tipo(self):
        return "Identificación por característica"


class PreguntaRelacion(Pregunta):
    """Preguntas sobre relaciones familiares, en cualquiera de sus dos
    direcciones ("¿Quién es el hijo de Ana?" o "¿De quién es hijo
    Carlos?")."""

    def obtener_tipo(self):
        return "Relación familiar"


class PreguntaVisual(Pregunta):
    """El jugador debe seleccionar la imagen correcta entre varios
    personajes, en lugar de elegir un nombre en texto."""

    def usa_opciones_visuales(self):
        return True

    def obtener_tipo(self):
        return "Reconocimiento visual"


_FABRICA_POR_TIPO = {
    "identificacion": lambda d: PreguntaIdentificacion(
        d["enunciado"], d["opciones"], d["respuesta"], d.get("personaje_imagen")
    ),
    "caracteristica": lambda d: PreguntaCaracteristica(
        d["enunciado"], d["opciones"], d["respuesta"]
    ),
    "relacion": lambda d: PreguntaRelacion(
        d["enunciado"], d["opciones"], d["respuesta"]
    ),
    "visual": lambda d: PreguntaVisual(
        d["enunciado"], d["opciones"], d["respuesta"]
    ),
}


def crear_pregunta_desde_datos(datos):
    """Fábrica: construye el objeto ``Pregunta`` concreto que corresponde
    a un diccionario leído del JSON, según su campo ``tipo``."""
    tipo = datos["tipo"]
    constructor = _FABRICA_POR_TIPO.get(tipo)
    if constructor is None:
        raise ValueError(f"Tipo de pregunta desconocido: {tipo!r}")
    return constructor(datos)


def cargar_preguntas(lista_datos):
    """Convierte la lista de diccionarios del JSON en una lista de
    objetos ``Pregunta`` (de distintas subclases)."""
    return [crear_pregunta_desde_datos(d) for d in lista_datos]
