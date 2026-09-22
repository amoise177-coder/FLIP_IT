from pathlib import Path
from typing import Tuple, List, Dict, Any

# --- Rutas Dinámicas con pathlib ---
_DIR_ACTUAL: Path = Path(__file__).resolve().parent
_DIR_RAIZ: Path = _DIR_ACTUAL.parent

BASE_DIR: Path = _DIR_RAIZ
RUTA_RAIZ: Path = BASE_DIR
RUTA_ASSETS: Path = BASE_DIR / "assets"
RUTA_IMAGENES: Path = RUTA_ASSETS / "images"
RUTA_SPRITES: Path = RUTA_ASSETS / "sprites"
RUTA_FONDO: Path = RUTA_SPRITES / "fondo.png"
RUTA_SONIDOS: Path = RUTA_ASSETS / "sounds"
RUTA_SFX: Path = RUTA_SONIDOS
RUTA_MUSICA: Path = RUTA_ASSETS / "music"
RUTA_DATA: Path = RUTA_ASSETS / "data"

GAMEMETA_FILE: Path = BASE_DIR / "gamemeta.json"
CATEGORIAS_FILE: Path = RUTA_DATA / "categorias.json"
DICTIONARY_FILE: Path = CATEGORIAS_FILE
PUNTUACIONES_FILE: Path = RUTA_DATA / "puntuaciones.json"
SCORES_FILE: Path = PUNTUACIONES_FILE
SOUNDS_DIR: Path = RUTA_SONIDOS


class Config:
    """Clase contenedora que encapsula todos los parámetros de configuración."""
    # Rutas dinámicas
    BASE_DIR, RUTA_RAIZ, RUTA_ASSETS = BASE_DIR, RUTA_RAIZ, RUTA_ASSETS
    RUTA_IMAGENES, RUTA_SPRITES, RUTA_FONDO = RUTA_IMAGENES, RUTA_SPRITES, RUTA_FONDO
    RUTA_SONIDOS, RUTA_SFX, RUTA_MUSICA, RUTA_DATA = RUTA_SONIDOS, RUTA_SFX, RUTA_MUSICA, RUTA_DATA
    GAMEMETA_FILE, CATEGORIAS_FILE, DICTIONARY_FILE = GAMEMETA_FILE, CATEGORIAS_FILE, DICTIONARY_FILE
    PUNTUACIONES_FILE, SCORES_FILE, SOUNDS_DIR = PUNTUACIONES_FILE, SCORES_FILE, SOUNDS_DIR

    # Audio y rendimiento
    SOUND_ENABLED: bool = True
    SOUND_VOLUME: float = 0.7
    SCREEN_WIDTH: int = 1280
    SCREEN_HEIGHT: int = 720
    FPS: int = 60
    WINDOW_TITLE: str = "Letra a Letra - Scrabble Adaptado para Estimulación Cognitiva"

    # Paleta de Colores Accesibles (Alto Contraste)
    COLOR_BG: Tuple[int, int, int] = (248, 246, 240)
    COLOR_PANEL: Tuple[int, int, int] = (235, 229, 218)
    COLOR_GRID_BG: Tuple[int, int, int] = (220, 212, 198)
    COLOR_CELL: Tuple[int, int, int] = (255, 252, 245)
    COLOR_CELL_BORDER: Tuple[int, int, int] = (190, 180, 160)

    # Fichas de madera
    COLOR_TILE_BG: Tuple[int, int, int] = (245, 215, 150)
    COLOR_TILE_SELECT: Tuple[int, int, int] = (255, 180, 70)
    COLOR_TILE_TEXT: Tuple[int, int, int] = (40, 30, 20)
    COLOR_TILE_BORDER: Tuple[int, int, int] = (160, 110, 50)

    # Botones y elementos dinámicos
    COLOR_BTN_PRIMARY: Tuple[int, int, int] = (76, 140, 95)
    COLOR_BTN_HINT: Tuple[int, int, int] = (55, 120, 185)
    COLOR_BTN_CLEAR: Tuple[int, int, int] = (200, 90, 75)
    COLOR_TEXT_DARK: Tuple[int, int, int] = (45, 45, 50)
    COLOR_TEXT_LIGHT: Tuple[int, int, int] = (255, 255, 255)
    COLOR_SUCCESS: Tuple[int, int, int] = (46, 125, 50)
    COLOR_INFO: Tuple[int, int, int] = (25, 118, 210)
    COLOR_HINT_BOX: Tuple[int, int, int] = (255, 250, 220)
    COLOR_PANEL_SOFT: Tuple[int, int, int] = (238, 232, 217)
    COLOR_MUTED: Tuple[int, int, int] = (111, 105, 96)
    COLOR_GOLD: Tuple[int, int, int] = (224, 169, 69)
    COLOR_LINE: Tuple[int, int, int] = (215, 203, 181)

    # Tablero 7x7 y Atril
    BOARD_ROWS: int = 7
    BOARD_COLS: int = 7
    CELL_SIZE: int = 60
    BOARD_X: int = 391
    BOARD_Y: int = 124

    RACK_CAPACITY: int = 7
    RACK_X: int = 379
    RACK_Y: int = 578
    TILE_SIZE: int = 52

    # Categorías temáticas oficiales
    CATEGORIES: List[Dict[str, Any]] = [
        {"id": "naturaleza", "title": "Naturaleza", "subtitle": "Naturaleza y entorno", "color": (76, 140, 95)},
        {"id": "objetos", "title": "Objetos", "subtitle": "Cosas de uso diario", "color": (180, 110, 50)},
        {"id": "frutas_alimentos", "title": "Frutas y Alimentos", "subtitle": "Comidas y bebidas conocidas", "color": (230, 150, 70)},
        {"id": "familia_hogar", "title": "Familia y Hogar", "subtitle": "Personas y lugares cercanos", "color": (140, 90, 160)},
        {"id": "animales", "title": "Animales", "subtitle": "Mascotas y animales", "color": (200, 90, 75)},
        {"id": "cuerpo_humano", "title": "Cuerpo Humano", "subtitle": "Partes del cuerpo", "color": (55, 126, 194)},
        {"id": "todas", "title": "Modo Completo", "subtitle": "Todas las palabras", "color": (90, 70, 150)},
    ]

    # Plantilla oficial requerida para gamemeta.json
    DEFAULT_GAMEMETA: Dict[str, Any] = {
        "nombre_juego": "Letra a Letra",
        "autores": ["Rita Salazar", "Gibran Sánchez"],
        "version": "1.0.0",
        "descripcion": "Juego de palabras adaptado para la estimulación cognitiva en personas con Alzheimer."
    }


# Mapa indexado de categorías para consultas O(1) rápidas
CATEGORY_MAP: Dict[str, Dict[str, Any]] = {c["id"]: c for c in Config.CATEGORIES}

# Exportación dinámica de alias a nivel de módulo para compatibilidad total con importaciones existentes
for _k, _v in list(Config.__dict__.items()):
    if _k.isupper():
        globals()[_k] = _v
