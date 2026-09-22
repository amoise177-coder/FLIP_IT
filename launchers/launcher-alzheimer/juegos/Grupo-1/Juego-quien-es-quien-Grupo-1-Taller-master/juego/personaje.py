"""Modelo de datos que representa a un integrante de la familia del juego."""


class Personaje:
    """Representa a un personaje de la familia ficticia.

    Encapsula sus datos básicos (nombre, rol, característica, relación
    familiar) exponiéndolos solo mediante propiedades de solo lectura,
    ya que un personaje no cambia durante la partida.
    """

    def __init__(self, nombre, rol, genero, caracteristica, color, padre=None):
        self._nombre = nombre
        self._rol = rol
        self._genero = genero  # "M" o "F", usado para redactar preguntas (hijo/hija, etc.)
        self._caracteristica = caracteristica
        self._color = tuple(color)
        self._padre = padre  # nombre del padre/madre en la familia, o None

    @property
    def nombre(self):
        return self._nombre

    @property
    def rol(self):
        return self._rol

    @property
    def genero(self):
        return self._genero

    @property
    def caracteristica(self):
        return self._caracteristica

    @property
    def color(self):
        return self._color

    @property
    def padre(self):
        return self._padre

    def descripcion_corta(self):
        """Texto breve para mostrar en las tarjetas de presentación."""
        return f"{self._rol} · {self._caracteristica}"

    @staticmethod
    def cargar_familia(lista_datos):
        """Construye un diccionario {nombre: Personaje} a partir de una lista
        de diccionarios (tal como vienen del archivo JSON)."""
        familia = {}
        for datos in lista_datos:
            personaje = Personaje(
                nombre=datos["nombre"],
                rol=datos["rol"],
                genero=datos["genero"],
                caracteristica=datos["caracteristica"],
                color=datos["color"],
                padre=datos.get("padre"),
            )
            familia[personaje.nombre] = personaje
        return familia
