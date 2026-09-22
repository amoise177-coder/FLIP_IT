from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

@dataclass(frozen=True)
class Constantes():

    # Rutas del sistema 
    BASE_DIR: Path = Path(__file__).resolve().parent
    ASSETS_DIR: Path = BASE_DIR / "assets"
    IMAGES_DIR: Path = ASSETS_DIR / "images"
    SOUNDS_DIR: Path = ASSETS_DIR / "sounds"
    FONTS_DIR: Path = ASSETS_DIR / "fonts"
    BACKGROUNDS_DIR: Path = ASSETS_DIR / "backgrounds"

    # Ventana y rendimiento
    TITULO_JUEGO: str = "Animal Genius"
    ANCHO_PANTALLA: int = 1280
    ALTO_PANTALLA: int = 720
    FPS: int = 60

    # Colores
    COLOR_FONDO: tuple = (245, 247, 248)
    COLOR_BOTON: tuple = (76, 175, 80)
    COLOR_BOTON_HOVER: tuple = (102, 187, 106)
    COLOR_TEXTO: tuple = (255, 255, 255)
    COLOR_TEXTO_DARK: tuple = (44, 62, 80)
    COLOR_BLOQUE_RASCA: tuple = (200, 200, 200)  

    # Posiciones y dimensiones
    ANCHO_IMAGEN: int = 200
    ALTO_IMAGEN: int = 200
    POS_IMAGEN_Y: int = 150

    ANCHO_BOTON: int = 300
    ALTO_BOTON: int = 80
    POS_Y_BOTONES: int = 520
    POS_X_BOTON_IZQ: int = 280
    POS_X_BOTON_DER: int = 700
    TAMANO_BLOQUE_RASCA: int = 25

    COLORES_BIOMAS: ClassVar[dict] = {
        "pradera": {"arriba": (255, 160, 50), "abajo": (180, 80, 15)},
        "bosque":  {"arriba": (240, 65, 65),  "abajo": (150, 20, 20)},
        "selva":   {"arriba": (110, 220, 90), "abajo": (35, 130, 45)},
        "artico":  {"arriba": (185, 125, 245),"abajo": (105, 45, 165)},
        "oceano":  {"arriba": (85, 165, 255), "abajo": (20, 65, 175)},
    }

const = Constantes()
