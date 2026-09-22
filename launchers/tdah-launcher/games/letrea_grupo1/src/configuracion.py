import sys
from pathlib import Path

# Dimensiones de ventana y tasa de refresco
ANCHO_VENTANA = 1280
ALTO_VENTANA = 720
FPS = 60

# Paleta de Colores
COLOR_FONDO_FALLBACK = (230, 242, 255)
COLOR_TEXTO = (50, 50, 50)
COLOR_BOTON = (255, 255, 255)
COLOR_BOTON_HOVER = (220, 240, 255)
COLOR_AZUL_BOBEO = (107, 193, 190)
VERDE_PRINCIPAL = (0, 140, 57)
COLOR_FEEDBACK_CERCA = (230, 180, 50)
COLOR_FEEDBACK_ERROR = (220, 80, 80)

# Medidas de tarjetas e iconos
TAMANO_BOTON_LETRA = 105
ANCHO_OVER = 192
ALTO_OVER = 190
MARGEN_X = 23
MARGEN_Y = 24

# Diccionario de títulos para la pantalla de escritura
TEXTOS_LETRAS_TITULO = {
    "A": "Aa", "B": "Bb", "C": "Cc", "D": "Dd", "E": "Ee", "F": "Ff", "G": "Gg", "H": "Hh",
    "I": "Ii", "J": "Jj", "K": "K",   "L": "Ll", "M": "Mm", "N": "Nn", "Ñ": "Ññ", "O": "O",
    "P": "P",   "Q": "Qq", "R": "Rr", "S": "S",   "T": "Tt", "U": "U",   "V": "V",   "W": "W",
    "X": "X",   "Y": "Yy", "Z": "Z"
}

def obtener_ruta_base() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent
