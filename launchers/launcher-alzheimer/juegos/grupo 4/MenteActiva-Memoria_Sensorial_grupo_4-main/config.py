"""
Memoria Sensorial - Configuración Global
Constantes, colores, dificultades y temas del juego.
"""
from dataclasses import dataclass
from enum import Enum
import os

# ─── Rutas ────────────────────────────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(_BASE_DIR, "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")

# ─── Ventana ──────────────────────────────────────────────────────────────────
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60
TITLE = "Memoria Sensorial"

# ─── Paleta de Colores ───────────────────────────────────────────────────────
class Colors:
    """Paleta accesible diseñada para calma y alto contraste."""
    LAVENDER     = (184, 169, 201)
    CORAL        = (232, 144, 126)
    SAGE_GREEN   = (168, 213, 186)
    GOLD         = (242, 201, 76)
    SKY_BLUE     = (135, 206, 235)
    WARM_ROSE    = (212, 160, 160)
    TEAL         = (126, 200, 200)
    CREAM        = (255, 248, 231)

    WHITE        = (255, 255, 255)
    SOFT_BLACK   = (50, 50, 58)
    DARK_TEXT     = (60, 60, 70)
    LIGHT_TEXT    = (140, 140, 150)
    CARD_BACK    = (175, 168, 195)
    CARD_SHADOW  = (145, 138, 165)
    SUCCESS      = (120, 200, 140)
    OVERLAY_DARK = (30, 30, 40)

# ─── Fuentes ──────────────────────────────────────────────────────────────────
FONT_NAME = "segoeui"  # Fallback: pygame buscará arial, helvetica
FONT_FALLBACKS = ["segoeui", "arial", "helvetica", "sans-serif"]

FONT_SIZES = {
    "title":    64,
    "subtitle": 40,
    "heading":  32,
    "body":     24,
    "button":   28,
    "small":    18,
    "tiny":     14,
}

# ─── Tarjetas ─────────────────────────────────────────────────────────────────
CARD_MARGIN = 14
CARD_BORDER_RADIUS = 16
CARD_FLIP_FRAMES = 12          # Frames para la animación de volteo
CARD_MIN_SIZE = 100
CARD_MAX_SIZE = 160

# ─── Animación ────────────────────────────────────────────────────────────────
TRANSITION_SPEED = 0.06
CELEBRATION_PARTICLES = 40
GLOW_PULSE_SPEED = 3.0         # Velocidad del pulso de brillo
MESSAGE_DISPLAY_TIME = 1.5     # Segundos que se muestra un mensaje positivo

# ─── Colores de Pista (borde de color por pareja) ────────────────────────────
HINT_BORDER_COLORS = [
    (232, 144, 126),   # Coral
    (126, 200, 200),   # Teal
    (242, 201, 76),    # Dorado
    (168, 213, 186),   # Verde salvia
    (212, 160, 160),   # Rosa
    (135, 206, 235),   # Azul cielo
    (184, 169, 201),   # Lavanda
    (200, 175, 130),   # Arena
]

# ─── Niveles de Dificultad ────────────────────────────────────────────────────
class DifficultyLevel(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

@dataclass(frozen=True)
class DifficultyConfig:
    """Configuración inmutable de un nivel de dificultad."""
    name: str
    rows: int
    cols: int
    num_pairs: int
    preview_time: float
    card_view_time: float
    description: str
    color: tuple

DIFFICULTY_CONFIGS = {
    DifficultyLevel.EASY: DifficultyConfig(
        name="Fácil", rows=2, cols=3, num_pairs=3,
        preview_time=5.0, card_view_time=2.5,
        description="3 parejas · Tablero 2x3",
        color=(80, 210, 120),
    ),
    DifficultyLevel.MEDIUM: DifficultyConfig(
        name="Medio", rows=3, cols=4, num_pairs=6,
        preview_time=4.0, card_view_time=1.5,
        description="6 parejas · Tablero 3x4",
        color=(242, 201, 76),
    ),
    DifficultyLevel.HARD: DifficultyConfig(
        name="Desafiante", rows=4, cols=4, num_pairs=8,
        preview_time=3.0, card_view_time=0.8,
        description="8 parejas · Tablero 4x4",
        color=(240, 120, 120),
    ),
}

# ─── Sistema de Pistas Adaptativo ────────────────────────────────────────────
# Umbral unificado: las pistas se activan tras 2 fallos consecutivos
# en pares ya vistos, sin importar la dificultad.
HINT_THRESHOLD = 2

HINT_GLOW_SPEED = 2.0            # Velocidad del pulso del borde dorado
HINT_REVEAL_TIME = 0.8           # Segundos de revelación temporal (Pista N3)
HINT_AUDIO_VOLUME = 0.3          # Volumen de la pista auditiva

# ─── Música de Fondo ─────────────────────────────────────────────────────────
MUSIC_VOLUME = 0.3               # Volumen de la música de fondo
MUSIC_FADE_MS = 1000             # Duración del fade al cambiar música (ms)

# ─── Tiempos del Juego ────────────────────────────────────────────────────────
FAIL_DISPLAY_TIME = 1.8          # Cartas fallidas permanecen visibles
MATCH_DISPLAY_TIME = 0.8         # Breve pausa tras acierto
PREVIEW_FADE_SPEED = 0.04        # Velocidad de volteo en previsualización

# ─── Temas de Cartas ─────────────────────────────────────────────────────────
THEMES = {
    "naturaleza": {
        "name": "Naturaleza",
        "icons": ["sol", "luna", "flor", "arbol", "nube", "estrella", "montana", "gota"],
        "color": (80, 210, 120),
    },
    "alimentos": {
        "name": "Alimentos",
        "icons": ["manzana", "pan", "cafe", "pastel", "uva", "naranja", "helado", "galleta"],
        "color": (240, 120, 120),
    },
    "animales": {
        "name": "Animales",
        "icons": ["gato", "perro", "pajaro", "mariposa", "pez", "conejo", "tortuga", "abeja"],
        "color": (242, 201, 76),
    },
    "hogar": {
        "name": "Hogar",
        "icons": ["casa", "silla", "taza", "reloj", "libro", "llave", "lampara", "corazon"],
        "color": (135, 206, 235),
    },
}

# ─── Mensajes Positivos ──────────────────────────────────────────────────────
POSITIVE_MESSAGES = [
    "¡Muy bien!", "¡Excelente!", "¡Fantástico!", "¡Increíble!",
    "¡Sigue así!", "¡Maravilloso!", "¡Genial!", "¡Bravo!",
]

ENCOURAGEMENT_MESSAGES = [
    "¡Sigue intentando!", "¡Casi lo logras!", "¡Tú puedes!",
    "¡No te rindas!", "¡Estás muy cerca!", "¡Vamos, tú puedes!",
]

# ─── Nombres de Pantallas ────────────────────────────────────────────────────
class ScreenName(Enum):
    MENU = "menu"
    GAME = "game"
    VICTORY = "victory"
    QUIT = "quit"
