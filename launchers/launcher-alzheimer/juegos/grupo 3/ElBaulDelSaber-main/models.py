"""Modelo de dominio: datos y reglas de un refrán."""
from dataclasses import dataclass
import unicodedata


def normalize(text: str) -> str:
    plain = "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")
    return " ".join("".join("" if not (c.isalnum() or c.isspace()) else c for c in plain).split())


@dataclass(frozen=True)
class Refran:
    """ENCAPSULAMIENTO: la regla de validación pertenece al propio refrán."""
    inicio: str
    respuesta: str
    significado: str
    preguntas: tuple[str, str]
    tema: str

    @property
    def letra_inicial(self) -> str:
        return self.respuesta[0].upper()

    def es_respuesta_correcta(self, intento: str) -> bool:
        return bool(intento.strip()) and normalize(intento) == normalize(self.respuesta)
