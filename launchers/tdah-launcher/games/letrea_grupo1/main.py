import sys
from pathlib import Path

RUTA_RAIZ = Path(__file__).resolve().parent
if str(RUTA_RAIZ) not in sys.path:
    sys.path.insert(0, str(RUTA_RAIZ))

from src.motor import JuegoLetrea
from src.modelos import Categoria
from src.audio import GestorAudio
from src.recursos import GestorRecursos
from src.componentes import CarruselBase, AnimadorMaestraD
from src.pantallas import (
    Pantalla,
    PantallaInicio,
    PantallaCategorias,
    PantallaLetras,
    PantallaEscritura,
)

def principal() -> None:
    juego = JuegoLetrea()
    juego.ejecutar()

if __name__ == "__main__":
    principal()